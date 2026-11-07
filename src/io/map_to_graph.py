from typing import TYPE_CHECKING

from src.lib.graph import Edge, MultiDiGraph, Node, ProxyNode, Route
from src.models import Connection, Hub, ZoneType
from src.models.hub import EndHub, StartHub

if TYPE_CHECKING:
    from src.models.map import Map


def map_to_graph(map: Map) -> MultiDiGraph:
    def _make_route(node1: Node, node2: Node, connection: Connection) -> Route:
        (n1, n2) = sorted((node1, node2), key=lambda n: n.key)
        return Route(
            key=f"{n1.key}-{n2.key}",
            max_occupancy=connection.metadata.max_link_capacity,
            nodes=(n1, n2),
            edges=set(),
        )

    def _make_restricted_zone_proxy_node(route: Route) -> ProxyNode:
        (n1, n2) = sorted(route.nodes, key=lambda n: n.key)
        return ProxyNode(
            key=f"{n1.key}-{n2.key}",
            maximum_occupancy=route.max_occupancy,
            proxy_for=route,
            x=(n1.x + n2.x) / 2,
            y=(n1.y + n2.y) / 2,
        )

    def _add_edge(src: Node, dst: Node, route: Route, suffix: str, weight: int) -> Edge:
        key = f"{route.key}-{suffix}"
        e = Edge(src=src, dst=dst, weight=weight, key=key, route=route)
        route.edges.add(e)
        graph.add_edge(e)
        return e

    def _hub_weight(hub: Hub) -> int:
        if hub.metadata.zone == ZoneType.Blocked:
            return 1000
        if hub.metadata.zone == ZoneType.Priority:
            return 99
        return 100

    graph = MultiDiGraph()
    for hub in map.all_hubs.values():
        node = Node(
            key=hub.name,
            maximum_occupancy=(
                hub.max_drones
                if not isinstance(hub, (StartHub, EndHub))
                else map.nb_drones
            ),
            x=hub.x,
            y=hub.y,
        )
        graph.add_node(node)

    for connection in map.connections:
        node1 = graph.nodes[connection.hub1.name]
        node2 = graph.nodes[connection.hub2.name]

        if (
            connection.hub1.metadata.zone == ZoneType.Blocked
            or connection.hub2.metadata.zone == ZoneType.Blocked
        ):
            continue

        if connection.hub1.max_drones == 0 or connection.hub2.max_drones == 0:
            continue

        if connection.metadata.max_link_capacity == 0:
            continue

        route = _make_route(node1, node2, connection)

        hub1_restricted = connection.hub1.metadata.zone == ZoneType.Restricted
        hub2_restricted = connection.hub2.metadata.zone == ZoneType.Restricted

        if not hub1_restricted and not hub2_restricted:
            _add_edge(node1, node2, route, "edge1", _hub_weight(connection.hub1))
            _add_edge(node2, node1, route, "edge2", _hub_weight(connection.hub2))
            continue

        proxy = _make_restricted_zone_proxy_node(route)
        graph.add_node(proxy)

        if hub1_restricted and hub2_restricted:
            _add_edge(node1, proxy, route, "edge1", _hub_weight(connection.hub1))
            _add_edge(proxy, node2, route, "edge2", _hub_weight(connection.hub2))
            _add_edge(
                proxy, node1, route, "edge1-reverse", _hub_weight(connection.hub1)
            )
            _add_edge(
                node2, proxy, route, "edge2-reverse", _hub_weight(connection.hub2)
            )
        elif hub1_restricted:
            _add_edge(node2, proxy, route, "edge1", _hub_weight(connection.hub2))
            _add_edge(proxy, node1, route, "edge2", _hub_weight(connection.hub1))
            _add_edge(
                node1, node2, route, "edge1-reverse", _hub_weight(connection.hub1)
            )
        else:
            _add_edge(node1, proxy, route, "edge1", _hub_weight(connection.hub1))
            _add_edge(proxy, node2, route, "edge2", _hub_weight(connection.hub2))
            _add_edge(
                node2, node1, route, "edge1-reverse", _hub_weight(connection.hub2)
            )

    return graph
