from collections.abc import Callable
from enum import Enum
from typing import Any

import pygame

from src.lib.colors import ColorPalette

from .ui_element import UIElement


class EnumToggle[EnumType: Enum](UIElement):
    def __init__(
        self,
        palette: ColorPalette,
        surface: pygame.Surface,
        enum_class: type[EnumType],
        on_value_changed: Callable[[EnumType], None],
        default_value: EnumType | None = None,
        background_color: pygame.Color | None = None,
        base_color: pygame.Color | None = None,
        hover_color: pygame.Color | None = None,
    ) -> None:
        super().__init__(palette, surface)
        self.enum_class = enum_class
        self.choices: list[EnumType] = list(enum_class)
        self.current_index = (
            0 if default_value is None else self.choices.index(default_value)
        )
        self.base_font = pygame.font.Font(None, 24)
        self.on_value_changed = on_value_changed

        self._background_color = background_color or self.palette.Background
        self._base_color = base_color or self.palette.Primary
        self._hover_color = hover_color or self.palette.Accent

    @property
    def _current_color(self) -> pygame.Color:
        if self.is_hovered:
            return self._hover_color
        return self._base_color

    @property
    def selected(self) -> EnumType:
        return self.choices[self.current_index]

    @property
    def value(self) -> Any:
        return self.selected.value

    def on_hover_enter(self, pos: pygame.Vector2) -> None:
        super().on_hover_enter(pos)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def on_hover_exit(self, pos: pygame.Vector2) -> None:
        super().on_hover_exit(pos)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def on_mouse_click(self, pos: pygame.Vector2) -> None:
        super().on_mouse_click(pos)
        self.current_index = (self.current_index + 1) % len(self.choices)
        self.on_value_changed(self.selected)

    def render(self, dt: float) -> None:
        self.surface.fill(self._background_color)

        background = pygame.Rect(
            0, 0, self.surface.get_width(), self.surface.get_height()
        )
        background_color = self._current_color
        pygame.draw.rect(self.surface, background_color, background, border_radius=32)

        text = self.base_font.render(self.selected.name, True, self.palette.Text)
        text_rect = text.get_rect(center=self.surface.get_rect().center)
        self.surface.blit(text, text_rect)
