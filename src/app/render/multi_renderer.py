from typing import Literal

import pygame

from src.app.render.drone_renderer import DroneRenderer
from src.app.render.ui_renderer import UIRenderer
from src.lib.simulation.simulation import Simulation

from .graph_renderer import GraphRenderer
from .map_renderer import MapRenderer
from .renderer import Renderer

RenderMode = Literal["map", "graph"]


class MultiRenderer(Renderer):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.mode: RenderMode = "map"
        self.map_renderer: MapRenderer | None = None
        self.graph_renderer: GraphRenderer | None = None
        self.drone_renderer: DroneRenderer | None = None
        self.ui_renderer: UIRenderer | None = None

    def load_data(self, simulation: Simulation) -> None:
        self.map_renderer = MapRenderer(self.screen, simulation.map)
        self.graph_renderer = GraphRenderer(self.screen, simulation)
        self.drone_renderer = DroneRenderer(self.screen, simulation)
        self.ui_renderer = UIRenderer(self.screen, simulation)
        self.map_renderer.camera = self.camera
        self.graph_renderer.camera = self.camera
        self.drone_renderer.camera = self.camera
        self.ui_renderer.camera = self.camera

    def center(self) -> None:
        if self.mode == "map" and self.map_renderer is not None:
            self.map_renderer.center()
        elif self.mode == "graph" and self.graph_renderer is not None:
            self.graph_renderer.center()

    def render(self) -> None:
        if self.mode == "map" and self.map_renderer is not None:
            self.map_renderer.render()
        elif self.mode == "graph" and self.graph_renderer is not None:
            self.graph_renderer.render()
        if self.drone_renderer is not None:
            self.drone_renderer.render()
        if self.ui_renderer is not None:
            self.ui_renderer.render()
