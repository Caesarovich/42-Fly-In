from enum import Enum

from pydantic import BaseModel, Field
from pygame import Color

from src.lib.colors import NAMED_COLORS


class ZoneType(Enum):
    """
    Standard zone with 1 turn movement cost (default)
    """

    Normal = "normal"

    """
    Inaccessible zone. Drones must not enter or pass through this zone.
    """
    Blocked = "blocked"

    """
    A sensitive or dangerous zone. Movement to this zone costs 2 turns.
    """
    Restricted = "restricted"

    """
    A preferred zone.
    Movement to this zone costs 1 turn
    but should be prioritized in pathfinding.
    """
    Priority = "priority"

    def get_color(self) -> Color:
        color_map = {
            ZoneType.Normal: Color(200, 200, 200),
            ZoneType.Blocked: Color(255, 0, 0),
            ZoneType.Restricted: Color(255, 255, 0),
            ZoneType.Priority: Color(0, 100, 200),
        }
        return color_map.get(self, Color(128, 128, 128))


class ZoneMetadata(BaseModel):
    zone: ZoneType = Field(default=ZoneType.Normal, description="The type of the zone")
    color: str | None = Field(
        default=None, description="The color of the zone for visualization purposes"
    )
    max_drones: int = Field(
        ge=0,
        default=1,
        description=(
            "The maximum number of drones that can occupy this zone at the same time"
        ),
    )


class Hub(BaseModel):
    """
    Represents a hub in the environment, with a name, coordinates,
    and metadata describing the zone type and occupancy limits.
    """

    metadata: ZoneMetadata = Field()
    name: str = Field(description="The unique name of the hub")
    x: int = Field(description="The x coordinate of the hub", ge=-10000, le=10000)
    y: int = Field(description="The y coordinate of the hub", ge=-10000, le=10000)

    def get_color(self) -> Color:
        color = Color(128, 128, 128)
        if isinstance(self, StartHub):
            color = Color(0, 255, 0)
        elif isinstance(self, EndHub):
            color = Color(255, 0, 0)
        if self.metadata.color:
            color = NAMED_COLORS.get(self.metadata.color, Color(128, 128, 128))
        return color

    @property
    def max_drones(self) -> int:
        if self.metadata.zone == ZoneType.Blocked:
            return 0
        return self.metadata.max_drones


class StartHub(Hub):
    pass


class EndHub(Hub):
    pass
