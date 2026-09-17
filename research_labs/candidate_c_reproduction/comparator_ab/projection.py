"""Frozen semantic projection; evaluator-specific provenance bytes are excluded."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .models import NeutralFixture, SemanticRow


PROJECTION_CONTRACT = {
    "contractId": "MO_R4A_CANDIDATE_C_AB1_SEMANTIC_PROJECTION_V1",
    "comparedFields": [
        "fixtureId", "semanticFixtureIdentityHash", "sourceProfile", "componentId", "sourceContractId",
        "provenance.operatorId", "provenance.operatorVersion_when_present_in_both", "outputStatus",
        "sourceValue_when_VALUE", "unknownReasonCode_when_UNKNOWN", "provenance.sourceStatus_when_present_in_both",
    ],
    "excludedFields": [
        "inputIdentity", "inputIdentityHash", "sourceLocatorFormatting", "sourceArtifactRepresentation",
        "explanatoryProvenanceFields",
    ],
    "canonicalSourceValueRules": {
        "SARAVALI_4_32_ORDINARY_DRSTI_V1": "DRSTI_<numerator>_<denominator> and <numerator>/<denominator> both canonicalize to <numerator>/<denominator>; source ledger rule stores a fraction.",
    },
}


def _canonical_source_value(operator_id: str, value: Any) -> Any:
    if operator_id == "SARAVALI_4_32_ORDINARY_DRSTI_V1" and isinstance(value, str) and value.startswith("DRSTI_"):
        parts = value.removeprefix("DRSTI_").split("_")
        if len(parts) == 2 and all(part.isdigit() for part in parts):
            return f"{parts[0]}/{parts[1]}"
    return value


def project_rows(fixture: NeutralFixture, rows: Sequence[Mapping[str, Any]]) -> list[SemanticRow]:
    projected: list[SemanticRow] = []
    for row in rows:
        provenance = row.get("provenance")
        if not isinstance(provenance, Mapping):
            raise ValueError("evaluator output has no provenance mapping")
        operator_id = provenance.get("operatorId")
        if not isinstance(operator_id, str):
            raise ValueError("evaluator output has no provenance.operatorId")
        output_status = row.get("outputStatus")
        if output_status not in {"VALUE", "UNKNOWN"}:
            raise ValueError("evaluator output status is outside the frozen enum")
        if output_status == "VALUE":
            source_value = _canonical_source_value(operator_id, row.get("sourceValue"))
            unknown_reason_code = None
        else:
            source_value = None
            unknown_reason_code = row.get("unknownReasonCode")
            if not isinstance(unknown_reason_code, str):
                raise ValueError("UNKNOWN evaluator output has no unknown reason")
        projected.append(
            SemanticRow(
                fixture_id=fixture.fixture_id,
                semantic_fixture_identity_hash=fixture.semantic_fixture_identity_hash,
                fixture_family=fixture.fixture_family,
                coverage_tags=fixture.coverage_tags,
                source_profile=str(row.get("sourceProfile")),
                component_id=str(row.get("componentId")),
                source_contract_id=str(row.get("sourceContractId")),
                operator_id=operator_id,
                operator_version=str(provenance["operatorVersion"]) if provenance.get("operatorVersion") is not None else None,
                output_status=output_status,
                source_value=source_value,
                unknown_reason_code=unknown_reason_code,
                source_status=str(provenance["sourceStatus"]) if provenance.get("sourceStatus") is not None else None,
                original_row=row,
            )
        )
    return projected
