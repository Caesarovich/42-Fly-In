from argparse import ArgumentParser
from pathlib import Path

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    maps_folder: Path = Field(
        default=Path("maps"), description="Path to the folder containing map files."
    )


def parse_args() -> AppConfig:
    parser = ArgumentParser(
        description=("Fly-in"),
        add_help=True,
    )
    parser.add_argument(
        "--maps-folder",
        type=Path,
        default=Path("maps"),
        help="Path to the folder containing map files.",
    )
    args = parser.parse_args()
    return AppConfig(**vars(args))
