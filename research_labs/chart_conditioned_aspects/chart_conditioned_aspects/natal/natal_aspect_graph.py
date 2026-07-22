from __future__ import annotations

from ..models import (
    FinancialDomainRecord,
    GraphEdge,
    GraphNode,
    NatalAspectGraph,
    NatalChartSnapshot,
    NatalCondition,
    OrganizationChartHypothesis,
    PlanetFunctionalRole,
    stable_hash,
)
from ..profiles import ResearchProfiles
from .natal_aspects import compile_conjunction_edges, compile_dispositor_edges


def _edge_sort_key(edge: GraphEdge) -> tuple[object, ...]:
    return (edge.source, edge.target, edge.edge_type, edge.status, edge.orb_deg or -1.0)


def compile_natal_graph(
    chart: OrganizationChartHypothesis,
    snapshot: NatalChartSnapshot,
    roles: tuple[PlanetFunctionalRole, ...],
    conditions: tuple[NatalCondition, ...],
    financial_domains: tuple[FinancialDomainRecord, ...],
    profiles: ResearchProfiles,
) -> NatalAspectGraph:
    nodes: dict[str, GraphNode] = {}
    for condition in conditions:
        node_id = f"PLANET:{condition.planet}"
        nodes[node_id] = GraphNode(
            node_id=node_id,
            node_type="PLANET",
            label=condition.planet,
            attributes=(
                ("sign", condition.sign),
                ("dignity", condition.dignity),
                ("house", condition.house),
            ),
        )

    house_ids: set[int] = set()
    edges: list[GraphEdge] = list(compile_conjunction_edges(snapshot, profiles))
    edges.extend(compile_dispositor_edges(snapshot, profiles))
    for role in roles:
        for house in role.owned_houses:
            house_ids.add(house)
            edges.append(
                GraphEdge(
                    source=f"PLANET:{role.planet}",
                    target=f"HOUSE:{house}",
                    edge_type="LORD_OF",
                    status=role.doctrine_status,
                    evidence_refs=role.evidence_refs,
                )
            )
    for condition in conditions:
        if condition.house is None:
            continue
        house_ids.add(condition.house)
        edges.append(
            GraphEdge(
                source=f"PLANET:{condition.planet}",
                target=f"HOUSE:{condition.house}",
                edge_type="OCCUPIES_HOUSE",
                status="DETERMINISTIC_CHART_PLACEMENT",
            )
        )
    for house in sorted(house_ids):
        nodes[f"HOUSE:{house}"] = GraphNode(
            node_id=f"HOUSE:{house}",
            node_type="HOUSE",
            label=f"House {house}",
        )

    ordered_nodes = tuple(sorted(nodes.values(), key=lambda item: item.node_id))
    ordered_edges = tuple(sorted(edges, key=_edge_sort_key))
    graph_payload = {
        "chart_hash": chart.chart_hash,
        "snapshot_hash": snapshot.snapshot_hash,
        "doctrine_profile_id": profiles.lordship["profile_id"],
        "graph_profile_id": profiles.graph["profile_id"],
        "nodes": ordered_nodes,
        "edges": ordered_edges,
        "financial_domains": financial_domains,
    }
    graph_hash = stable_hash(graph_payload)
    context_id = (
        f"{chart.chart_id}|{profiles.lordship['profile_id']}|"
        f"{profiles.graph['profile_id']}|{graph_hash[:16]}"
    )
    return NatalAspectGraph(
        natal_context_id=context_id,
        chart_id=chart.chart_id,
        chart_hash=chart.chart_hash,
        snapshot_hash=snapshot.snapshot_hash,
        doctrine_profile_id=str(profiles.lordship["profile_id"]),
        graph_profile_id=str(profiles.graph["profile_id"]),
        nodes=ordered_nodes,
        edges=ordered_edges,
        financial_domains=tuple(
            sorted(
                financial_domains,
                key=lambda item: (item.planet, item.source_house, item.domain),
            )
        ),
        doctrine_status="SOURCE_ALIGNED_PLUS_EXPERIMENTAL_MAPPING",
        graph_hash=graph_hash,
        execution_allowed=False,
    )
