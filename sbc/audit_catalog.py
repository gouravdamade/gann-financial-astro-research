from __future__ import annotations

import base64
import ctypes
import os
import stat
from ctypes import wintypes
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .audit_packages import (
    AUDIT_PACKAGE_VERIFICATION_CONTRACT,
    portable_canonical_hash,
    portable_canonical_json,
    validate_audit_package_payload,
)
from .audit_views import PASS
from .models import to_primitive


AUDIT_CATALOG_CONTRACT = "SBC_AUDIT_PACKAGE_CATALOG_V1"
AUDIT_CATALOG_SCHEMA_VERSION = 1
AUDIT_CATALOG_POLICY = "SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1"
AUDIT_CATALOG_SIGNATURE_CONTRACT = "SBC_AUDIT_CATALOG_SIGNATURE_V1"
AUDIT_CATALOG_BUNDLE_CONTRACT = "SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1"
AUDIT_CATALOG_BUNDLE_POLICY = "SIGNED_PORTABLE_RESEARCH_EXCHANGE_V1"
AUDIT_CATALOG_VERIFICATION_CONTRACT = "SBC_AUDIT_CATALOG_VERIFICATION_V1"
ED25519_ALGORITHM = "ED25519"
NOT_PERFORMED = "NOT_PERFORMED"
FAIL = "FAIL"

CATALOG_TOP_LEVEL_KEYS = {
    "contract",
    "schema_version",
    "catalog_policy",
    "classification",
    "catalog_id",
    "created_at_utc",
    "entries",
    "validation_gates",
    "guardrails",
}
CATALOG_ENTRY_KEYS = {
    "entry_id",
    "package_id",
    "package_digest",
    "source_audit_id",
    "instrument_identity",
    "sealed_at_utc",
    "p4_replay_state",
    "package",
}
CATALOG_VALIDATION_GATE_KEYS = {
    "gate_id",
    "state",
    "label",
    "detail",
}
CATALOG_GUARDRAIL_KEYS = {
    "research_only",
    "read_only",
    "timestamp_safe",
    "no_lookahead",
    "source_profiled_experimental",
    "financially_validated",
    "catalog_only",
    "embedded_p4_replay_required",
    "no_cross_package_arithmetic",
    "no_cross_package_voting",
    "no_market_direction",
    "no_confidence_output",
    "signatures_prove_integrity_only",
    "counts_as_independent_vote",
    "directional_contribution",
    "execution_allowed",
    "blocked_capabilities",
}
SIGNATURE_KEYS = {
    "contract",
    "schema_version",
    "algorithm",
    "key_id",
    "public_key_base64",
    "catalog_id",
    "catalog_digest",
    "signed_at_utc",
    "signature_base64",
}
BUNDLE_KEYS = {
    "contract",
    "schema_version",
    "bundle_policy",
    "catalog",
    "signature",
}


def _required_text(value: Any, label: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def _sha256(value: Any, label: str) -> str:
    normalized = _required_text(value, label).upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _utc(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _parse_utc(value: Any, label: str) -> datetime:
    text = _required_text(value, label).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO timestamp") from exc
    return _utc(parsed, label)


def _b64decode(value: Any, label: str, expected_length: int | None = None) -> bytes:
    text = _required_text(value, label)
    try:
        decoded = base64.b64decode(text, validate=True)
    except ValueError as exc:
        raise ValueError(f"{label} must be valid base64") from exc
    if expected_length is not None and len(decoded) != expected_length:
        raise ValueError(f"{label} must decode to {expected_length} bytes")
    return decoded


@dataclass(frozen=True)
class SbcAuditCatalogGuardrails:
    research_only: bool = True
    read_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    source_profiled_experimental: bool = True
    financially_validated: bool = False
    catalog_only: bool = True
    embedded_p4_replay_required: bool = True
    no_cross_package_arithmetic: bool = True
    no_cross_package_voting: bool = True
    no_market_direction: bool = True
    no_confidence_output: bool = True
    signatures_prove_integrity_only: bool = True
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    execution_allowed: bool = False
    blocked_capabilities: tuple[str, ...] = (
        "CROSS_AUDIT_ARITHMETIC",
        "CROSS_PACKAGE_VOTING",
        "FX_SUBTRACTION",
        "PHASE_OUTPUT",
        "CONFIDENCE_OUTPUT",
        "MARKET_DIRECTION",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VALIDATION_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    )


@dataclass(frozen=True)
class SbcAuditCatalogValidationGate:
    gate_id: str
    state: str
    label: str
    detail: str


@dataclass(frozen=True)
class SbcAuditCatalogEntry:
    entry_id: str
    package_id: str
    package_digest: str
    source_audit_id: str
    instrument_identity: str
    sealed_at_utc: datetime
    p4_replay_state: str
    package: dict[str, Any]


@dataclass(frozen=True)
class SbcAuditPackageCatalog:
    contract: str
    schema_version: int
    catalog_policy: str
    classification: str
    catalog_id: str
    created_at_utc: datetime
    entries: tuple[SbcAuditCatalogEntry, ...]
    validation_gates: tuple[SbcAuditCatalogValidationGate, ...]
    guardrails: SbcAuditCatalogGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAuditCatalogSignature:
    contract: str
    schema_version: int
    algorithm: str
    key_id: str
    public_key_base64: str
    catalog_id: str
    catalog_digest: str
    signed_at_utc: datetime
    signature_base64: str

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcSignedAuditCatalogBundle:
    contract: str
    schema_version: int
    bundle_policy: str
    catalog: SbcAuditPackageCatalog
    signature: SbcAuditCatalogSignature

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAuditCatalogEntryVerification:
    package_id: str
    structural_integrity: str
    semantic_replay: str
    errors: tuple[str, ...]


@dataclass(frozen=True)
class SbcAuditCatalogVerification:
    contract: str
    state: str
    catalog_id: str | None
    key_id: str | None
    catalog_hash_match: bool
    signature_valid: bool
    embedded_packages_valid: bool
    semantic_replay_state: str
    entry_count: int
    entry_verifications: tuple[SbcAuditCatalogEntryVerification, ...]
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


class SbcAuditPackageCatalogCompiler:
    def compile(
        self,
        packages: Sequence[Mapping[str, Any]],
        *,
        replay_verifications: Mapping[str, Mapping[str, Any]],
        created_at_utc: datetime,
    ) -> SbcAuditPackageCatalog:
        if not packages:
            raise ValueError("P5 requires at least one sealed P4 package")

        entries: list[SbcAuditCatalogEntry] = []
        seen: set[str] = set()
        for payload in packages:
            package = dict(payload)
            validate_audit_package_payload(package)
            package_id = _sha256(package["package_id"], "package_id")
            if package_id in seen:
                raise ValueError("P5 catalog package IDs must be unique")
            seen.add(package_id)

            verification = replay_verifications.get(package_id)
            if not isinstance(verification, Mapping):
                raise ValueError(f"P4 replay verification is missing for {package_id}")
            if (
                verification.get("contract") != AUDIT_PACKAGE_VERIFICATION_CONTRACT
                or verification.get("state") != PASS
                or verification.get("package_id") != package_id
                or verification.get("source_audit_id") != package["source_audit_id"]
                or not all(
                    verification.get(key) is True
                    for key in (
                        "structural_hash_match",
                        "source_projection_match",
                        "replay_recipe_match",
                        "replay_audit_match",
                        "replay_package_match",
                    )
                )
                or verification.get("errors")
            ):
                raise ValueError(
                    f"P5 only accepts fully replay-verified P4 packages: {package_id}"
                )

            package_digest = portable_canonical_hash(package)
            entry_identity = {
                "package_id": package_id,
                "package_digest": package_digest,
                "source_audit_id": package["source_audit_id"],
                "instrument_identity": package["instrument_identity"],
                "sealed_at_utc": package["sealed_at_utc"],
                "p4_replay_state": PASS,
                "package": package,
            }
            entries.append(
                SbcAuditCatalogEntry(
                    entry_id=portable_canonical_hash(entry_identity),
                    package_id=package_id,
                    package_digest=package_digest,
                    source_audit_id=package["source_audit_id"],
                    instrument_identity=package["instrument_identity"],
                    sealed_at_utc=_parse_utc(
                        package["sealed_at_utc"],
                        "package.sealed_at_utc",
                    ),
                    p4_replay_state=PASS,
                    package=package,
                )
            )

        ordered_entries = tuple(sorted(entries, key=lambda item: item.package_id))
        created_at = _utc(created_at_utc, "created_at_utc")
        guardrails = SbcAuditCatalogGuardrails()
        gates = (
            SbcAuditCatalogValidationGate(
                "EMBEDDED_P4_REPLAY",
                PASS,
                "Embedded P4 replay",
                f"{len(ordered_entries)} sealed package(s) passed full P4 replay before inclusion.",
            ),
            SbcAuditCatalogValidationGate(
                "PORTABLE_INTEGRITY",
                PASS,
                "Portable integrity",
                "Every embedded package and catalog entry has a portable SHA-256 identity.",
            ),
            SbcAuditCatalogValidationGate(
                "CROSS_PACKAGE_INFERENCE",
                "UNKNOWN",
                "Cross-package inference",
                "No arithmetic, voting, confidence, market direction, or trade inference is permitted.",
            ),
            SbcAuditCatalogValidationGate(
                "FINANCIAL_VALIDATION",
                "UNKNOWN",
                "Financial validation",
                "Catalog membership and signatures do not establish prospective financial validity.",
            ),
            SbcAuditCatalogValidationGate(
                "EXECUTION_LOCK",
                PASS,
                "Execution lock",
                "Auto Suggest, live inference, trade output, and MT5 execution remain blocked.",
            ),
        )
        identity = {
            "contract": AUDIT_CATALOG_CONTRACT,
            "schema_version": AUDIT_CATALOG_SCHEMA_VERSION,
            "catalog_policy": AUDIT_CATALOG_POLICY,
            "classification": RESEARCH_CLASSIFICATION,
            "created_at_utc": created_at.isoformat(),
            "entries": to_primitive(ordered_entries),
            "validation_gates": to_primitive(gates),
            "guardrails": to_primitive(guardrails),
        }
        return SbcAuditPackageCatalog(
            contract=AUDIT_CATALOG_CONTRACT,
            schema_version=AUDIT_CATALOG_SCHEMA_VERSION,
            catalog_policy=AUDIT_CATALOG_POLICY,
            classification=RESEARCH_CLASSIFICATION,
            catalog_id=portable_canonical_hash(identity),
            created_at_utc=created_at,
            entries=ordered_entries,
            validation_gates=gates,
            guardrails=guardrails,
        )


def _guardrails_are_locked(guardrails: Any) -> bool:
    expected_blocked = list(SbcAuditCatalogGuardrails().blocked_capabilities)
    return isinstance(guardrails, dict) and set(guardrails) == CATALOG_GUARDRAIL_KEYS and (
        guardrails.get("research_only") is True
        and guardrails.get("read_only") is True
        and guardrails.get("timestamp_safe") is True
        and guardrails.get("no_lookahead") is True
        and guardrails.get("source_profiled_experimental") is True
        and guardrails.get("financially_validated") is False
        and guardrails.get("catalog_only") is True
        and guardrails.get("embedded_p4_replay_required") is True
        and guardrails.get("no_cross_package_arithmetic") is True
        and guardrails.get("no_cross_package_voting") is True
        and guardrails.get("no_market_direction") is True
        and guardrails.get("no_confidence_output") is True
        and guardrails.get("signatures_prove_integrity_only") is True
        and guardrails.get("counts_as_independent_vote") is False
        and float(guardrails.get("directional_contribution", 1.0)) == 0.0
        and guardrails.get("execution_allowed") is False
        and guardrails.get("blocked_capabilities") == expected_blocked
    )


def validate_audit_catalog_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValueError("audit catalog must be an object")
    if set(payload) != CATALOG_TOP_LEVEL_KEYS:
        raise ValueError("audit catalog fields do not match the canonical P5 contract")
    if payload["contract"] != AUDIT_CATALOG_CONTRACT:
        raise ValueError("unsupported audit catalog contract")
    if payload["schema_version"] != AUDIT_CATALOG_SCHEMA_VERSION:
        raise ValueError("unsupported audit catalog schema version")
    if payload["catalog_policy"] != AUDIT_CATALOG_POLICY:
        raise ValueError("unsupported audit catalog policy")
    if payload["classification"] != RESEARCH_CLASSIFICATION:
        raise ValueError("audit catalog classification must remain experimental")

    catalog_id = _sha256(payload["catalog_id"], "catalog_id")
    identity = {
        key: payload[key] for key in CATALOG_TOP_LEVEL_KEYS if key != "catalog_id"
    }
    if portable_canonical_hash(identity) != catalog_id:
        raise ValueError("audit catalog hash does not match its contents")
    _parse_utc(payload["created_at_utc"], "created_at_utc")
    if not _guardrails_are_locked(payload.get("guardrails")):
        raise ValueError("audit catalog guardrails are weakened")
    validation_gates = payload.get("validation_gates")
    if not isinstance(validation_gates, list):
        raise ValueError("audit catalog validation_gates must be an array")
    gate_ids: set[str] = set()
    for gate in validation_gates:
        if not isinstance(gate, dict) or set(gate) != CATALOG_VALIDATION_GATE_KEYS:
            raise ValueError("audit catalog validation gate fields are invalid")
        gate_id = _required_text(gate["gate_id"], "validation gate ID")
        if gate_id in gate_ids:
            raise ValueError("audit catalog validation gate IDs must be unique")
        gate_ids.add(gate_id)
        if gate["state"] not in {PASS, "UNKNOWN"}:
            raise ValueError("audit catalog validation gate state is invalid")
        _required_text(gate["label"], "validation gate label")
        _required_text(gate["detail"], "validation gate detail")
    if gate_ids != {
        "EMBEDDED_P4_REPLAY",
        "PORTABLE_INTEGRITY",
        "CROSS_PACKAGE_INFERENCE",
        "FINANCIAL_VALIDATION",
        "EXECUTION_LOCK",
    }:
        raise ValueError("audit catalog validation gates are incomplete")

    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("audit catalog requires at least one entry")
    if entries != sorted(entries, key=lambda item: item.get("package_id", "")):
        raise ValueError("audit catalog entries must be sorted by package_id")
    seen_packages: set[str] = set()
    seen_entries: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != CATALOG_ENTRY_KEYS:
            raise ValueError("audit catalog entry fields do not match the P5 contract")
        package_id = _sha256(entry["package_id"], "entry.package_id")
        entry_id = _sha256(entry["entry_id"], "entry.entry_id")
        if package_id in seen_packages or entry_id in seen_entries:
            raise ValueError("audit catalog entry identities must be unique")
        seen_packages.add(package_id)
        seen_entries.add(entry_id)
        validate_audit_package_payload(entry["package"])
        if entry["package"]["package_id"] != package_id:
            raise ValueError("catalog entry package_id does not match embedded P4")
        if portable_canonical_hash(entry["package"]) != _sha256(
            entry["package_digest"],
            "entry.package_digest",
        ):
            raise ValueError("catalog entry package digest does not match embedded P4")
        if entry["source_audit_id"] != entry["package"]["source_audit_id"]:
            raise ValueError("catalog entry source audit does not match embedded P4")
        if entry["instrument_identity"] != entry["package"]["instrument_identity"]:
            raise ValueError("catalog entry instrument does not match embedded P4")
        if entry["sealed_at_utc"] != entry["package"]["sealed_at_utc"]:
            raise ValueError("catalog entry sealed time does not match embedded P4")
        if entry["p4_replay_state"] != PASS:
            raise ValueError("catalog entry must record a PASS P4 replay")
        entry_identity = {
            key: entry[key] for key in CATALOG_ENTRY_KEYS if key != "entry_id"
        }
        if portable_canonical_hash(entry_identity) != entry_id:
            raise ValueError("audit catalog entry hash does not match its contents")


def sign_audit_catalog(
    catalog: SbcAuditPackageCatalog | Mapping[str, Any],
    private_key: Ed25519PrivateKey,
    *,
    signed_at_utc: datetime,
) -> SbcSignedAuditCatalogBundle:
    catalog_payload = (
        catalog.to_dict()
        if isinstance(catalog, SbcAuditPackageCatalog)
        else dict(catalog)
    )
    validate_audit_catalog_payload(catalog_payload)
    message = portable_canonical_json(catalog_payload).encode("utf-8")
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    signature = private_key.sign(message)
    key_id = portable_canonical_hash(
        {"algorithm": ED25519_ALGORITHM, "public_key_base64": base64.b64encode(public_key).decode("ascii")}
    )
    signature_record = SbcAuditCatalogSignature(
        contract=AUDIT_CATALOG_SIGNATURE_CONTRACT,
        schema_version=AUDIT_CATALOG_SCHEMA_VERSION,
        algorithm=ED25519_ALGORITHM,
        key_id=key_id,
        public_key_base64=base64.b64encode(public_key).decode("ascii"),
        catalog_id=catalog_payload["catalog_id"],
        catalog_digest=portable_canonical_hash(catalog_payload),
        signed_at_utc=_utc(signed_at_utc, "signed_at_utc"),
        signature_base64=base64.b64encode(signature).decode("ascii"),
    )
    catalog_object = (
        catalog
        if isinstance(catalog, SbcAuditPackageCatalog)
        else _catalog_from_valid_payload(catalog_payload)
    )
    return SbcSignedAuditCatalogBundle(
        contract=AUDIT_CATALOG_BUNDLE_CONTRACT,
        schema_version=AUDIT_CATALOG_SCHEMA_VERSION,
        bundle_policy=AUDIT_CATALOG_BUNDLE_POLICY,
        catalog=catalog_object,
        signature=signature_record,
    )


def _catalog_from_valid_payload(payload: Mapping[str, Any]) -> SbcAuditPackageCatalog:
    validate_audit_catalog_payload(dict(payload))
    return SbcAuditPackageCatalog(
        contract=payload["contract"],
        schema_version=payload["schema_version"],
        catalog_policy=payload["catalog_policy"],
        classification=payload["classification"],
        catalog_id=payload["catalog_id"],
        created_at_utc=_parse_utc(payload["created_at_utc"], "created_at_utc"),
        entries=tuple(
            SbcAuditCatalogEntry(
                entry_id=item["entry_id"],
                package_id=item["package_id"],
                package_digest=item["package_digest"],
                source_audit_id=item["source_audit_id"],
                instrument_identity=item["instrument_identity"],
                sealed_at_utc=_parse_utc(item["sealed_at_utc"], "sealed_at_utc"),
                p4_replay_state=item["p4_replay_state"],
                package=item["package"],
            )
            for item in payload["entries"]
        ),
        validation_gates=tuple(
            SbcAuditCatalogValidationGate(
                gate_id=item["gate_id"],
                state=item["state"],
                label=item["label"],
                detail=item["detail"],
            )
            for item in payload["validation_gates"]
        ),
        guardrails=SbcAuditCatalogGuardrails(
            blocked_capabilities=tuple(
                payload["guardrails"]["blocked_capabilities"]
            )
        ),
    )


def verify_signed_audit_catalog(
    bundle: Any,
    *,
    replay_verifications: Mapping[str, Mapping[str, Any]] | None = None,
) -> SbcAuditCatalogVerification:
    errors: list[str] = []
    catalog_id: str | None = None
    key_id: str | None = None
    catalog_hash_match = False
    signature_valid = False
    embedded_packages_valid = False
    entry_results: list[SbcAuditCatalogEntryVerification] = []
    catalog_payload: dict[str, Any] | None = None

    try:
        if not isinstance(bundle, dict) or set(bundle) != BUNDLE_KEYS:
            raise ValueError("signed bundle fields do not match the P5 contract")
        if bundle["contract"] != AUDIT_CATALOG_BUNDLE_CONTRACT:
            raise ValueError("unsupported signed audit catalog bundle contract")
        if bundle["schema_version"] != AUDIT_CATALOG_SCHEMA_VERSION:
            raise ValueError("unsupported signed audit catalog schema version")
        if bundle["bundle_policy"] != AUDIT_CATALOG_BUNDLE_POLICY:
            raise ValueError("unsupported signed audit catalog bundle policy")
        catalog_payload = bundle["catalog"]
        validate_audit_catalog_payload(catalog_payload)
        catalog_id = catalog_payload["catalog_id"]
        embedded_packages_valid = True

        signature = bundle["signature"]
        if not isinstance(signature, dict) or set(signature) != SIGNATURE_KEYS:
            raise ValueError("catalog signature fields do not match the P5 contract")
        if signature["contract"] != AUDIT_CATALOG_SIGNATURE_CONTRACT:
            raise ValueError("unsupported catalog signature contract")
        if signature["schema_version"] != AUDIT_CATALOG_SCHEMA_VERSION:
            raise ValueError("unsupported catalog signature schema version")
        if signature["algorithm"] != ED25519_ALGORITHM:
            raise ValueError("unsupported catalog signature algorithm")
        if signature["catalog_id"] != catalog_id:
            raise ValueError("signature catalog_id does not match the catalog")
        key_id = _sha256(signature["key_id"], "signature.key_id")
        public_key_bytes = _b64decode(
            signature["public_key_base64"],
            "signature.public_key_base64",
            32,
        )
        expected_key_id = portable_canonical_hash(
            {
                "algorithm": ED25519_ALGORITHM,
                "public_key_base64": signature["public_key_base64"],
            }
        )
        if key_id != expected_key_id:
            raise ValueError("signature key_id does not match its public key")
        expected_catalog_digest = portable_canonical_hash(catalog_payload)
        catalog_hash_match = (
            _sha256(signature["catalog_digest"], "signature.catalog_digest")
            == expected_catalog_digest
        )
        if not catalog_hash_match:
            raise ValueError("signature catalog digest does not match the catalog")
        _parse_utc(signature["signed_at_utc"], "signature.signed_at_utc")
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
            _b64decode(
                signature["signature_base64"],
                "signature.signature_base64",
                64,
            ),
            portable_canonical_json(catalog_payload).encode("utf-8"),
        )
        signature_valid = True
    except (InvalidSignature, KeyError, TypeError, ValueError) as exc:
        errors.append(
            "Ed25519 signature is invalid"
            if isinstance(exc, InvalidSignature)
            else str(exc)
        )

    semantic_state = NOT_PERFORMED
    if catalog_payload is not None:
        for entry in catalog_payload.get("entries", ()):
            package_id = str(entry.get("package_id") or "")
            item_errors: list[str] = []
            structural_state = PASS
            try:
                validate_audit_package_payload(entry.get("package"))
            except (TypeError, ValueError) as exc:
                structural_state = FAIL
                item_errors.append(str(exc))
            replay_state = NOT_PERFORMED
            if replay_verifications is not None:
                verification = replay_verifications.get(package_id)
                if (
                    isinstance(verification, Mapping)
                    and verification.get("state") == PASS
                    and verification.get("package_id") == package_id
                    and all(
                        verification.get(key) is True
                        for key in (
                            "structural_hash_match",
                            "source_projection_match",
                            "replay_recipe_match",
                            "replay_audit_match",
                            "replay_package_match",
                        )
                    )
                    and not verification.get("errors")
                ):
                    replay_state = PASS
                else:
                    replay_state = FAIL
                    item_errors.append("full P4 semantic replay did not pass")
            entry_results.append(
                SbcAuditCatalogEntryVerification(
                    package_id=package_id,
                    structural_integrity=structural_state,
                    semantic_replay=replay_state,
                    errors=tuple(item_errors),
                )
            )
        if replay_verifications is not None:
            semantic_state = (
                PASS
                if entry_results
                and all(item.semantic_replay == PASS for item in entry_results)
                else FAIL
            )
            if semantic_state == FAIL:
                errors.append("one or more embedded P4 semantic replays failed")

    return SbcAuditCatalogVerification(
        contract=AUDIT_CATALOG_VERIFICATION_CONTRACT,
        state=PASS if not errors else FAIL,
        catalog_id=catalog_id,
        key_id=key_id,
        catalog_hash_match=catalog_hash_match,
        signature_valid=signature_valid,
        embedded_packages_valid=embedded_packages_valid,
        semantic_replay_state=semantic_state,
        entry_count=len(entry_results),
        entry_verifications=tuple(entry_results),
        errors=tuple(errors),
    )


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
    ]


def _blob(value: bytes) -> tuple[_DataBlob, Any]:
    buffer = ctypes.create_string_buffer(value)
    return (
        _DataBlob(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))),
        buffer,
    )


def _dpapi_transform(value: bytes, *, protect: bool) -> bytes:
    if os.name != "nt":
        return value
    input_blob, input_buffer = _blob(value)
    output_blob = _DataBlob()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    if protect:
        ok = crypt32.CryptProtectData(
            ctypes.byref(input_blob),
            "Gann Astro SBC audit catalog signing key",
            None,
            None,
            None,
            0,
            ctypes.byref(output_blob),
        )
    else:
        ok = crypt32.CryptUnprotectData(
            ctypes.byref(input_blob),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(output_blob),
        )
    if not ok:
        raise OSError(ctypes.get_last_error(), "Windows DPAPI operation failed")
    try:
        # Keep the input buffer alive until the Windows call has completed.
        del input_buffer
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(output_blob.pbData)


def load_or_create_signing_key(path: Path) -> Ed25519PrivateKey:
    resolved = Path(path).resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    if resolved.exists():
        private_bytes = _dpapi_transform(resolved.read_bytes(), protect=False)
        return Ed25519PrivateKey.from_private_bytes(private_bytes)

    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    protected = _dpapi_transform(private_bytes, protect=True)
    temporary = resolved.with_suffix(f"{resolved.suffix}.tmp")
    temporary.write_bytes(protected)
    try:
        os.chmod(temporary, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    os.replace(temporary, resolved)
    return private_key
