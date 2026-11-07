from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.app.app import App


class Screen(ABC):
    """
    Represents a screen in the application.

    A screen is responsible for handling its own events,
    updates, and rendering.
    """

    @abstractmethod
    def __init__(self, app: App) -> None:
        """
        Initialize the screen.

        :param app: The application instance.
        """
        self.app = app

    @abstractmethod
    def on_event(self, event: pygame.event.Event) -> None:
        """
        Handle an event.

        :param event: The event to handle.
        """

    @abstractmethod
    def on_update(self, dt: float) -> None:
        """
        Update the screen.

        :param dt: The time delta since the last update.
        """

    @abstractmethod
    def on_render(self, dt: float) -> None:
        """
        Render the screen.

        :param dt: The time delta since the last render.
        """

    @abstractmethod
    def on_enter(self) -> None:
        """
        Called when the screen is entered.
        """
