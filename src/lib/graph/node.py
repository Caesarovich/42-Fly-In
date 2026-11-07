from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .edge import Edge
    from .route import Route


@dataclass
class Node:
    """
    Represents a node in the graph, with a unique key, maximum occupancy,
    coordinates, and connections to neighboring nodes.
    """

    key: str
    maximum_occupancy: int
    x: float
    y: float
    occupencies: dict[int, set[str]] = field(default_factory=dict)
    neighbors: set[Node] = field(default_factory=set)
    edges: set[Edge] = field(default_factory=set)

    def __hash__(self) -> int:
        return hash(self.key)

    def __str__(self) -> str:
        return f"{self.key} (max occupancy: {self.maximum_occupancy})"

    def get_edges_to_neighbor(self, neighbor: Node) -> set[Edge]:
        return {edge for edge in self.edges if edge.dst == neighbor}

    def get_edge_to_neighbor(self, neighbor: Node) -> Edge | None:
        edges = self.get_edges_to_neighbor(neighbor)
        if not edges:
            return None
        return next(iter(edges))

    def reserve_for_turn(self, turn: int, drone_id: str) -> None:
        self.occupencies.setdefault(turn, set())
        if len(self.occupencies[turn]) >= self.maximum_occupancy:
            raise RuntimeError(
                f"Node {self.key} is already at maximum occupancy for turn {turn}"
            )
        self.occupencies[turn].add(drone_id)

    def can_wait_at_node(self, turn: int) -> bool:
        return self.is_available(turn)

    def is_available(self, turn: int) -> bool:
        return len(self.occupencies.get(turn, {})) < self.maximum_occupancy


@dataclass
class ProxyNode(Node):
    """
    Represents a proxy node in the graph,
    which is used to model restricted zones.
    """

    proxy_for: Route | None = field(default=None)

    def __str__(self) -> str:
        p_for = self.proxy_for.key if self.proxy_for else "None"
        return (
            f"{self.key} (proxy for: {p_for}, max occupancy: {self.maximum_occupancy})"
        )

    def __hash__(self) -> int:
        return hash(self.key)

    def can_wait_at_node(self, turn: int) -> bool:
        return False
