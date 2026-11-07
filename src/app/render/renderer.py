from abc import ABC, abstractmethod

import pygame

WORLD_TO_SCREEN_SCALE = 200


class Camera:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.reset()

    def screen_center(self) -> pygame.Vector2:
        return pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)

    def reset(self) -> None:
        self.position = pygame.Vector2(0, 0)
        self.zoom = 1.0

    def apply(self, pos: pygame.Vector2) -> pygame.Vector2:
        return (
            pos - self.position
        ) * WORLD_TO_SCREEN_SCALE * self.zoom + self.screen_center()

    def zoomIn(self, factor: float, zoom_at: pygame.Vector2 | None = None) -> None:
        if zoom_at is not None:
            offset = zoom_at - self.screen_center()
            offset /= self.zoom * WORLD_TO_SCREEN_SCALE
            self.panView(offset * (1 - 1 / factor))
        self.zoom = min(max(0.1, self.zoom * factor), 10.0)

    def panView(self, delta: pygame.Vector2) -> None:
        self.position += delta / (WORLD_TO_SCREEN_SCALE * self.zoom)

        self.position.x = min(max(-10000, self.position.x), 10000)
        self.position.y = min(max(-10000, self.position.y), 10000)


class Renderer(ABC):
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.camera = Camera(self.screen)
        self.base_font = pygame.font.SysFont("Arial", 16)
        self.reset()

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def center(self) -> None:
        pass

    def reset(self) -> None:
        self.screen.fill((0, 0, 0))
        self.camera.reset()

    def render_text(
        self, text: str, pos: pygame.Vector2, color: tuple[int, int, int]
    ) -> None:
        text_surface = self.base_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        self.screen.blit(text_surface, text_rect)
