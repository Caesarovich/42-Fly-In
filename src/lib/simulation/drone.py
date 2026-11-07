from logging import getLogger

from src.lib.graph import Node
from src.lib.graph.edge import Edge
from src.lib.pathfinding.algorithm import PathfindingAlgorithm

logger = getLogger(__name__)


def can_move_to_node_at_turn(node: Node, edge: Edge, turn: int) -> bool:
    if not node.is_available(turn):
        return False
    return edge.route.is_available(turn)


def process_path(ideal_path: list[Node], current_turn: int = 0) -> list[Node] | None:
    logger.debug(
        f"Processing path at turn {current_turn}: "
        f"{[node.key for node in ideal_path]}..."
    )
    current_node = ideal_path[0]
    if not ideal_path:
        logger.info("Ideal path is empty, returning empty path...")
        return []
    if not current_node.is_available(current_turn):
        logger.info(
            f"Node {current_node.key} is not available "
            f"at turn {current_turn}, trying to wait..."
        )
        return None

    next_node = ideal_path[1] if len(ideal_path) > 1 else None
    if not next_node:
        logger.info("No next node, returning current path...")
        return [current_node]
    next_edge = current_node.get_edge_to_neighbor(next_node)
    if not next_edge:
        raise RuntimeError(f"No edge found from {current_node.key} to {next_node.key}")
    wait_count = 0
    while True:
        wait_count += 1
        if not can_move_to_node_at_turn(
            next_node, next_edge, current_turn + wait_count
        ):
            logger.info(
                f"Node {next_node.key} is not available at turn "
                f"{current_turn + wait_count}, trying to wait more..."
            )
            if not current_node.can_wait_at_node(current_turn + wait_count):
                logger.warning(
                    f"/!\\ Turn {current_turn}: Node {current_node.key} "
                    f"is not available for waiting after {wait_count} turns"
                )
                return None
            continue
        path = process_path(ideal_path[1:], current_turn + wait_count)
        if path is not None:
            return [current_node] * wait_count + path

        logger.warning(
            f"Turn {current_turn}: Node {current_node.key} "
            f"needs to wait for {wait_count} turns"
        )

        if not current_node.can_wait_at_node(current_turn + wait_count):
            logger.warning(
                f"/!\\ Turn {current_turn}: Node {current_node.key}"
                f" is not available for waiting after {wait_count} turns"
            )
            return None


class Drone:
    def __init__(self, id: str, x: float, y: float):
        self.id = id
        self.x = x
        self.y = y
        self.fly_path: list[Node] = []

    def generate_fly_path(
        self, path_finder: PathfindingAlgorithm, start_node: Node, end_node: Node
    ) -> None:
        logger.info(
            f"Generating fly path for drone {self.id} from "
            f"{start_node.key} to {end_node.key}..."
        )
        ideal_path = path_finder.find_path(start_node, end_node)

        if ideal_path[0] != start_node or ideal_path[-1] != end_node:
            raise RuntimeError("Pathfinding algorithm returned an invalid path")

        logger.debug(f"Drone {self.id} ideal path: {[node.key for node in ideal_path]}")
        reservable_path = process_path(ideal_path)
        if reservable_path is None:
            raise RuntimeError(f"No valid path found for the drone {self.id}")
        self.fly_path = reservable_path
        logger.info(
            f"Drone {self.id} reservable path: {[node.key for node in reservable_path]}"
        )
        for turn, node in enumerate(self.fly_path):
            logger.debug(
                f"Turn {turn}: Reserving node {node.key} for drone {self.id}..."
            )
            node.reserve_for_turn(turn, self.id)
            next_node = (
                self.fly_path[turn + 1] if turn + 1 < len(self.fly_path) else None
            )
            if next_node:
                edge = node.get_edge_to_neighbor(next_node)
                if not edge:
                    continue  # Means we are waiting at the same node
                logger.debug(
                    f"Turn {turn}: Reserving route "
                    f"{edge.route.key} for drone {self.id}..."
                )
                edge.route.reserve_for_turn(turn + 1, self.id)

    def get_position_for_turn(self, turn: int) -> tuple[float, float]:
        if not self.fly_path:
            return self.x, self.y
        if turn <= 0:
            return self.fly_path[0].x, self.fly_path[0].y
        if turn >= len(self.fly_path):
            return self.fly_path[-1].x, self.fly_path[-1].y
        return self.fly_path[turn].x, self.fly_path[turn].y

    def tween_position_for_turn(self, turn: int, t: float) -> None:
        if turn == 0:
            return
        target_x, target_y = self.get_position_for_turn(turn)
        prev_x, prev_y = self.get_position_for_turn(turn - 1)
        tweened_x = prev_x + (target_x - prev_x) * t
        tweened_y = prev_y + (target_y - prev_y) * t
        self.x = tweened_x
        self.y = tweened_y

    def get_move_for_turn(self, turn: int) -> Node | None:
        if turn < 0 or turn >= len(self.fly_path):
            return None
        if turn == 0:
            return self.fly_path[0]
        if self.fly_path[turn] == self.fly_path[turn - 1]:
            return None
        return self.fly_path[turn]

    def get_moves(self) -> list[Node]:
        return [
            node
            for i in range(len(self.fly_path))
            if (node := self.get_move_for_turn(i)) is not None
        ]
