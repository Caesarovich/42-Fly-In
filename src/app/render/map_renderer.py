from typing import TYPE_CHECKING

import pygame

from src.models.connection import Connection
from src.models.hub import Hub, ZoneType

from .renderer import Renderer

if TYPE_CHECKING:
    from src.models.map import Map


class MapRenderer(Renderer):
    def __init__(self, screen: pygame.Surface, map: Map) -> None:
        super().__init__(screen)
        self.map = map

    def center(self) -> None:
        if not self.map.all_hubs:
            return

        min_x = min(hub.x for hub in self.map.all_hubs.values())
        max_x = max(hub.x for hub in self.map.all_hubs.values())
        min_y = min(hub.y for hub in self.map.all_hubs.values())
        max_y = max(hub.y for hub in self.map.all_hubs.values())

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.camera.position = pygame.Vector2(center_x, center_y)

    def render(self) -> None:
        self.screen.fill((0, 0, 0))

        for connection in self.map.connections:
            self._render_connection(connection)

        for hub in self.map.all_hubs.values():
            self._render_hub(hub)

    def _render_hub(self, hub: Hub) -> None:
        def render_zone_type(zone_type: ZoneType) -> None:
            color = zone_type.get_color()

            size = 40 * self.camera.zoom
            pos = self.camera.apply(hub_pos)

            pygame.draw.circle(self.screen, color, pos, size)

        color = hub.get_color()
        hub_pos = pygame.Vector2(hub.x, hub.y)

        render_zone_type(hub.metadata.zone)

        pos = self.camera.apply(hub_pos)
        size = 32 * self.camera.zoom

        pygame.draw.circle(self.screen, color, pos, size)

        self.render_text(hub.name, pos - pygame.Vector2(0, size * 1.6), (255, 255, 255))

        self.render_text(str(hub.max_drones), pos, (150, 150, 150))

    def _render_connection(self, connection: Connection) -> None:
        pos1 = self.camera.apply(pygame.Vector2(connection.hub1.x, connection.hub1.y))
        pos2 = self.camera.apply(pygame.Vector2(connection.hub2.x, connection.hub2.y))

        thickness = connection.metadata.max_link_capacity
        thickness *= int(self.camera.zoom * 4)
        thickness = max(1, int(thickness))
        color = (255, 255, 255)
        pygame.draw.line(self.screen, color, pos1, pos2, thickness)
