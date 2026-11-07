from collections.abc import Callable

import pygame

from src.io import MapInfo
from src.lib.colors import ColorPalette

from .ui_element import UIElement


class MapCard(UIElement):
    def __init__(
        self,
        palette: ColorPalette,
        surface: pygame.Surface,
        map_info: MapInfo,
        on_map_selected: Callable[[MapInfo], None],
    ) -> None:
        super().__init__(palette, surface)
        self.map_info = map_info
        self.base_font = pygame.font.Font(None, 24)
        self.on_map_selected = on_map_selected

    def on_hover_enter(self, pos: pygame.Vector2) -> None:
        super().on_hover_enter(pos)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def on_hover_exit(self, pos: pygame.Vector2) -> None:
        super().on_hover_exit(pos)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def on_mouse_click(self, pos: pygame.Vector2) -> None:
        super().on_mouse_click(pos)
        self.on_map_selected(self.map_info)

    def render(self, dt: float) -> None:
        self.surface.fill(self.palette.Background)

        background = pygame.Rect(
            0, 0, self.surface.get_width(), self.surface.get_height()
        )
        background_color = (
            self.palette.Secondary if not self.is_hovered else self.palette.Accent
        )
        pygame.draw.rect(self.surface, background_color, background, border_radius=32)

        rect = pygame.Rect(
            0, 0, self.surface.get_width(), self.surface.get_height() - 50
        )

        preview = pygame.transform.smoothscale(
            self.map_info.preview,
            rect.size,
        )

        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, *rect.size),
            border_top_left_radius=32,
            border_top_right_radius=32,
        )
        image = preview.copy().convert_alpha()
        image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.surface.blit(image, (0, 0))

        title = self.base_font.render(
            f"{self.map_info.category} - {self.map_info.name}", True, self.palette.Text
        )
        title_rect = title.get_rect(
            center=(self.surface.get_width() / 2, self.surface.get_height() - 25)
        )
        self.surface.blit(title, title_rect)
