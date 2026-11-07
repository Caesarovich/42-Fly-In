import pygame
from pygame.event import Event

from src.lib.colors.color_palette import ColorPalette

from .ui_element import UIElement


class HeaderBar(UIElement):
    def __init__(
        self, palette: ColorPalette, surface: pygame.Surface, title: str
    ) -> None:
        super().__init__(palette, surface)
        self.title = title
        self.base_font = pygame.font.Font(None, 48)
        self.spacing = 20
        self.current_offset = 20
        self.children: list[tuple[UIElement, pygame.Vector2]] = []

    def add_child(self, child: UIElement) -> None:
        pos = child.surface.get_rect(
            midright=(
                self.surface.get_width() - self.current_offset,
                self.surface.get_height() / 2,
            )
        )

        self.children.append((child, pygame.Vector2(pos.topleft)))
        self.current_offset += child.surface.get_width() + self.spacing

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        for child, pos in self.children:
            offset_event = pygame.event.Event(event.type, **event.dict)
            if hasattr(offset_event, "pos"):
                offset_event.pos = pygame.Vector2(event.pos) - pos
            child.on_event(offset_event)

    def render(self, dt: float) -> None:
        self.surface.fill(self.palette.Secondary)

        text = self.base_font.render(self.title, True, self.palette.Text)
        text_rect = text.get_rect(midleft=(20, self.surface.get_height() / 2))
        self.surface.blit(text, text_rect)

        self._render_children(dt)

    def _render_children(self, dt: float) -> None:
        for child, pos in self.children:
            child.render(dt)
            self.surface.blit(child.surface, pos)
