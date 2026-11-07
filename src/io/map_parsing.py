from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from re import search


class MapEntry(ABC):
    @abstractmethod
    def __init__(self, line_number: int, content: str):
        self.line_number = line_number
        self.content = content
        self.metadata: dict[str, str] = {}

        metadata_regex = r"\[.*\]$"
        metadata_search = search(metadata_regex, content)
        if metadata_search:
            metadata_str = metadata_search.group(0)
            content = content[: metadata_search.start()].strip()
            self.metadata = self.parse_metadata(metadata_str)

        self.values = [c.strip() for c in content.split(" ")]

    def parse_metadata(self, metadata_str: str) -> dict[str, str]:
        metadata_str = metadata_str.strip("[]")
        metadata = {}
        for item in metadata_str.split(" "):
            if item.count("=") != 1:
                raise MapParser.ParsingError(
                    f"Invalid metadata format: '{item}' should be in "
                    f"the format 'key=value'",
                    self.line_number,
                )
            key, value = item.split("=")
            metadata[key.strip()] = value.strip()

        return metadata


class DroneNumberMapEntry(MapEntry):
    def __init__(self, line_number: int, content: str):
        super().__init__(line_number, content)

        if len(self.values) != 1:
            raise MapParser.ParsingError(
                f"Invalid drone number entry: expected 1 value "
                f"(number of drones), got {len(self.values)}",
                line_number,
            )
        try:
            self.nb_drones = int(self.values[0])
            if self.nb_drones < 0:
                raise ValueError(
                    f"Number of drones must be non-negative, got {self.nb_drones}"
                )
        except ValueError:
            raise MapParser.ParsingError(
                f"Invalid number of drones: expected an integer, got "
                f"'{self.values[0]}'",
                line_number,
            )


class HubMapEntry(MapEntry):
    def __init__(self, line_number: int, content: str):
        super().__init__(line_number, content)

        if len(self.values) != 3:
            raise MapParser.ParsingError(
                f"Invalid hub entry: expected 3 values (name, x, y), "
                f"got {len(self.values)}",
                line_number,
            )
        self.name = self.values[0].strip()
        if "-" in self.name:
            raise MapParser.ParsingError(
                f"Invalid hub name: '{self.name}' should not contain dashes",
                line_number,
            )
        try:
            self.x = int(self.values[1])
            self.y = int(self.values[2])
        except ValueError:
            raise MapParser.ParsingError(
                f"Invalid hub coordinates: x and y should be integers, got "
                f"'{self.values[1]}' and '{self.values[2]}'",
                line_number,
            )


class StartHubMapEntry(HubMapEntry):
    pass


class EndHubMapEntry(HubMapEntry):
    pass


class ConnectionMapEntry(MapEntry):
    def __init__(self, line_number: int, content: str):
        super().__init__(line_number, content)

        if len(self.values) != 1:
            raise MapParser.ParsingError(
                f"Invalid connection entry: expected 1 value "
                f"(hub names separated by '-'), got {len(self.values)}",
                line_number,
            )
        hubs = self.values[0].split("-")
        if len(hubs) != 2:
            raise MapParser.ParsingError(
                f"Invalid connection entry: expected 2 hub names "
                f"separated by '-', got {len(hubs)}",
                line_number,
            )
        self.hub1 = hubs[0].strip()
        self.hub2 = hubs[1].strip()

        if self.hub1 == self.hub2:
            raise MapParser.ParsingError(
                f"Invalid connection entry: "
                f"a hub cannot be connected to itself "
                f"('{self.hub1}')",
                line_number,
            )

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ConnectionMapEntry) and (
            (self.hub1 == value.hub1 and self.hub2 == value.hub2)
            or (self.hub1 == value.hub2 and self.hub2 == value.hub1)
        )


@dataclass
class MapData:
    nb_drones: int
    start_hub: StartHubMapEntry
    end_hub: EndHubMapEntry
    hubs: list[HubMapEntry]
    connections: list[ConnectionMapEntry]


class MapParser:
    class ParsingError(Exception):
        def __init__(self, message: str, line_number: int | None = None):
            if line_number is not None:
                message = f"Map error on line {line_number}: {message}"
            else:
                message = f"Map error: {message}"
            super().__init__(message)

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def _read_map_file(self) -> list[tuple[int, str]]:
        with open(self.file_path, "r") as file:
            lines = file.readlines()

            def line_filter(line: str) -> bool:
                line = line.strip()
                return bool(line) and not line.startswith("#")

            map_entries: list[tuple[int, str]] = [
                (i, line.strip()) for i, line in enumerate(lines) if line_filter(line)
            ]

            return map_entries

    def _parse_map_entry(self, line: tuple[int, str]) -> MapEntry:
        line_number, content = line

        if content.count(":") != 1:
            raise MapParser.ParsingError(
                "Invalid map entry format: expected 'type: values'", line_number
            )
        entry_type, entry_content = content.split(":", 1)
        entry_type = entry_type.strip().lower()
        entry_content = entry_content.strip()
        if entry_type == "nb_drones":
            return DroneNumberMapEntry(line_number, entry_content)
        elif entry_type == "hub":
            return HubMapEntry(line_number, entry_content)
        elif entry_type == "start_hub":
            return StartHubMapEntry(line_number, entry_content)
        elif entry_type == "end_hub":
            return EndHubMapEntry(line_number, entry_content)
        elif entry_type == "connection":
            return ConnectionMapEntry(line_number, entry_content)
        else:
            raise MapParser.ParsingError(
                f"Unknown map entry type: '{entry_type}'", line_number
            )

    def _parse_map_entries(self, map_entries: list[tuple[int, str]]) -> list[MapEntry]:
        return [self._parse_map_entry(line) for line in map_entries]

    def _parse_map(self, map_entries: list[tuple[int, str]]) -> MapData:
        parsed_entries = self._parse_map_entries(map_entries)

        drone_number_entry = parsed_entries[0]
        if not isinstance(drone_number_entry, DroneNumberMapEntry):
            raise MapParser.ParsingError(
                "First map entry must be the drone number entry",
                drone_number_entry.line_number,
            )

        parsed_entries = parsed_entries[1:]
        if any(isinstance(entry, DroneNumberMapEntry) for entry in parsed_entries):
            raise MapParser.ParsingError(
                "More than one drone number entry found", drone_number_entry.line_number
            )

        start_hub_entries: list[StartHubMapEntry] = [
            entry for entry in parsed_entries if isinstance(entry, StartHubMapEntry)
        ]

        if len(start_hub_entries) == 0:
            raise MapParser.ParsingError("Missing start hub entry")

        if len(start_hub_entries) > 1:
            raise MapParser.ParsingError(
                "Multiple start hub entries found", start_hub_entries[1].line_number
            )

        start_hub_entry = start_hub_entries[0]

        end_hub_entries: list[EndHubMapEntry] = [
            entry for entry in parsed_entries if isinstance(entry, EndHubMapEntry)
        ]

        if len(end_hub_entries) == 0:
            raise MapParser.ParsingError("Missing end hub entry")

        if len(end_hub_entries) > 1:
            raise MapParser.ParsingError(
                "Multiple end hub entries found", end_hub_entries[1].line_number
            )

        end_hub_entry = end_hub_entries[0]

        hub_entries: list[HubMapEntry] = []
        connection_entries: list[ConnectionMapEntry] = []

        def hub_exists(hub_name: str) -> bool:
            return any(
                entry.name == hub_name
                for entry in [start_hub_entry, end_hub_entry] + hub_entries
            )

        def connection_exists(connection: ConnectionMapEntry) -> bool:
            return any(entry == connection for entry in connection_entries)

        for entry in parsed_entries:
            if isinstance(entry, HubMapEntry) and not isinstance(
                entry, (StartHubMapEntry, EndHubMapEntry)
            ):
                if hub_exists(entry.name):
                    raise MapParser.ParsingError(
                        f"Duplicate hub name: '{entry.name}'", entry.line_number
                    )
                hub_entries.append(entry)
            elif isinstance(entry, ConnectionMapEntry):
                for hub in (entry.hub1, entry.hub2):
                    if not hub_exists(hub):
                        raise MapParser.ParsingError(
                            f"Connection entry references unknown hub '{hub}'",
                            entry.line_number,
                        )
                if connection_exists(entry):
                    raise MapParser.ParsingError(
                        f"Duplicate connection entry: '{entry.hub1}' - '{entry.hub2}'",
                        entry.line_number,
                    )
                connection_entries.append(entry)

        return MapData(
            nb_drones=drone_number_entry.nb_drones,
            start_hub=start_hub_entry,
            end_hub=end_hub_entry,
            hubs=hub_entries,
            connections=connection_entries,
        )

    def parse(self) -> MapData:
        map_entries = self._read_map_file()
        return self._parse_map(map_entries)
