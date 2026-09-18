"""Complete-but-locked R3R2A real-run controller boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .authorization_record_r3r2 import validate_external_authorization
from .canonical import canonical_hash
from .contract_bundle_r3r2 import verify_bundle
from .real_v2_bridge_r3r2 import bridge_population_identity


FUTURE_RESULT_PATHS = (
    "status/research/mo_r4a_candidate_c_run1_evaluator_a_real_output_v1.json",
    "status/research/mo_r4a_candidate_c_run1_evaluator_b_real_output_v1.json",
    "status/research/mo_r4a_candidate_c_run1_ab_comparison_result_v1.json",
)
REAL_READ_SCOPE = "IDENTITY_STRUCTURE_ADAPTER_AUTHORIZATION_BUNDLE_AND_REAL_V2_BRIDGE_VALIDATION_ONLY"


def population_order_hash(events: tuple[Mapping[str, Any], ...]) -> str:
    return canonical_hash([{"eventId": event["eventId"], "eventHash": event["eventHash"]} for event in events])


def structural_real_preflight(root: Path | str, population: Any) -> dict[str, Any]:
    """Permitted structural read only; it never invokes evaluator or V2 science."""

    bundle = verify_bundle(root)
    bridge, bridge_hash = bridge_population_identity(population.events)
    return {
        "realFrozenPopulationRead": True, "realFrozenPopulationReadScope": REAL_READ_SCOPE,
        "populationCount": len(population.events), "populationHash": population.manifest["exactPopulationHash"],
        "populationOrderHash": population_order_hash(population.events), "realV2BridgePopulationHash": bridge_hash,
        "realV2BridgeCount": len(bridge), "bundleManifestHash": bundle["bundleManifestHash"],
        "realFrozenPopulationEvaluated": False, "realCandidateCOutputProduced": False,
        "realCandidateCOutputRowCount": 0, "realComparisonExecuted": False,
    }


def run_authorized_real_population(authorization_record: Mapping[str, Any] | None, expected_bindings: Mapping[str, Any], *_: Any, **__: Any) -> None:
    """Future entrypoint. It cannot start without a separately frozen record."""

    validate_external_authorization(authorization_record, expected_bindings)
    raise RuntimeError("R3R2A contains no authorized real execution record")
