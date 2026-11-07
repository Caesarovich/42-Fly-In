from logging import getLogger

from src.lib.graph import Edge, Node, ProxyNode

from .algorithm import Path
from .dijkstra_path_finder import DijkstraNode, DijkstraPathFinder

logger = getLogger(__name__)


class AlphaPathFinder(DijkstraPathFinder):
    """
    Path-finder based on Dijkstra's algorithm,
    but accounting for other drones and swarm planning.
    It will count waiting times and choose paths that
    garantee the best 'turn-distance', then based on the best total weight.
    """

    def can_wait_at_node(self, node: Node, turn: int) -> bool:
        if isinstance(node, ProxyNode):
            return False
        return node.is_available(turn)

    def find_path(self, start_node: Node, end_node: Node) -> Path:

        logger.info(f"Starting pathfinding from {start_node.key} to {end_node.key}...")

        unvisited: dict[str, DijkstraNode] = {
            node.key: DijkstraNode.from_node(node) for node in self.graph.nodes.values()
        }

        visited: dict[str, DijkstraNode] = {}

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

        def process_node(current_node: DijkstraNode) -> None:
            logger.debug(f"Processing {current_node.node.key}")
            for edge in current_node.node.edges:
                neighbor = edge.dst
                if neighbor.key not in unvisited:
                    continue

                current_turn = current_node.distance_in_turns + 1
                while not (can_traverse_edge_at_turn(edge, current_turn)):
                    current_turn += 1

                current_weight = current_node.distance_in_weight + edge.weight
                tmp_neighbor = DijkstraNode(
                    neighbor,
                    current_node,
                    current_turn,
                    current_weight,
                )
                unvisited[neighbor.key] = min(unvisited[neighbor.key], tmp_neighbor)

        def process_all_nodes() -> None:
            current_node: DijkstraNode | None = DijkstraNode(start_node, None, 0, 0)
            assert current_node is not None
            visited[current_node.node.key] = current_node

            def find_next_node() -> DijkstraNode | None:
                if not unvisited:
                    return None
                key = min(unvisited, key=lambda node: unvisited[node])
                return unvisited[key]

            while current_node:
                process_node(current_node)
                visited[current_node.node.key] = current_node
                del unvisited[current_node.node.key]
                current_node = find_next_node()

        process_all_nodes()
        logger.info(f"Best path found {visited[end_node.key]}")

        return DijkstraPathFinder.reconstruct_path(visited[end_node.key])
