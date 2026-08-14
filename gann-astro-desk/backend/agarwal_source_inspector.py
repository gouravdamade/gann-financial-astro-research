from __future__ import annotations

"""Read-only adapter for the founder-approved Agarwal A2 source scope.

This module intentionally exposes source records, not a Vedha calculator.  The
immutable YAML packets remain the authority; the response is a presentation
contract for the desktop inspector and never enters synchronized field work.
"""

from pathlib import Path
from typing import Any

import yaml


AGARWAL_PROFILE_ID = "AGARWAL_2000_GEOMETRY_STRENGTH_INSPECTOR_V1"
AGARWAL_SOURCE_ID = "AGARWAL_MYSTICS_SAGAR_FIRST_EDITION_2000_HARDCOPY"
AGARWAL_EDITION = (
    "Mystics of Sarvato Bhadra Chakra and Astrological Predictions, "
    "M. K. Agarwal, Sagar Publications, New Delhi, First Edition 2000"
)
AGARWAL_DEPENDENCIES = [
    "deterministic motion-state precedence",
    "stationary/direct-slow handling",
    "board-ray traversal semantics",
    "origin-cell inclusion",
    "simultaneous-hit precedence",
    "cancellation/obstruction order",
    "universal validity-window contract",
    "reproducible complete worked method",
]


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Agarwal source fixture is missing: {path.name}")
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Agarwal source fixture is not a mapping: {path.name}")
    return value


def _source_witnesses(page_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    witnesses: list[dict[str, Any]] = []
    for item in page_evidence.get("photographs", []):
        if not isinstance(item, dict):
            continue
        witnesses.append(
            {
                "filename": item.get("filename"),
                "sha256": item.get("sha256"),
                "role": item.get("role"),
                "printedPage": 145 if "PASS_" in str(item.get("role", "")) else "145-146",
            }
        )
    historical = page_evidence.get("historical_capture")
    if isinstance(historical, dict):
        witnesses.append(
            {
                "filename": historical.get("filename"),
                "sha256": historical.get("sha256"),
                "role": historical.get("role"),
                "printedPage": "145-146",
            }
        )
    return witnesses


def _cells(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    page_evidence = geometry.get("page_evidence", {})
    packet_id = str(geometry.get("packet_id", ""))
    rows = geometry.get("transcription", {}).get("pass_A", {}).get("core_rows", [])
    cells: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows, start=1):
        if not isinstance(row, list):
            raise ValueError("Agarwal geometry core row is not a list")
        for column_index, raw_cell in enumerate(row, start=1):
            if not isinstance(raw_cell, dict):
                raise ValueError("Agarwal geometry cell is not a mapping")
            literal = raw_cell.get("literal")
            varga_number = raw_cell.get("varga_number")
            layer = raw_cell.get("layer")
            if literal is None or varga_number is None or layer is None:
                raise ValueError(
                    f"Agarwal geometry cell {row_index}:{column_index} is incomplete"
                )
            cells.append(
                {
                    "coordinate": {
                        "row": row_index,
                        "column": column_index,
                        "label": f"{row_index}:{column_index}",
                    },
                    "literal": str(literal),
                    "normalizedLabel": None,
                    "vargaNumber": int(varga_number),
                    "layer": str(layer),
                    "sourceProfile": AGARWAL_SOURCE_ID,
                    "printedPage": page_evidence.get("printed_page", 145),
                    "evidencePacketId": packet_id,
                    "sourceStatus": "SOURCE_CLOSED_TWO_PASS_AGREED",
                }
            )
    if len(cells) != 81 or len({cell["coordinate"]["label"] for cell in cells}) != 81:
        raise ValueError("Agarwal geometry fixture must contain exactly 81 unique cells")
    return cells


def _strength_rows(strength: dict[str, Any]) -> list[dict[str, Any]]:
    artifact_hashes = strength.get("artifact_sha256", {})
    rows: list[dict[str, Any]] = []
    for entry in strength.get("entries", []):
        if not isinstance(entry, dict):
            continue
        page = entry.get("printed_page")
        rows.append(
            {
                "variableId": entry.get("variable_id"),
                "categoryLiteral": entry.get("category_label_literal"),
                "literalValue": entry.get("literal_value"),
                "normalizedValue": entry.get("normalized_value"),
                "printedPage": page,
                "privateArtifact": strength.get("private_artifact"),
                "artifactSha256": artifact_hashes,
                "sourceStatus": entry.get("source_status"),
                "diffStatus": entry.get("diff_status"),
            }
        )
    return rows


def _financial_summary(financial: dict[str, Any]) -> dict[str, Any]:
    claims = financial.get("claims", [])
    return {
        "ledgerId": financial.get("ledger_id"),
        "classification": "FINANCIAL_HYPOTHESIS_LEDGER_ONLY",
        "printedPages": financial.get("printed_pages"),
        "claimCount": len(claims) if isinstance(claims, list) else 0,
        "claims": [
            {
                "hypothesisId": claim.get("hypothesis_id"),
                "printedPage": claim.get("printed_page"),
                "sourceStatus": claim.get("source_status"),
            }
            for claim in claims
            if isinstance(claim, dict)
        ],
        "labels": [
            "RESEARCH HYPOTHESIS",
            "NOT VALIDATED",
            "NOT FX-MAPPED",
            "NOT EXECUTABLE",
        ],
        "allowedUse": "research_ledger_only",
        "prohibitedUses": list(financial.get("prohibited_uses", [])),
    }


def build_agarwal_source_profile(project_root: Path) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    evidence_root = root / "configs" / "sbc" / "evidence_packets"
    geometry = _read_yaml(evidence_root / "agarwal_2000_page145_geometry_two_pass_v1.yaml")
    strength = _read_yaml(evidence_root / "agarwal_2000_strength_two_pass_v1.yaml")
    financial = _read_yaml(evidence_root / "agarwal_financial_sbc_v1_hypothesis_ledger.yaml")
    readiness = _read_yaml(root / "configs" / "sbc" / "agarwal_2000_a1_readiness.yaml")

    page_evidence = geometry.get("page_evidence", {})
    orientation = page_evidence.get("author_orientation", {})
    coordinate_convention = page_evidence.get("coordinate_convention", {})
    reconciliation = geometry.get("p144_reconciliation", {})
    readiness_values = readiness.get("readiness", {})
    geometry_ready = bool(readiness_values.get("AGARWAL_GEOMETRY_READY", {}).get("value"))
    strength_ready = bool(readiness_values.get("AGARWAL_STRENGTH_READY", {}).get("value"))

    if not geometry_ready or not strength_ready:
        raise ValueError("Agarwal A2 source scope is not ready in the canonical readiness record")

    return {
        "contract": "AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1",
        "schemaVersion": 1,
        "profileId": AGARWAL_PROFILE_ID,
        "sourceId": AGARWAL_SOURCE_ID,
        "edition": AGARWAL_EDITION,
        "authority": "MODERN_PRACTITIONER_SOURCE",
        "status": "GEOMETRY + STRENGTH SOURCE CLOSED",
        "geometry": {
            "contract": "AGARWAL_PAGE145_CORE_9X9_V1",
            "printedPage": page_evidence.get("printed_page", 145),
            "contextPage": page_evidence.get("context_page", 146),
            "orientation": orientation,
            "coordinateConvention": coordinate_convention,
            "cells": _cells(geometry),
            "sourceStatus": geometry.get("source_status"),
            "evidencePacketId": geometry.get("packet_id"),
            "witnesses": _source_witnesses(page_evidence),
            "p144Reconciliation": {
                "status": reconciliation.get("status"),
                "method": reconciliation.get("method"),
                "result": reconciliation.get("result"),
                "expected": reconciliation.get("expected"),
            },
            "historicalUnknownCenterFold": "SUPERSEDED_BY_CLEAR_PAGE145_PHOTOGRAPHS",
        },
        "strengthEvidence": {
            "contract": "AGARWAL_2000_NUMERICAL_AND_GENERAL_STRENGTH_TWO_PASS_V1",
            "packetId": strength.get("packet_id"),
            "sourceStatus": strength.get("source_status"),
            "rows": _strength_rows(strength),
            "aggregationStatus": "SOURCE_RECORD_ONLY_NO_MASTER_SCORE",
        },
        "vedhaStatus": "DEPENDENCY_NOT_READY",
        "vedhaDependencies": AGARWAL_DEPENDENCIES,
        "partialSourceEvidence": [
            "five subject factors",
            "nine-transit placement",
            "front/right/left direction records",
            "28-row target table",
            "planet classifications",
        ],
        "financialStatus": _financial_summary(financial),
        "provenance": {
            "geometryPrintedPage": 145,
            "allocationContextPrintedPage": 144,
            "geometryEvidence": "A1R3_TWO_PASS",
            "strengthPages": "54-55 / 60-63",
            "sourceStatus": "SOURCE_CLOSED_FOR_READ_ONLY_GEOMETRY_AND_STRENGTH",
            "privateImagePathsExposed": False,
        },
        "guardrails": {
            "readOnly": True,
            "marketDirectionInferred": False,
            "polarityAllowed": False,
            "scoreAggregationAllowed": False,
            "fieldsInfluenceAllowed": False,
            "autoSuggestAllowed": False,
            "mlAllowed": False,
            "executionAllowed": False,
        },
        "executionAllowed": False,
    }
