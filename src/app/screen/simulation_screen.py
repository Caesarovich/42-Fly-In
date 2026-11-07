from typing import TYPE_CHECKING

import pygame

from src.app.render.multi_renderer import MultiRenderer
from src.lib.graph.graph import MultiDiGraph
from src.lib.simulation.simulation import Simulation, SimulationState
from src.models.map import Map

from .screen import Screen

if TYPE_CHECKING:
    from src.app.app import App


class SimulationScreen(Screen):
    def __init__(
        self,
        app: App,
        map: Map,
        graph: MultiDiGraph,
    ) -> None:
        super().__init__(app)
        self.simulation = Simulation(map, graph, app.algorithm.value)
        self.renderer = MultiRenderer(app.display_surface)

    def on_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            self._on_mouse_wheel(event)

        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            self._on_mouse_drag(event)

        if event.type == pygame.KEYDOWN:
            self._on_key_down(event)

    def _on_mouse_wheel(self, event: pygame.event.Event) -> None:
        if event.button == 4:
            self.renderer.camera.zoomIn(1.1, pygame.Vector2(event.pos[0], event.pos[1]))
        elif event.button == 5:
            self.renderer.camera.zoomIn(0.9, pygame.Vector2(event.pos[0], event.pos[1]))

    def _on_mouse_drag(self, event: pygame.event.Event) -> None:
        if pygame.mouse.get_pressed()[0]:  # Left button is held down
            delta = pygame.Vector2(-event.rel[0], -event.rel[1])
            self.renderer.camera.panView(delta)

    def _on_key_down(self, event: pygame.event.Event) -> None:
        from src.app.screen.loading_screen import LoadingScreen

        if event.key == pygame.K_ESCAPE:
            self.app.load_screen(LoadingScreen(self.app))
        if event.key == pygame.K_r:
            self.renderer.reset()
            self.renderer.center()
            self.simulation.reset()
        if event.key == pygame.K_c:
            self.renderer.center()
        if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            self.simulation.speed_multiplier *= 1.25
        if event.key == pygame.K_MINUS:
            self.simulation.speed_multiplier *= 0.8
        if event.key == pygame.K_m:
            self.renderer.mode = "map"
        if event.key == pygame.K_g:
            self.renderer.mode = "graph"
        if event.key == pygame.K_SPACE:
            if self.simulation.state == SimulationState.RUNNING:
                self.simulation.pause()
            else:
                self.simulation.resume()

    def on_update(self, dt: float) -> None:
        self.simulation.update(dt)

    def on_render(self, dt: float) -> None:
        self.renderer.render()
        pygame.display.flip()

    def on_enter(self) -> None:
        self.renderer.load_data(self.simulation)
        self.renderer.center()
