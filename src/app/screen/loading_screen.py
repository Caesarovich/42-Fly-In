import io
import logging
from concurrent.futures import Future
from typing import TYPE_CHECKING

import pygame
from pygame.event import Event

from src.app.screen.main_menu_screen import MainMenuScreen
from src.io.map_loader import MapInfo, MapLoader

from .screen import Screen

if TYPE_CHECKING:
    from src.app.app import App


logger = logging.getLogger(__name__)


def load_and_scale_svg(filename: str, scale: int) -> pygame.Surface:
    with open(filename) as svg_file:
        svg_string = svg_file.read()
    image = pygame.image.load(io.BytesIO(svg_string.encode()))
    return pygame.transform.smoothscale(image, (scale, scale))


class LoadingScreen(Screen):
    def __init__(self, app: App) -> None:
        super().__init__(app)
        self.map_loader = MapLoader(self.app.config.maps_folder)
        self.spinner = load_and_scale_svg(
            "src/assets/180-ring-with-bg.svg",
            64,
        )
        self.splash_image = pygame.image.load("src/assets/splash.png").convert_alpha()

    def on_update(self, dt: float) -> None:
        pass

    def on_event(self, event: Event) -> None:
        pass

    def on_render(self, dt: float) -> None:
        self.total_time += dt
        self.app.display_surface.fill(self.app.color_palette.Background)
        spinner = pygame.transform.rotate(
            self.spinner,
            self.total_time * 360,
        )
        loading_center = self.app.display_surface.get_rect().center
        spinner_rect = spinner.get_rect(center=loading_center + pygame.Vector2(0, 100))
        self.app.display_surface.blit(spinner, spinner_rect)

        splash_size = (
            self.splash_image.get_width() * 0.5,
            self.splash_image.get_height() * 0.5,
        )
        spash = pygame.transform.smoothscale(
            self.splash_image,
            splash_size,
        )
        splash_rect = spash.get_rect(center=loading_center + pygame.Vector2(0, -200))
        self.app.display_surface.blit(spash, splash_rect)

    def on_enter(self) -> None:
        self.total_time = 0.0
        map_load_future = self.map_loader.load_all_maps_async()
        map_load_future.add_done_callback(self._on_map_load_complete)

    def _on_map_load_complete(
        self,
        future: Future[dict[str, MapInfo | None]],
    ) -> None:
        result = future.result()
        loaded_maps = [data for data in result.values() if data is not None]
        logger.info(f"Loaded {len(loaded_maps)} maps successfully")
        self.app.load_screen(MainMenuScreen(self.app, loaded_maps))
