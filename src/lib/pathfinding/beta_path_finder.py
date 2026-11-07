import sys
from dataclasses import dataclass
from logging import getLogger

from src.lib.graph import Edge, Node, ProxyNode

from .algorithm import Path, PathfindingAlgorithm

logger = getLogger(__name__)


@dataclass
class BetaDijkstraNode:
    """
    A different helper class for the BetaPathFinder,
    representing a node in the search space.
    It accounts for waiting times, which are crucial for the algorithm.
    """

    node: Node
    parent: BetaDijkstraNode | None
    distance_in_turns: int
    distance_in_weight: float
    waiting_time: int = 0

    @staticmethod
    def from_node(node: Node) -> BetaDijkstraNode:
        return BetaDijkstraNode(node, None, int(sys.maxsize), float("inf"), 0)

    def get_comparison_tuple(self) -> tuple[int, int, float]:
        return (self.distance_in_turns, self.waiting_time, self.distance_in_weight)

    def __str__(self) -> str:
        return (
            f"BetaDijkstraNode(node={self.node.key}, "
            f"parent={self.parent.node.key if self.parent else None}, "
            f"distance_in_turns={self.distance_in_turns},"
            f"distance_in_weight={self.distance_in_weight},"
            f"waiting_time={self.waiting_time})"
        )

    def __lt__(self, other: BetaDijkstraNode) -> bool:
        return self.get_comparison_tuple() < other.get_comparison_tuple()


class BetaPathFinder(PathfindingAlgorithm):
    @staticmethod
    def reconstruct_path(end_node: BetaDijkstraNode) -> Path:
        return_path = []
        current: BetaDijkstraNode | None = end_node
        while current is not None:
            return_path.append(current.node)
            current = current.parent
        return return_path[::-1]

    def can_wait_at_node(self, node: Node, turn: int) -> bool:
        if isinstance(node, ProxyNode):
            return False
        return node.is_available(turn)

    def find_path(self, start_node: Node, end_node: Node) -> Path:

        logger.info(f"Starting pathfinding from {start_node.key} to {end_node.key}...")

        unvisited: dict[Node, BetaDijkstraNode] = {
            node: BetaDijkstraNode.from_node(node) for node in self.graph.nodes.values()
        }
        visited: dict[Node, BetaDijkstraNode] = {}

        def can_traverse_edge_at_turn(edge: Edge, turn: int) -> bool:
            if not edge.dst.is_available(turn):
                return False
            if not edge.route.is_available(turn):
                return False
            if isinstance(edge.dst, ProxyNode) and edge.dst.proxy_for:
                target = edge.dst.proxy_for.get_dst_for_src(edge.src)
                if not target.is_available(turn + 1):
                    return False
                edge_to_target = edge.dst.get_edge_to_neighbor(target)
                if not edge_to_target:
                    raise RuntimeError(
                        f"No edge found from proxy node "
                        f"{edge.dst.key} to its target "
                        f"{target.key}"
                    )
                if not edge_to_target.route.is_available(turn + 1):
                    return False
            return True

        def process_node(current_node: BetaDijkstraNode) -> None:
            logger.debug(f"Processing {current_node.node.key}")
            for edge in current_node.node.edges:
                neighbor = edge.dst
                if neighbor not in unvisited:
                    continue

                current_turn = current_node.distance_in_turns
                wait_count = 1
                while not (can_traverse_edge_at_turn(edge, current_turn + wait_count)):
                    wait_count += 1

                current_weight = current_node.distance_in_weight + edge.weight
                current_waiting_time = current_node.waiting_time + wait_count
                tmp_neighbor = BetaDijkstraNode(
                    neighbor,
                    current_node,
                    current_turn + wait_count,
                    current_weight,
                    current_waiting_time - 1,
                )
                unvisited[neighbor] = min(unvisited[neighbor], tmp_neighbor)

        def process_all_nodes() -> None:
            current_node: BetaDijkstraNode | None = BetaDijkstraNode(
                start_node, None, 0, 0, 0
            )
            assert current_node is not None
            visited[current_node.node] = current_node

            def find_next_node() -> BetaDijkstraNode | None:
                if not unvisited:
                    return None
                key = min(unvisited, key=lambda node: unvisited[node])
                return unvisited[key]

            while current_node:
                process_node(current_node)
                visited[current_node.node] = current_node
                del unvisited[current_node.node]
                current_node = find_next_node()

        process_all_nodes()
        logger.info(f"Best path found {visited[end_node]}")

        return BetaPathFinder.reconstruct_path(visited[end_node])
