"""Comparator-owned neutral fixture and mismatch models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class NeutralFixture:
    fixture_id: str
    fixture_family: str
    source_body: str
    target_body: str
    source_sign_index: int
    target_sign_index: int
    sun_sign_index: int
    coverage_tags: tuple[str, ...]
    optional_aspect_type: str | None = None
    semantic_fixture_identity_hash: str = ""

    def semantic_input(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "fixtureId": self.fixture_id,
            "fixtureFamily": self.fixture_family,
            "sourceBody": self.source_body,
            "targetBody": self.target_body,
            "sourceSignIndex": self.source_sign_index,
            "targetSignIndex": self.target_sign_index,
            "sunSignIndex": self.sun_sign_index,
            "coverageTags": list(self.coverage_tags),
        }
        if self.optional_aspect_type is not None:
            value["optionalAspectType"] = self.optional_aspect_type
        return value

    def to_dict(self) -> dict[str, Any]:
        value = self.semantic_input()
        value["semanticFixtureIdentityHash"] = self.semantic_fixture_identity_hash
        return value


@dataclass(frozen=True)
class SemanticRow:
    fixture_id: str
    semantic_fixture_identity_hash: str
    fixture_family: str
    coverage_tags: tuple[str, ...]
    source_profile: str
    component_id: str
    source_contract_id: str
    operator_id: str
    operator_version: str | None
    output_status: str
    source_value: Any | None
    unknown_reason_code: str | None
    source_status: str | None
    original_row: Mapping[str, Any]

    def row_key(self) -> tuple[str, str, str, str, str]:
        return (
            self.semantic_fixture_identity_hash,
            self.source_profile,
            self.component_id,
            self.source_contract_id,
            self.operator_id,
        )

    def comparison_view(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "fixtureId": self.fixture_id,
            "semanticFixtureIdentityHash": self.semantic_fixture_identity_hash,
            "sourceProfile": self.source_profile,
            "componentId": self.component_id,
            "sourceContractId": self.source_contract_id,
            "operatorId": self.operator_id,
            "outputStatus": self.output_status,
        }
        if self.operator_version is not None:
            value["operatorVersion"] = self.operator_version
        if self.source_status is not None:
            value["sourceStatus"] = self.source_status
        if self.output_status == "VALUE":
            value["sourceValue"] = self.source_value
        else:
            value["unknownReasonCode"] = self.unknown_reason_code
        return value
