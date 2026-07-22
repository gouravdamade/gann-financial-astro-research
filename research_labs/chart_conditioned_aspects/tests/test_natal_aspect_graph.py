from __future__ import annotations

from conftest import make_structure


def test_graph_hash_is_deterministic_and_doctrine_is_bounded(profiles) -> None:
    first = make_structure(profiles, conjunction=True)
    second = make_structure(profiles, conjunction=True)
    assert first.graph.graph_hash == second.graph.graph_hash
    edge_types = {edge.edge_type for edge in first.graph.edges}
    assert "CONJUNCTION" in edge_types
    assert "CONFIGURED_DRISHTI" not in edge_types
    assert "YOGA_RELATION" not in edge_types
    assert first.graph.execution_allowed is False


def test_unclassified_dignity_remains_unknown(profiles) -> None:
    structure = make_structure(profiles)
    moon = next(item for item in structure.conditions if item.planet == "MOON")
    assert moon.dignity == "UNCLASSIFIED_PROFILE_PENDING"
    assert (
        "EXALTATION_DEBILITATION_AND_RELATIONSHIP_PROFILE_NOT_CERTIFIED"
        in moon.unknowns
    )
