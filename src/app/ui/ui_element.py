import logging
from abc import ABC, abstractmethod

import pygame

from src.lib.colors.color_palette import ColorPalette

logger = logging.getLogger(__name__)


class UIElement(ABC):
    def __init__(self, palette: ColorPalette, surface: pygame.Surface) -> None:
        self.surface = surface
        self.palette = palette
        self.is_hovered = False

    def on_hover_enter(self, pos: pygame.Vector2) -> None:
        logger.debug(f"Hover enter on {self} at {pos}")
        self.is_hovered = True

    def on_hover_exit(self, pos: pygame.Vector2) -> None:
        logger.debug(f"Hover exit on {self} at {pos}")
        self.is_hovered = False

    def is_mouse_over(self, pos: pygame.Vector2) -> bool:
        return self.surface.get_rect().collidepoint(pos)

    def on_mouse_move(self, pos: pygame.Vector2) -> None:
        if self.is_mouse_over(pos):
            if not self.is_hovered:
                self.on_hover_enter(pos)
        else:
            if self.is_hovered:
                self.on_hover_exit(pos)

    def on_mouse_click(self, pos: pygame.Vector2) -> None:
        logger.debug(f"Mouse click on {self} at {pos}")

    def on_mouse_scroll(self, scroll_amount: float) -> None:
        logger.debug(f"Mouse scroll on {self} with amount {scroll_amount}")

    def on_event(self, event: pygame.event.Event) -> None:
        if not hasattr(event, "pos"):
            event.pos = -1, -1
        if event.type == pygame.MOUSEMOTION:
            self.on_mouse_move(pygame.Vector2(event.pos))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_mouse_over(pygame.Vector2(event.pos)):
                self.on_mouse_click(pygame.Vector2(event.pos))
        elif event.type == pygame.MOUSEWHEEL and self.is_mouse_over(event.pos):
            self.on_mouse_scroll(event.y)

    @abstractmethod
    def render(self, dt: float) -> None:
        pass
