"""Regression gates for the TD0R Trailokya source-recovery audit metadata."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
LEDGER_PATH = ROOT / "configs" / "sbc" / "trailokya" / "trailokya_1972_translation_coverage_ledger_v1.yaml"


def _ledger() -> dict:
    return yaml.safe_load(LEDGER_PATH.read_text(encoding="utf-8"))


def test_witness_hashes_and_authority_are_explicit() -> None:
    ledger = _ledger()
    witnesses = ledger["witnesses"]
    assert witnesses["primary1972"]["role"] == "CITATION_AUTHORITY"
    assert witnesses["primary1972"]["sha256"] == "1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194"
    assert witnesses["ocrCompanion"]["role"] == "NAVIGATION_AND_DRAFT_TRANSLATION_ONLY"
    assert witnesses["sameLineage2016"]["role"] == "SAME_LINEAGE_READING_WITNESS_NOT_INDEPENDENT_DOCTRINE"


def test_audit_recovers_the_five_required_artifacts_without_runtime_change() -> None:
    ledger = _ledger()
    paths = {item["path"] for item in ledger["recoveredArtifacts"]}
    assert len(paths) == 5
    assert all((ROOT / path).is_file() for path in paths)
    assert ledger["sourcePolicy"]["noRuntimeProfileBehaviorChanged"] is True
    assert ledger["sourcePolicy"]["noProductCapabilityAdded"] is True


def test_legacy_guidance_cross_source_and_engineering_parts_are_not_translation_claims() -> None:
    audit = _ledger()["legacyRuntimeGuidanceAudit"]
    assert audit["runtimeBehaviorChanged"] is False
    assert "PHALADEEPIKA_1937_SBC_EDITOR_SUPPLEMENT_shared_board_ray_worked_fixtures" in audit["crossSourceOnly"]
    assert "EXPERIMENTAL_NORMALIZED_GUIDANCE_V1" in audit["engineeringOrExperimentalOnly"]


def test_arghya_remains_source_preserved_and_execution_locked() -> None:
    audit = _ledger()["arghyaAudit"]
    assert audit["pass1Rows"] == audit["pass2Rows"] == 108
    assert audit["crossEditionMismatches"] == 0
    assert len(audit["sourcePreservedAnomalies"]) == 2
    assert "mt5_execution" in audit["blockedOutputs"]


def test_continuation_map_preserves_unresolved_dependencies() -> None:
    ledger = _ledger()
    dependencies = {item["id"]: item["status"] for item in ledger["continuationDependencies"]}
    assert dependencies["TD1_MOTION_STATE_CONTRACT"] == "UNRESOLVED"
    assert dependencies["TD1_ARGHYA_COMPLETE_WORKED_ARITHMETIC"] == "UNRESOLVED"
    assert ledger["sourcePolicy"]["executionAllowed"] is False
