import logging

import pygame

from src.lib.colors import BeachSummerPalette, ColorPalette
from src.lib.pathfinding import PathfindingAlgorithms

from .args import AppConfig
from .screen.screen import Screen

logger = logging.getLogger(__name__)


class App:
    def __init__(self, config: AppConfig) -> None:
        pygame.font.init()
        pygame.display.set_caption("Fly-in")
        self.config = config
        self.color_palette: ColorPalette = BeachSummerPalette
        self.display_surface = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = False
        self.algorithm: PathfindingAlgorithms = PathfindingAlgorithms.ALPHA
        self.screen: Screen | None = None
        self.total_time = 0.0

    def load_screen(self, screen: Screen) -> None:
        logger.debug(f"Loading screen: {type(screen).__name__}")
        self.screen = screen
        self.screen.on_enter()

    def on_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif self.screen:
            self.screen.on_event(event)

    def on_update(self, dt: float) -> None:
        if self.screen:
            self.screen.on_update(dt)

    def on_render(self, dt: float) -> None:
        if self.screen:
            self.screen.on_render(dt)
            pygame.display.flip()

    def run(self) -> None:
        dt = 0.0
        self.running = True

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update(dt)
            self.on_render(dt)
            dt = self.clock.tick(60.0) / 1000.0
            self.total_time += dt

        logger.info("Exiting application")

        pygame.quit()
