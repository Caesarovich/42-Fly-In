import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from src.app.render.map_renderer import MapRenderer
from src.lib.graph import MultiDiGraph

from .map_parsing import MapData, MapParser
from .map_to_graph import map_to_graph

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.models.map import Map


@dataclass
class MapInfo:
    """
    Container for map information, including the name,
    parsed data, and a rendered preview.
    """

    name: str
    category: str
    data: MapData
    map: Map
    graph: MultiDiGraph
    preview: pygame.Surface


class MapLoader:
    """
    Wraps the functionality to load maps from a directory, parse them,
    convert them to graph representations, and generate previews for display.
    """

    def __init__(self, map_dir: Path) -> None:
        assert map_dir.is_dir(), f"{map_dir} is not a directory"
        self.map_dir = map_dir

    def get_map_paths(self) -> list[Path]:
        return list(self.map_dir.glob("**/*.txt"))

    def load_map(self, map_path: Path) -> MapInfo | None:
        from src.models.map import Map

        try:
            map_data = MapParser(map_path).parse()
            map_model = Map(map_data)
            graph = map_to_graph(map_model)
            renderer = MapRenderer(pygame.Surface((500, 300)), map_model)
            renderer.camera.zoom = 0.4

            renderer.center()
            renderer.render()

            logger.info(f"Successfully loaded map: {map_path}")
            time.sleep(0.1)
            return MapInfo(
                name=map_path.stem,
                category=map_path.parent.name,
                data=map_data,
                map=map_model,
                graph=graph,
                preview=renderer.screen,
            )
        except Exception as error:  # noqa: BLE001
            logger.warning(f"Failed to load map {map_path}: {error}")
            return None

    def load_all_maps_async(self) -> Future[dict[str, MapInfo | None]]:
        map_paths = self.get_map_paths()
        executor = ThreadPoolExecutor(max_workers=max(1, len(map_paths)))
        future = executor.submit(
            lambda: {str(path): self.load_map(path) for path in map_paths}
        )
        future.add_done_callback(lambda _: executor.shutdown(wait=False))
        return future
