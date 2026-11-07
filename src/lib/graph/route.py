from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .edge import Edge
    from .node import Node


@dataclass
class Route:
    """
    Higher-level abstraction representing a route between two nodes,
    with a maximum occupancy and a set of edges that compose the route.
    """

    key: str
    max_occupancy: int
    nodes: tuple[Node, Node]
    edges: set[Edge]
    occupencies: dict[int, set[str]] = field(default_factory=dict)

    def get_dst_for_src(self, src: Node) -> Node:
        if self.nodes[0] == src:
            return self.nodes[1]
        elif self.nodes[1] == src:
            return self.nodes[0]
        else:
            raise ValueError(
                f"Source node {src.key} is not part of the route {self.key}"
            )

    def is_available(self, turn: int) -> bool:
        return len(self.occupencies.get(turn, set())) < self.max_occupancy

    def reserve_for_turn(self, turn: int, drone_id: str) -> None:
        self.occupencies.setdefault(turn, set())
        if len(self.occupencies[turn]) >= self.max_occupancy:
            raise RuntimeError(
                f"Route {self.key} is already at maximum occupancy for turn {turn}"
            )
        self.occupencies[turn].add(drone_id)

    def __str__(self) -> str:
        return (
            f"Route {self.key} (max occupancy: {self.max_occupancy}, "
            f"current occupancy: {self.occupencies})"
        )

    def __hash__(self) -> int:
        return hash(self.key)
