from enum import Enum
from logging import getLogger

from src.lib.graph.graph import MultiDiGraph
from src.lib.pathfinding import PathfindingAlgorithm
from src.models import Map

from .drone import Drone

logger = getLogger(__name__)


class SimulationState(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3


class SimulationMode(Enum):
    NORMAL = 0
    STEP_BY_STEP = 1


class Simulation:
    def __init__(
        self,
        map: Map,
        map_graph: MultiDiGraph,
        path_finder: type[PathfindingAlgorithm],
        speed_multiplier: float = 1.0,
        mode: SimulationMode = SimulationMode.NORMAL,
    ) -> None:
        self.map = map
        self.graph = map_graph
        self.path_finder = path_finder
        self._speed_multiplier = speed_multiplier
        self.mode = mode
        self.reset()

    def _reset_drones(self) -> None:
        (start_x, start_y) = (self.map.start_hub.x, self.map.start_hub.y)
        self.drones = [
            Drone(id=str(i), x=start_x, y=start_y) for i in range(self.map.nb_drones)
        ]

        pathfinder = self.path_finder(self.graph)

        logger.info("Resetting drones and generating paths...")
        try:
            for drone in self.drones:
                drone.generate_fly_path(
                    path_finder=pathfinder,
                    start_node=self.graph.nodes[self.map.start_hub.name],
                    end_node=self.graph.nodes[self.map.end_hub.name],
                )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error generating paths for drones: {e}")
            raise
        logger.info("All drones reset and paths generated.")

    def _reset_nodes(self) -> None:
        for node in self.graph.nodes.values():
            node.occupencies.clear()
            for edge in node.edges:
                edge.route.occupencies.clear()

    @property
    def speed_multiplier(self) -> float:
        return self._speed_multiplier

    @speed_multiplier.setter
    def speed_multiplier(self, value: float) -> None:
        self._speed_multiplier = min(max(value, 0.1), 10.0)

    def start(self) -> None:
        self.state = SimulationState.RUNNING

    def pause(self) -> None:
        self.state = SimulationState.PAUSED

    def resume(self) -> None:
        self.state = SimulationState.RUNNING

    def reset(self) -> None:
        self.turn = 0
        self.elapsed_time = 0.0
        self.state = SimulationState.NOT_STARTED
        self._reset_nodes()
        self._reset_drones()

    def all_drones_finished(self) -> bool:
        return all(
            drone.x == self.map.end_hub.x and drone.y == self.map.end_hub.y
            for drone in self.drones
        )

    def update(self, dt: float) -> None:
        if self.state != SimulationState.RUNNING:
            return
        dt *= self.speed_multiplier
        self.elapsed_time += dt
        self.turn = int(self.elapsed_time)
        for drone in self.drones:
            drone.tween_position_for_turn(self.turn + 1, self.elapsed_time - self.turn)
        if self.all_drones_finished():
            self.state = SimulationState.FINISHED

            logger.info("Simulation finished! See output below:")
            logger.info("-" * 40)
            print(self.generate_report())
            logger.info("-" * 40)
            print(self.generate_output())
            logger.info("-" * 40)

    def generate_output(self) -> str:
        output = ""
        for turn in range(self.turn):
            moves = [
                f"D{drone.id}-{node.key}"
                for drone in self.drones
                if (node := drone.get_move_for_turn(turn + 1)) is not None
            ]

            output += f"{' '.join(moves)}\n"
        return output

    def generate_report(self) -> str:
        report = "Simulation Report\n"
        report += f"Elapsed Time: {self.elapsed_time:.2f} seconds\n"
        report += f"Total Turns: {self.turn}\n"
        report += f"Number of Drones: {len(self.drones)}\n"

        turns_per_drone = [len(drone.get_moves()) for drone in self.drones]

        avg_turns = (
            sum(turns_per_drone) / len(turns_per_drone) if turns_per_drone else 0
        )
        report += f"Average Turns per Drone: {avg_turns:.2f}\n"

        drones_per_turn = [
            len(
                [
                    drone
                    for drone in self.drones
                    if drone.get_move_for_turn(turn) is not None
                ]
            )
            for turn in range(self.turn)
        ]

        avg_drones_per_turn = (
            sum(drones_per_turn) / len(drones_per_turn) if drones_per_turn else 0
        )
        report += f"Average Drones Moving per Turn: {avg_drones_per_turn:.2f}\n"

        return report
