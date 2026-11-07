import logging
from typing import TYPE_CHECKING

import pygame

from src.app.screen.simulation_screen import SimulationScreen
from src.app.ui.enum_toggle import EnumToggle
from src.app.ui.header_bar import HeaderBar
from src.app.ui.map_card_grid import MapCardGrid
from src.io.map_loader import MapInfo
from src.lib.pathfinding import PathfindingAlgorithms

from .screen import Screen

if TYPE_CHECKING:
    from src.app.app import App


logger = logging.getLogger(__name__)


class MainMenuScreen(Screen):
    def __init__(self, app: App, maps: list[MapInfo]) -> None:
        super().__init__(app)
        self.loaded_maps = maps
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.header_bar = HeaderBar(
            self.app.color_palette,
            pygame.Surface((self.app.display_surface.get_width(), 80)),
            "Fly-in",
        )
        self.map_grid = MapCardGrid(
            self.app.color_palette,
            pygame.Surface(self.app.display_surface.get_size() - pygame.Vector2(0, 80)),
            self.loaded_maps,
            self._on_map_selected,
        )

    def on_event(self, event: pygame.event.Event) -> None:
        event = pygame.event.Event(event.type, **event.dict)
        self.header_bar.on_event(event)
        event.pos = pygame.mouse.get_pos() - pygame.Vector2(0, 80)
        self.map_grid.on_event(event)

    def on_update(self, dt: float) -> None:
        pass

    def on_render(self, dt: float) -> None:
        self.app.display_surface.fill(self.app.color_palette.Background)
        self._render_header(dt)
        self._render_map_list(dt)

    def _render_header(self, dt: float) -> None:
        self.header_bar.render(dt)
        self.app.display_surface.blit(self.header_bar.surface, (0, 0))

    def _render_map_list(self, dt: float) -> None:
        self.map_grid.render(dt)
        self.app.display_surface.blit(self.map_grid.surface, (0, 80))

    def _on_map_selected(self, map_info: MapInfo) -> None:
        try:
            screen = SimulationScreen(self.app, map_info.map, map_info.graph)
            self.app.load_screen(screen)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error loading map {map_info.name}: {e}")
            return

    def on_enter(self) -> None:
        logger.info("Entered Main Menu Screen")

        self.algorithm_toggle = EnumToggle(
            self.app.color_palette,
            pygame.Surface((150, 40)),
            PathfindingAlgorithms,
            lambda algo: setattr(self.app, "algorithm", algo),
            default_value=self.app.algorithm,
            background_color=self.app.color_palette.Secondary,
            base_color=self.app.color_palette.Primary,
            hover_color=self.app.color_palette.Accent,
        )
        self.header_bar.add_child(self.algorithm_toggle)
