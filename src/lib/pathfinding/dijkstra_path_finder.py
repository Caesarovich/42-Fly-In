import sys
from dataclasses import dataclass

from src.lib.graph import Node

from .algorithm import Path, PathfindingAlgorithm


@dataclass
class DijkstraNode:
    """
    A helper class for the DijkstraPathFinder,
    representing a node in the search space.
    """

    node: Node
    parent: DijkstraNode | None
    distance_in_turns: int
    distance_in_weight: float

    @staticmethod
    def from_node(node: Node) -> DijkstraNode:
        return DijkstraNode(node, None, int(sys.maxsize), float("inf"))

    def get_comparison_tuple(self) -> tuple[int, float]:
        return (self.distance_in_turns, self.distance_in_weight)

    def __str__(self) -> str:
        return (
            f"DijkstraNode(node={self.node.key}, "
            f"parent={self.parent.node.key if self.parent else None}, "
            f"distance_in_turns={self.distance_in_turns},"
            f"distance_in_weight={self.distance_in_weight})"
        )

    def __lt__(self, other: DijkstraNode) -> bool:
        return self.get_comparison_tuple() < other.get_comparison_tuple()


class DijkstraPathFinder(PathfindingAlgorithm):
    """
    A path-finder based on Dijkstra's algorithm.
    This algorithm simply finds the best route,
    without accounting for other drones and swarm planning.
    """

    @staticmethod
    def reconstruct_path(end_node: DijkstraNode) -> Path:
        return_path = []
        current: DijkstraNode | None = end_node
        while current is not None:
            return_path.append(current.node)
            current = current.parent
        return return_path[::-1]

    def find_path(self, start_node: Node, end_node: Node) -> Path:

        unvisited: dict[Node, DijkstraNode] = {
            node: DijkstraNode.from_node(node) for node in self.graph.nodes.values()
        }
        visited: dict[Node, DijkstraNode] = {}

        def process_node(current_node: DijkstraNode) -> None:
            for edge in current_node.node.edges:
                neighbor = edge.dst
                if neighbor not in unvisited:
                    continue
                tmp_neighbor = DijkstraNode(
                    neighbor,
                    current_node,
                    current_node.distance_in_turns + 1,
                    current_node.distance_in_weight + edge.weight,
                )
                unvisited[neighbor] = min(unvisited[neighbor], tmp_neighbor)

        def process_all_nodes() -> None:
            current_node: DijkstraNode | None = DijkstraNode(start_node, None, 0, 0)
            assert current_node is not None
            visited[current_node.node] = current_node

            def find_next_node() -> DijkstraNode | None:
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

        return DijkstraPathFinder.reconstruct_path(visited[end_node])
