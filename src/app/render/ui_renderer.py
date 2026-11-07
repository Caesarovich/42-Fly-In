import pygame

from src.lib.simulation.simulation import Simulation

from .renderer import Renderer


class UIRenderer(Renderer):
    def __init__(self, screen: pygame.Surface, simulation: Simulation) -> None:
        super().__init__(screen)
        self.font = pygame.font.SysFont("Arial", 16)
        self.simulation = simulation

    def center(self) -> None:
        pass

    def render(self) -> None:
        self._render_state()
        self._render_speed_multiplier()
        self._render_mode()
        self._render_turn()
        self._render_time()

    def _render_state(self) -> None:
        state_text = self.font.render(
            f"State: {self.simulation.state.name}", True, (255, 255, 255)
        )
        self.screen.blit(state_text, (10, 10))

    def _render_speed_multiplier(self) -> None:
        text = f"Speed Multiplier: {self.simulation.speed_multiplier:.2f}"
        speed_text = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(speed_text, (10, 30))

    def _render_mode(self) -> None:
        mode_text = self.font.render(
            f"Mode: {self.simulation.mode.name}", True, (255, 255, 255)
        )
        self.screen.blit(mode_text, (10, 50))

    def _render_turn(self) -> None:
        turn_text = self.font.render(
            f"Turn: {self.simulation.turn}", True, (255, 255, 255)
        )
        self.screen.blit(turn_text, (10, 70))

    def _render_time(self) -> None:
        text = f"Time: {self.simulation.elapsed_time:.2f}s"
        time_text = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(time_text, (10, 90))
