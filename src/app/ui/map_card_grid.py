from collections.abc import Callable

import pygame

from src.io.map_loader import MapInfo
from src.lib.colors.color_palette import ColorPalette

from .map_card import MapCard
from .ui_element import UIElement


class MapCardGrid(UIElement):
    def __init__(
        self,
        palette: ColorPalette,
        surface: pygame.Surface,
        map_infos: list[MapInfo],
        on_map_selected: Callable[[MapInfo], None],
    ) -> None:
        super().__init__(palette, surface)
        self.spacing = pygame.Vector2(20, 20)
        self.card_size = pygame.Vector2(500, 350)
        self.map_cards: list[tuple[MapCard, pygame.Vector2]] = []
        self.on_map_selected = on_map_selected
        self._create_map_cards(map_infos)
        self.scroll_offset = pygame.Vector2(0, 0)

    def _create_map_cards(self, map_infos: list[MapInfo]) -> None:
        columns_count = self.surface.get_width() // (self.card_size.x + self.spacing.x)
        columns_total_width = (
            columns_count * self.card_size.x + (columns_count - 1) * self.spacing.x
        )

        offset = pygame.Vector2(
            (self.surface.get_width() - columns_total_width) / 2, self.spacing.y
        )

        for i, map_info in enumerate(map_infos):
            col = i % columns_count
            row = i // columns_count
            card_position = offset + pygame.Vector2(
                col * (self.card_size.x + self.spacing.x),
                row * (self.card_size.y + self.spacing.y),
            )
            card_surface = pygame.Surface(self.card_size)
            card = MapCard(self.palette, card_surface, map_info, self.on_map_selected)
            self.map_cards.append((card, card_position))

    def on_mouse_move(self, pos: pygame.Vector2) -> None:
        super().on_mouse_move(pos)
        for card, card_pos in self.map_cards:
            card.on_mouse_move(pos - card_pos + self.scroll_offset)

    def on_hover_exit(self, pos: pygame.Vector2) -> None:
        super().on_hover_exit(pos)
        for card, card_pos in self.map_cards:
            card.on_hover_exit(pos - card_pos - self.scroll_offset)

    def on_mouse_click(self, pos: pygame.Vector2) -> None:
        super().on_mouse_click(pos)
        for card, card_pos in self.map_cards:
            if card.is_mouse_over(pos - card_pos + self.scroll_offset):
                card.on_mouse_click(pos - card_pos + self.scroll_offset)

    def on_mouse_scroll(self, scroll_amount: float) -> None:
        super().on_mouse_scroll(scroll_amount)
        self.scroll_offset.y -= scroll_amount * 40

        max_height = (len(self.map_cards) + 2) // 3 * (
            self.card_size.y + self.spacing.y
        ) + self.spacing.y

        max_scroll = max(0, max_height - self.surface.get_height())
        self.scroll_offset.y = max(0, min(self.scroll_offset.y, max_scroll))

    def render(self, dt: float) -> None:
        self.surface.fill(self.palette.Background)
        for card, pos in self.map_cards:
            card.render(dt)
            self.surface.blit(card.surface, pos - self.scroll_offset)
