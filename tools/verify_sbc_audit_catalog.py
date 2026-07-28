"""Standalone integrity verifier for signed SBC P5 audit catalogs.

This tool intentionally does not import the application SBC implementation.
It verifies portable hashes, embedded P4 structural identities, and the
Ed25519 signature. It cannot replay ephemeris, Chakra, P1-P4 semantics, or
establish astrological/financial validity.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


BUNDLE_CONTRACT = "SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1"
BUNDLE_POLICY = "SIGNED_PORTABLE_RESEARCH_EXCHANGE_V1"
CATALOG_CONTRACT = "SBC_AUDIT_PACKAGE_CATALOG_V1"
CATALOG_POLICY = "SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1"
SIGNATURE_CONTRACT = "SBC_AUDIT_CATALOG_SIGNATURE_V1"
P4_CONTRACT = "SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1"
P4_POLICY = "READ_ONLY_COMPARISON_EXPORT_REPLAY_V1"
CLASSIFICATION = "SOURCE_PROFILED_EXPERIMENTAL"
ALGORITHM = "ED25519"
SCHEMA_VERSION = 1
PASS = "PASS"
FAIL = "FAIL"
NOT_PERFORMED = "NOT_PERFORMED"

BUNDLE_KEYS = {
    "contract",
    "schema_version",
    "bundle_policy",
    "catalog",
    "signature",
}
CATALOG_KEYS = {
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
EXPECTED_BLOCKED_CAPABILITIES = [
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
]
ENTRY_KEYS = {
    "entry_id",
    "package_id",
    "package_digest",
    "source_audit_id",
    "instrument_identity",
    "sealed_at_utc",
    "p4_replay_state",
    "package",
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
P4_KEYS = {
    "contract",
    "schema_version",
    "package_policy",
    "classification",
    "package_id",
    "source_audit_id",
    "source_projection_hash",
    "instrument_identity",
    "sealed_at_utc",
    "replay_recipe_hash",
    "replay_recipe",
    "source_audit",
    "comparisons",
    "bookmarks",
    "validation_gates",
    "guardrails",
}


def portable_value(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("catalog contains a non-finite number")
        if value == 0.0:
            return 0
        if value.is_integer():
            return int(value)
        return value
    if isinstance(value, Mapping):
        return {key: portable_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable_value(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        portable_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest().upper()


def required_digest(value: Any, label: str) -> str:
    text = str(value or "").strip().upper()
    if len(text) != 64 or any(character not in "0123456789ABCDEF" for character in text):
        raise ValueError(f"{label} is not an uppercase SHA-256 digest")
    return text


def decode_base64(value: Any, label: str, length: int) -> bytes:
    try:
        decoded = base64.b64decode(str(value or ""), validate=True)
    except ValueError as exc:
        raise ValueError(f"{label} is not valid base64") from exc
    if len(decoded) != length:
        raise ValueError(f"{label} must decode to {length} bytes")
    return decoded


def locked_catalog_guardrails(value: Any) -> bool:
    return isinstance(value, dict) and set(value) == CATALOG_GUARDRAIL_KEYS and (
        value.get("research_only") is True
        and value.get("read_only") is True
        and value.get("timestamp_safe") is True
        and value.get("no_lookahead") is True
        and value.get("source_profiled_experimental") is True
        and value.get("financially_validated") is False
        and value.get("catalog_only") is True
        and value.get("embedded_p4_replay_required") is True
        and value.get("no_cross_package_arithmetic") is True
        and value.get("no_cross_package_voting") is True
        and value.get("no_market_direction") is True
        and value.get("no_confidence_output") is True
        and value.get("signatures_prove_integrity_only") is True
        and value.get("counts_as_independent_vote") is False
        and float(value.get("directional_contribution", 1)) == 0
        and value.get("execution_allowed") is False
        and value.get("blocked_capabilities") == EXPECTED_BLOCKED_CAPABILITIES
    )


def validate_p4(package: Any) -> None:
    if not isinstance(package, dict) or set(package) != P4_KEYS:
        raise ValueError("embedded P4 fields do not match the canonical contract")
    if (
        package["contract"] != P4_CONTRACT
        or package["schema_version"] != SCHEMA_VERSION
        or package["package_policy"] != P4_POLICY
        or package["classification"] != CLASSIFICATION
    ):
        raise ValueError("embedded package is not canonical P4")
    identity = {key: package[key] for key in P4_KEYS if key != "package_id"}
    if digest(identity) != required_digest(package["package_id"], "P4 package_id"):
        raise ValueError("embedded P4 package hash does not match")
    if digest(package["replay_recipe"]) != required_digest(
        package["replay_recipe_hash"],
        "P4 replay_recipe_hash",
    ):
        raise ValueError("embedded P4 replay recipe hash does not match")
    if digest(package["source_audit"]) != required_digest(
        package["source_projection_hash"],
        "P4 source_projection_hash",
    ):
        raise ValueError("embedded P4 source projection hash does not match")
    guardrails = package.get("guardrails")
    if not isinstance(guardrails, dict) or not (
        guardrails.get("research_only") is True
        and guardrails.get("read_only") is True
        and guardrails.get("timestamp_safe") is True
        and guardrails.get("no_lookahead") is True
        and guardrails.get("financially_validated") is False
        and guardrails.get("counts_as_independent_vote") is False
        and float(guardrails.get("directional_contribution", 1)) == 0
        and guardrails.get("execution_allowed") is False
    ):
        raise ValueError("embedded P4 guardrails are weakened")


def verify(bundle: Any) -> dict[str, Any]:
    errors: list[str] = []
    catalog_id = None
    key_id = None
    signature_valid = False
    catalog_hash_match = False
    embedded_packages_valid = False
    entry_count = 0
    try:
        if not isinstance(bundle, dict) or set(bundle) != BUNDLE_KEYS:
            raise ValueError("bundle fields do not match the P5 contract")
        if (
            bundle["contract"] != BUNDLE_CONTRACT
            or bundle["schema_version"] != SCHEMA_VERSION
            or bundle["bundle_policy"] != BUNDLE_POLICY
        ):
            raise ValueError("unsupported signed audit catalog bundle")

        catalog = bundle["catalog"]
        if not isinstance(catalog, dict) or set(catalog) != CATALOG_KEYS:
            raise ValueError("catalog fields do not match the P5 contract")
        if (
            catalog["contract"] != CATALOG_CONTRACT
            or catalog["schema_version"] != SCHEMA_VERSION
            or catalog["catalog_policy"] != CATALOG_POLICY
            or catalog["classification"] != CLASSIFICATION
        ):
            raise ValueError("unsupported audit catalog")
        catalog_id = required_digest(catalog["catalog_id"], "catalog_id")
        catalog_identity = {
            key: catalog[key] for key in CATALOG_KEYS if key != "catalog_id"
        }
        if digest(catalog_identity) != catalog_id:
            raise ValueError("catalog hash does not match")
        if not locked_catalog_guardrails(catalog.get("guardrails")):
            raise ValueError("catalog guardrails are weakened")

        entries = catalog.get("entries")
        if not isinstance(entries, list) or not entries:
            raise ValueError("catalog has no entries")
        if entries != sorted(entries, key=lambda item: item.get("package_id", "")):
            raise ValueError("catalog entries are not sorted")
        entry_count = len(entries)
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
                raise ValueError("catalog entry fields do not match the P5 contract")
            package_id = required_digest(entry["package_id"], "entry package_id")
            if package_id in seen:
                raise ValueError("catalog contains a duplicate package")
            seen.add(package_id)
            validate_p4(entry["package"])
            if entry["package"]["package_id"] != package_id:
                raise ValueError("entry package_id does not match embedded P4")
            if digest(entry["package"]) != required_digest(
                entry["package_digest"],
                "entry package_digest",
            ):
                raise ValueError("entry package digest does not match")
            entry_identity = {
                key: entry[key] for key in ENTRY_KEYS if key != "entry_id"
            }
            if digest(entry_identity) != required_digest(
                entry["entry_id"],
                "entry_id",
            ):
                raise ValueError("entry hash does not match")
            if entry["p4_replay_state"] != PASS:
                raise ValueError("entry does not record a P4 replay PASS")
        embedded_packages_valid = True

        signature = bundle["signature"]
        if not isinstance(signature, dict) or set(signature) != SIGNATURE_KEYS:
            raise ValueError("signature fields do not match the P5 contract")
        if (
            signature["contract"] != SIGNATURE_CONTRACT
            or signature["schema_version"] != SCHEMA_VERSION
            or signature["algorithm"] != ALGORITHM
        ):
            raise ValueError("unsupported catalog signature")
        if signature["catalog_id"] != catalog_id:
            raise ValueError("signature catalog_id does not match")
        public_key = decode_base64(
            signature["public_key_base64"],
            "public key",
            32,
        )
        key_id = required_digest(signature["key_id"], "key_id")
        expected_key_id = digest(
            {
                "algorithm": ALGORITHM,
                "public_key_base64": signature["public_key_base64"],
            }
        )
        if key_id != expected_key_id:
            raise ValueError("key_id does not match the public key")
        catalog_hash_match = (
            digest(catalog)
            == required_digest(signature["catalog_digest"], "catalog_digest")
        )
        if not catalog_hash_match:
            raise ValueError("signature catalog digest does not match")
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            decode_base64(signature["signature_base64"], "signature", 64),
            canonical_json(catalog).encode("utf-8"),
        )
        signature_valid = True
    except (InvalidSignature, KeyError, TypeError, ValueError) as exc:
        errors.append(
            "Ed25519 signature is invalid"
            if isinstance(exc, InvalidSignature)
            else str(exc)
        )

    return {
        "contract": "SBC_INDEPENDENT_AUDIT_CATALOG_CHECK_V1",
        "state": PASS if not errors else FAIL,
        "catalog_id": catalog_id,
        "key_id": key_id,
        "catalog_hash_match": catalog_hash_match,
        "signature_valid": signature_valid,
        "embedded_packages_valid": embedded_packages_valid,
        "semantic_replay_state": NOT_PERFORMED,
        "entry_count": entry_count,
        "errors": errors,
        "scope": (
            "Independent portable-hash and Ed25519 integrity check only. "
            "P1-P4 semantic replay, doctrine correctness, and financial validity "
            "were not performed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a signed SBC P5 audit catalog without the app runtime.",
    )
    parser.add_argument("bundle", type=Path, help="Path to the signed JSON bundle")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable verification JSON",
    )
    args = parser.parse_args()
    try:
        payload = json.loads(args.bundle.read_text(encoding="utf-8"))
        result = verify(payload)
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "contract": "SBC_INDEPENDENT_AUDIT_CATALOG_CHECK_V1",
            "state": FAIL,
            "semantic_replay_state": NOT_PERFORMED,
            "errors": [str(exc)],
        }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Integrity: {result['state']}")
        print(f"Semantic replay: {result['semantic_replay_state']}")
        for error in result.get("errors", ()):
            print(f"ERROR: {error}")
        print(result.get("scope", ""))
    return 0 if result["state"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
