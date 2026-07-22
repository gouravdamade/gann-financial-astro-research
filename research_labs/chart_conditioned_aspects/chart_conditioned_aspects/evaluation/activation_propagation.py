from __future__ import annotations

from collections import deque

from ..models import ActivationPath, NatalAspectGraph
from ..profiles import ResearchProfiles


def resolve_activation_paths(
    graph: NatalAspectGraph,
    natal_target: str,
    profiles: ResearchProfiles,
) -> tuple[ActivationPath, ...]:
    start = f"PLANET:{str(natal_target).strip().upper()}"
    known_nodes = {node.node_id for node in graph.nodes}
    if start not in known_nodes:
        raise ValueError(f"natal target is absent from the immutable graph: {start}")
    max_depth = int(profiles.graph["max_activation_depth"])
    if max_depth < 0:
        raise ValueError("max_activation_depth cannot be negative")

    adjacency: dict[str, list[tuple[str, str]]] = {
        node_id: [] for node_id in known_nodes
    }
    for edge in graph.edges:
        adjacency[edge.source].append((edge.target, edge.edge_type))
        if edge.edge_type == "CONJUNCTION":
            adjacency[edge.target].append((edge.source, edge.edge_type))
    for neighbors in adjacency.values():
        neighbors.sort()

    paths: list[ActivationPath] = []
    queue = deque([(start, (start,), ())])
    shortest_depth: dict[str, int] = {start: 0}
    while queue:
        node_id, path, edge_types = queue.popleft()
        depth = len(edge_types)
        if depth >= max_depth:
            continue
        for neighbor, edge_type in adjacency.get(node_id, []):
            if neighbor in path:
                continue
            next_depth = depth + 1
            prior_depth = shortest_depth.get(neighbor)
            if prior_depth is not None and prior_depth < next_depth:
                continue
            shortest_depth[neighbor] = next_depth
            next_path = path + (neighbor,)
            next_edges = edge_types + (edge_type,)
            paths.append(
                ActivationPath(
                    target_node=neighbor,
                    depth=next_depth,
                    path=next_path,
                    edge_types=next_edges,
                )
            )
            queue.append((neighbor, next_path, next_edges))
    return tuple(
        sorted(paths, key=lambda item: (item.depth, item.target_node, item.path))
    )
