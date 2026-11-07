from pydantic import BaseModel, Field

from .hub import Hub


class ConnectionMetadata(BaseModel):
    max_link_capacity: int = Field(
        ge=0,
        default=1,
        description=(
            "The maximum number of drones that can use this connection at the same time"
        ),
    )


class Connection(BaseModel):
    hub1: Hub = Field(...)
    hub2: Hub = Field(...)
    metadata: ConnectionMetadata = Field(...)
