from __future__ import annotations

import copy
import json
import subprocess
import sys
from datetime import timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from sbc.audit_catalog import (
    AUDIT_CATALOG_BUNDLE_CONTRACT,
    AUDIT_CATALOG_CONTRACT,
    AUDIT_CATALOG_POLICY,
    NOT_PERFORMED,
    SbcAuditPackageCatalogCompiler,
    load_or_create_signing_key,
    sign_audit_catalog,
    validate_audit_catalog_payload,
    verify_signed_audit_catalog,
)
from sbc.audit_packages import (
    SbcAuditComparisonPackageCompiler,
    verify_audit_package_replay,
)
from test_sbc_phase5d_audit_packages import START, _audit, _compile_package


def _second_package():
    audit = _audit()
    return SbcAuditComparisonPackageCompiler().compile(
        audit,
        baseline_interval_id=audit.intervals[1].interval_id,
        comparison_interval_ids=(audit.intervals[2].interval_id,),
        bookmark_inputs=(),
        sealed_at_utc=START + timedelta(hours=6),
        replay_recipe={
            "audit_request": {"fixture": "second"},
            "baseline_interval_id": audit.intervals[1].interval_id,
            "comparison_interval_ids": [audit.intervals[2].interval_id],
            "bookmarks": [],
            "sealed_at_utc": (START + timedelta(hours=6)).isoformat(),
        },
    )


def _catalog():
    _, first = _compile_package()
    second = _second_package()
    packages = (second.to_dict(), first.to_dict())
    verifications = {
        package["package_id"]: verify_audit_package_replay(package, package).to_dict()
        for package in packages
    }
    catalog = SbcAuditPackageCatalogCompiler().compile(
        packages,
        replay_verifications=verifications,
        created_at_utc=START + timedelta(hours=7),
    )
    return catalog, verifications


def test_p5_catalog_is_stable_sorted_and_blocks_cross_package_inference() -> None:
    first, _ = _catalog()
    second, _ = _catalog()

    assert first.contract == AUDIT_CATALOG_CONTRACT
    assert first.catalog_policy == AUDIT_CATALOG_POLICY
    assert first.catalog_id == second.catalog_id
    assert first.to_dict() == second.to_dict()
    assert [item.package_id for item in first.entries] == sorted(
        item.package_id for item in first.entries
    )
    assert first.guardrails.no_cross_package_arithmetic is True
    assert first.guardrails.no_cross_package_voting is True
    assert first.guardrails.no_market_direction is True
    assert first.guardrails.no_confidence_output is True
    assert first.guardrails.execution_allowed is False
    validate_audit_catalog_payload(first.to_dict())


def test_p5_signed_bundle_separates_integrity_from_semantic_replay() -> None:
    catalog, verifications = _catalog()
    bundle = sign_audit_catalog(
        catalog,
        Ed25519PrivateKey.generate(),
        signed_at_utc=START + timedelta(hours=8),
    ).to_dict()

    assert bundle["contract"] == AUDIT_CATALOG_BUNDLE_CONTRACT
    independent = verify_signed_audit_catalog(bundle)
    assert independent.state == "PASS"
    assert independent.signature_valid is True
    assert independent.catalog_hash_match is True
    assert independent.embedded_packages_valid is True
    assert independent.semantic_replay_state == NOT_PERFORMED
    assert all(
        item.semantic_replay == NOT_PERFORMED
        for item in independent.entry_verifications
    )

    full = verify_signed_audit_catalog(
        bundle,
        replay_verifications=verifications,
    )
    assert full.state == "PASS"
    assert full.semantic_replay_state == "PASS"
    assert all(item.semantic_replay == "PASS" for item in full.entry_verifications)


def test_p5_rejects_duplicate_or_unverified_p4_membership() -> None:
    _, package = _compile_package()
    payload = package.to_dict()
    verification = verify_audit_package_replay(payload, payload).to_dict()
    compiler = SbcAuditPackageCatalogCompiler()

    with pytest.raises(ValueError, match="unique"):
        compiler.compile(
            (payload, payload),
            replay_verifications={payload["package_id"]: verification},
            created_at_utc=START,
        )

    failed = dict(verification)
    failed["state"] = "FAIL"
    with pytest.raises(ValueError, match="fully replay-verified"):
        compiler.compile(
            (payload,),
            replay_verifications={payload["package_id"]: failed},
            created_at_utc=START,
        )


def test_p5_tampering_breaks_structural_or_signature_integrity() -> None:
    catalog, _ = _catalog()
    bundle = sign_audit_catalog(
        catalog,
        Ed25519PrivateKey.generate(),
        signed_at_utc=START,
    ).to_dict()
    tampered = copy.deepcopy(bundle)
    tampered["catalog"]["entries"][0]["package"]["instrument_identity"] = "FX:TAMPERED"

    result = verify_signed_audit_catalog(tampered)
    assert result.state == "FAIL"
    assert result.signature_valid is False
    assert result.errors


def test_p5_machine_key_round_trip(tmp_path) -> None:
    path = tmp_path / "catalog-signing-key.dpapi"
    first = load_or_create_signing_key(path)
    second = load_or_create_signing_key(path)

    assert path.is_file()
    assert first.public_key().public_bytes_raw() == second.public_key().public_bytes_raw()


def test_p5_standalone_verifier_does_not_claim_semantic_replay(tmp_path) -> None:
    catalog, _ = _catalog()
    bundle = sign_audit_catalog(
        catalog,
        Ed25519PrivateKey.generate(),
        signed_at_utc=START,
    ).to_dict()
    bundle_path = tmp_path / "catalog.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "tools/verify_sbc_audit_catalog.py",
            str(bundle_path),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["state"] == "PASS"
    assert payload["signature_valid"] is True
    assert payload["embedded_packages_valid"] is True
    assert payload["semantic_replay_state"] == NOT_PERFORMED
