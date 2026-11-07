import math

import pygame

from src.lib.graph import Edge, MultiDiGraph, Node, ProxyNode
from src.lib.simulation.simulation import Simulation

from .renderer import Renderer


def points_normal(p1: pygame.Vector2, p2: pygame.Vector2) -> pygame.Vector2:
    direction = p2 - p1
    length = direction.length()
    if length == 0:
        return pygame.Vector2(0, 0)
    normal = pygame.Vector2(-direction.y / length, direction.x / length)
    return normal


def point_around_between(
    p0: pygame.Vector2, p1: pygame.Vector2, radius: float
) -> pygame.Vector2:
    direction = p1 - p0
    length = direction.length()
    if length == 0:
        return p1
    direction.normalize_ip()
    return p1 - direction * radius


def arrow_middle_point(
    p0: pygame.Vector2, p1: pygame.Vector2, w: float
) -> pygame.Vector2:
    normal = points_normal(p0, p1)
    mid = (p0 + p1) / 2
    return mid + normal * w


def bezier_point(
    p0: pygame.Vector2, p1: pygame.Vector2, p2: pygame.Vector2, t: float
) -> tuple[float, float]:
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
    return (x, y)


def get_beszier_points(
    p0: pygame.Vector2, p1: pygame.Vector2, p2: pygame.Vector2
) -> list[tuple[float, float]]:
    return [bezier_point(p0, p1, p2, t / 30) for t in range(31)]


class GraphRenderer(Renderer):
    def __init__(self, screen: pygame.Surface, simulation: Simulation) -> None:
        super().__init__(screen)
        self.simulation = simulation

    @property
    def graph(self) -> MultiDiGraph:
        return self.simulation.graph

    def center(self) -> None:
        if not self.graph.nodes:
            return

        min_x = min(node.x for node in self.graph.nodes.values())
        max_x = max(node.x for node in self.graph.nodes.values())
        min_y = min(node.y for node in self.graph.nodes.values())
        max_y = max(node.y for node in self.graph.nodes.values())

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.camera.position = pygame.Vector2(center_x, center_y)

    def render(self) -> None:
        self.screen.fill((0, 0, 0))

        for node in self.graph.nodes.values():
            self._render_node(node)

        for edge in self.graph.edges.values():
            self._render_edge(edge)

    def _render_node(self, node: Node) -> None:
        color = (80, 200, 0) if isinstance(node, ProxyNode) else (10, 230, 0)
        node_pos = pygame.Vector2(node.x, node.y)

        pos = self.camera.apply(node_pos)
        size = 12.0 if isinstance(node, ProxyNode) else 24.0
        size *= self.camera.zoom

        pygame.draw.circle(self.screen, color, pos, size)

        self.render_text(node.key, pos - pygame.Vector2(0, size * 2.4), (255, 255, 255))

    def _render_edge(self, edge: Edge) -> None:
        start_pos = self.camera.apply(pygame.Vector2(edge.src.x, edge.src.y))
        end_pos = self.camera.apply(pygame.Vector2(edge.dst.x, edge.dst.y))

        self._draw_curved_arrow(
            start_pos,
            end_pos,
            radiuses=(
                12.0 if isinstance(edge.src, ProxyNode) else 24.0,
                12.0 if isinstance(edge.dst, ProxyNode) else 24.0,
            ),
        )

    def _draw_curved_arrow(
        self,
        start: pygame.Vector2,
        end: pygame.Vector2,
        radiuses: tuple[float, float] = (20, 20),
        offset: float = 40,
        color: tuple[int, int, int] = (255, 255, 255),
        width: float = 2,
    ) -> None:

        offset *= self.camera.zoom
        width *= self.camera.zoom
        radiuses = (radiuses[0] * self.camera.zoom, radiuses[1] * self.camera.zoom)

        start_offset = point_around_between(end, start, radiuses[0])
        end_offset = point_around_between(start, end, radiuses[1])
        start = start_offset
        end = end_offset

        mid_point = arrow_middle_point(start, end, offset)
        pts = get_beszier_points(start, mid_point, end)
        pygame.draw.lines(self.screen, color, False, pts, int(width))

        p_prev = pts[-2]
        p_end = pts[-1]
        angle = math.atan2(p_end[1] - p_prev[1], p_end[0] - p_prev[0])

        arrow_len = 12 * self.camera.zoom
        arrow_angle = math.pi / 7

        left = (
            p_end[0] - arrow_len * math.cos(angle - arrow_angle),
            p_end[1] - arrow_len * math.sin(angle - arrow_angle),
        )
        right = (
            p_end[0] - arrow_len * math.cos(angle + arrow_angle),
            p_end[1] - arrow_len * math.sin(angle + arrow_angle),
        )

        pygame.draw.polygon(self.screen, color, [p_end, left, right])
