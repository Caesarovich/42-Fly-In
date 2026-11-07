from abc import ABC, abstractmethod

from src.lib.graph import Node
from src.lib.graph.graph import MultiDiGraph

type Path = list[Node]


class PathfindingAlgorithm(ABC):
    def __init__(self, graph: MultiDiGraph) -> None:
        self.graph = graph

    @abstractmethod
    def find_path(self, start_node: Node, end_node: Node) -> Path:
        pass
