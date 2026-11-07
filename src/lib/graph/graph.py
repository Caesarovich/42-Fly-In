from dataclasses import dataclass, field

from .edge import Edge
from .node import Node


@dataclass
class MultiDiGraph:
    """
    Represents a directed graph.
    """

    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        self.nodes[node.key] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges[edge.key] = edge
        edge.src.neighbors.add(edge.dst)
        edge.src.edges.add(edge)
