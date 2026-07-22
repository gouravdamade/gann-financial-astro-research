from __future__ import annotations

from chart_conditioned_aspects.evaluation import resolve_activation_paths

from conftest import make_structure


def test_activation_paths_are_bounded_and_cycle_free(profiles) -> None:
    structure = make_structure(profiles, conjunction=True)
    paths = resolve_activation_paths(structure.graph, "SATURN", profiles)
    assert paths
    assert max(path.depth for path in paths) <= profiles.graph["max_activation_depth"]
    assert all(len(path.path) == len(set(path.path)) for path in paths)
    assert any(path.target_node == "PLANET:JUPITER" for path in paths)
