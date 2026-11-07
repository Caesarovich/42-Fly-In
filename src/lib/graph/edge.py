from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node
    from .route import Route


@dataclass
class Edge:
    """
    Represents a directed edge in the graph,
    connecting two nodes with a certain weight.
    """

    src: Node
    dst: Node
    weight: int
    key: str
    route: Route

    def __hash__(self) -> int:
        return hash(self.key)

    def __str__(self) -> str:
        return f"{self.key} (weight:{self.weight})"
