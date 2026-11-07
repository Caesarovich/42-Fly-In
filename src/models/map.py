from functools import cached_property

from src.io.map_parsing import HubMapEntry, MapData

from .connection import Connection, ConnectionMetadata
from .hub import EndHub, Hub, StartHub, ZoneMetadata


class Map:
    """
    Represents the map of the environment, including hubs, connections,
    and the number of drones.
    """

    def __init__(self, data: MapData):
        self.nb_drones = data.nb_drones
        self.start_hub = StartHub(
            name=data.start_hub.name,
            x=data.start_hub.x,
            y=data.start_hub.y,
            metadata=ZoneMetadata.model_validate(data.start_hub.metadata),
        )
        self.end_hub = EndHub(
            name=data.end_hub.name,
            x=data.end_hub.x,
            y=data.end_hub.y,
            metadata=ZoneMetadata.model_validate(data.end_hub.metadata),
        )

        def hub_data_to_hub(hub_data: HubMapEntry) -> Hub:
            return Hub(
                name=hub_data.name,
                x=hub_data.x,
                y=hub_data.y,
                metadata=ZoneMetadata.model_validate(hub_data.metadata),
            )

        self.hubs = {entry.name: hub_data_to_hub(entry) for entry in data.hubs}

        self.connections: list[Connection] = []

        for connection_data in data.connections:
            connection = Connection(
                hub1=self.all_hubs[connection_data.hub1],
                hub2=self.all_hubs[connection_data.hub2],
                metadata=ConnectionMetadata.model_validate(connection_data.metadata),
            )
            self.connections.append(connection)

    @cached_property
    def all_hubs(self) -> dict[str, Hub]:
        return {
            **self.hubs,
            self.start_hub.name: self.start_hub,
            self.end_hub.name: self.end_hub,
        }
