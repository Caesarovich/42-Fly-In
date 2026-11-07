from enum import Enum

from .algorithm import Path, PathfindingAlgorithm
from .alpha_path_finder import AlphaPathFinder
from .beta_path_finder import BetaPathFinder
from .dijkstra_path_finder import DijkstraPathFinder


class PathfindingAlgorithms(Enum):
    DIJKSTRA = DijkstraPathFinder
    ALPHA = AlphaPathFinder
    BETA = BetaPathFinder


__all__ = [
    "AlphaPathFinder",
    "BetaPathFinder",
    "DijkstraPathFinder",
    "Path",
    "PathfindingAlgorithm",
    "PathfindingAlgorithms",
]
