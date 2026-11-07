import random

import pygame

from src.lib.simulation.drone import Drone
from src.lib.simulation.simulation import Simulation

from .renderer import Renderer


class DroneRenderer(Renderer):
    def __init__(self, screen: pygame.Surface, simulation: Simulation) -> None:
        super().__init__(screen)
        self.simulation = simulation

    def center(self) -> None:
        return

    def render(self) -> None:
        for drone in self.simulation.drones:
            self._render_drone(drone)

    def _drones_at_position(self, x: float, y: float) -> list[Drone]:
        return [
            drone
            for drone in self.simulation.drones
            if (round(drone.x, 1) == round(x, 1) and round(drone.y, 1) == round(y, 1))
        ]

    def _render_drone(self, drone: Drone) -> None:
        drone_pos = pygame.Vector2(drone.x, drone.y)

        other_drones = self._drones_at_position(drone.x, drone.y)
        offset = other_drones.index(drone) * 0.2

        pos = self.camera.apply(drone_pos + pygame.Vector2(0, offset))

        size = 26.0 * self.camera.zoom
        rect = pygame.Rect(pos.x - size / 2, pos.y - size / 2, size, size)
        pygame.draw.rect(self.screen, (20, 20, 20), rect, border_radius=8)

        size = 22.0 * self.camera.zoom
        random.seed(drone.id)
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )
        rect = pygame.Rect(pos.x - size / 2, pos.y - size / 2, size, size)
        pygame.draw.rect(self.screen, color, rect, border_radius=4)

        self.render_text(drone.id, pos, (255, 255, 255))
