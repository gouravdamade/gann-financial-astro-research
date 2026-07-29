from __future__ import annotations

import copy
import unittest

from status.validate_status import (
    EXPECTED_CONTRACTS,
    STATUS_ROOT,
    _load,
    validate_all,
    validate_capabilities,
    validate_cross_document_links,
    validate_release,
    validate_sbc_atomic_intervals_p1_audit,
    validate_sbc_fixed_zero_pi_phasor_f3_audit,
    validate_sbc_linked_audit_views_p3_audit,
    validate_sbc_multidimensional_ledger_p2_audit,
    validate_sbc_phase_p0_audit,
    validate_sbc_reproducible_audit_packages_p4_audit,
    validate_sbc_signed_audit_catalogs_p5_audit,
    validate_sbc_timing_profile_admission_t0_audit,
    validate_timing_profile_registry,
)


class StatusValidationTests(unittest.TestCase):
    def test_canonical_documents_validate(self) -> None:
        result = validate_all()
        self.assertTrue(result["valid"])
        self.assertFalse(result["executionAllowed"])
        self.assertEqual(result["documentCount"], 14)
        self.assertEqual(result["auditCount"], 8)

    def test_release_cannot_promote_with_blockers(self) -> None:
        document = _load(STATUS_ROOT / "release_status.json")
        document["promotionAllowed"] = True
        with self.assertRaisesRegex(ValueError, "blockers"):
            validate_release(document)

    def test_capability_cannot_enable_execution(self) -> None:
        document = copy.deepcopy(_load(STATUS_ROOT / "capability_status.json"))
        document["capabilities"][0]["executionAllowed"] = True
        with self.assertRaisesRegex(ValueError, "enables execution"):
            validate_capabilities(document)

    def test_selected_candidate_metadata_must_match_release(self) -> None:
        documents = {
            filename: copy.deepcopy(_load(STATUS_ROOT / filename))
            for filename in EXPECTED_CONTRACTS
        }
        documents["mobile_acceptance_plan.json"]["mobileCandidate"][
            "sourceGitDirty"
        ] = True
        with self.assertRaisesRegex(ValueError, "sourceGitDirty differs"):
            validate_cross_document_links(documents, STATUS_ROOT)

    def test_sbc_phase_p0_audit_cannot_enable_runtime_behavior(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_phase_p0_gap_audit_20260728.json")
        )
        document["guardrails"]["runtimeBehaviorChanged"] = True
        with self.assertRaisesRegex(ValueError, "runtimeBehaviorChanged"):
            validate_sbc_phase_p0_audit(document, STATUS_ROOT.parent)

    def test_sbc_phase_p0_audit_requires_all_residual_corrections(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_phase_p0_gap_audit_20260728.json")
        )
        document["residualContractCorrections"].pop()
        with self.assertRaisesRegex(ValueError, "P0-R1 through P0-R8"):
            validate_sbc_phase_p0_audit(document, STATUS_ROOT.parent)

    def test_sbc_atomic_p1_audit_cannot_enable_phase_output(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_atomic_intervals_p1_20260728.json")
        )
        document["guardrails"]["phaseOutputIncluded"] = True
        with self.assertRaisesRegex(ValueError, "phaseOutputIncluded"):
            validate_sbc_atomic_intervals_p1_audit(document, STATUS_ROOT.parent)

    def test_sbc_atomic_p1_audit_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_atomic_intervals_p1_20260728.json")
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_atomic_intervals_p1_audit(document, STATUS_ROOT.parent)

    def test_sbc_multidimensional_p2_audit_cannot_count_as_vote(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_multidimensional_ledger_p2_20260728.json")
        )
        document["guardrails"]["countsAsIndependentVote"] = True
        with self.assertRaisesRegex(ValueError, "countsAsIndependentVote"):
            validate_sbc_multidimensional_ledger_p2_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_multidimensional_p2_audit_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_multidimensional_ledger_p2_20260728.json")
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_multidimensional_ledger_p2_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_multidimensional_p2_audit_preserves_exact_axes(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_multidimensional_ledger_p2_20260728.json")
        )
        document["implementation"]["ledgerAxes"].append("MARKET_DIRECTION")
        with self.assertRaisesRegex(ValueError, "ledger axes drifted"):
            validate_sbc_multidimensional_ledger_p2_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_linked_audit_p3_cannot_enable_phase_output(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_linked_audit_views_p3_20260728.json")
        )
        document["guardrails"]["phaseOutputIncluded"] = True
        with self.assertRaisesRegex(ValueError, "phaseOutputIncluded"):
            validate_sbc_linked_audit_views_p3_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_linked_audit_p3_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_linked_audit_views_p3_20260728.json")
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_linked_audit_views_p3_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_linked_audit_p3_preserves_exact_view_ids(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_linked_audit_views_p3_20260728.json")
        )
        document["implementation"]["viewIds"].append("MARKET_DIRECTION")
        with self.assertRaisesRegex(ValueError, "view IDs drifted"):
            validate_sbc_linked_audit_views_p3_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_reproducible_audit_p4_requires_replay(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT / "audits/sbc_reproducible_audit_packages_p4_20260728.json"
            )
        )
        document["guardrails"]["replayRequiredForVerification"] = False
        with self.assertRaisesRegex(ValueError, "replayRequiredForVerification"):
            validate_sbc_reproducible_audit_packages_p4_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_reproducible_audit_p4_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT / "audits/sbc_reproducible_audit_packages_p4_20260728.json"
            )
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_reproducible_audit_packages_p4_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_reproducible_audit_p4_cannot_enable_market_direction(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT / "audits/sbc_reproducible_audit_packages_p4_20260728.json"
            )
        )
        document["guardrails"]["marketDirectionIncluded"] = True
        with self.assertRaisesRegex(ValueError, "marketDirectionIncluded"):
            validate_sbc_reproducible_audit_packages_p4_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_signed_audit_p5_requires_embedded_p4_replay(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_signed_audit_catalogs_p5_20260728.json")
        )
        document["guardrails"]["embeddedP4ReplayRequired"] = False
        with self.assertRaisesRegex(ValueError, "embeddedP4ReplayRequired"):
            validate_sbc_signed_audit_catalogs_p5_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_signed_audit_p5_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_signed_audit_catalogs_p5_20260728.json")
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_signed_audit_catalogs_p5_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_signed_audit_p5_blocks_cross_package_arithmetic(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_signed_audit_catalogs_p5_20260728.json")
        )
        document["guardrails"]["noCrossPackageArithmetic"] = False
        with self.assertRaisesRegex(ValueError, "noCrossPackageArithmetic"):
            validate_sbc_signed_audit_catalogs_p5_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_fixed_phasor_f3_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_fixed_zero_pi_phasor_f3_20260729.json")
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_fixed_zero_pi_phasor_f3_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_fixed_phasor_f3_preserves_fixed_angle_domain(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_fixed_zero_pi_phasor_f3_20260729.json")
        )
        document["projection"]["negativeFixedAngle"] = "THREE_PI_OVER_TWO"
        with self.assertRaisesRegex(ValueError, "projection domain drifted"):
            validate_sbc_fixed_zero_pi_phasor_f3_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_fixed_phasor_f3_cannot_contribute_direction(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_fixed_zero_pi_phasor_f3_20260729.json")
        )
        document["guardrails"]["directionalContribution"] = 1
        with self.assertRaisesRegex(ValueError, "directional contribution"):
            validate_sbc_fixed_zero_pi_phasor_f3_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_timing_profile_registry_cannot_enable_execution(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "timing_phase_profile_registry.json")
        )
        document["executionAllowed"] = True
        with self.assertRaisesRegex(ValueError, "executionAllowed=false"):
            validate_timing_profile_registry(document)

    def test_sbc_timing_admission_t0_detects_module_hash_drift(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT
                / "audits/sbc_timing_profile_admission_t0_20260729.json"
            )
        )
        document["implementation"]["moduleCanonicalTextSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "module hash differs"):
            validate_sbc_timing_profile_admission_t0_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_timing_admission_t0_cannot_claim_directional_engine(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT
                / "audits/sbc_timing_profile_admission_t0_20260729.json"
            )
        )
        document["separation"]["directionalEngineImplemented"] = True
        with self.assertRaisesRegex(ValueError, "separation contract drifted"):
            validate_sbc_timing_profile_admission_t0_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_timing_admission_t0_rejects_registry_count_drift(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT
                / "audits/sbc_timing_profile_admission_t0_20260729.json"
            )
        )
        document["admission"]["repositoryProfileCount"] = 1
        with self.assertRaisesRegex(ValueError, "admission contract drifted"):
            validate_sbc_timing_profile_admission_t0_audit(
                document,
                STATUS_ROOT.parent,
            )

    def test_sbc_timing_admission_t0_preserves_blocked_capabilities(self) -> None:
        document = copy.deepcopy(
            _load(
                STATUS_ROOT
                / "audits/sbc_timing_profile_admission_t0_20260729.json"
            )
        )
        document["guardrails"]["blockedCapabilities"].remove("AUTO_SUGGEST")
        with self.assertRaisesRegex(ValueError, "blockedCapabilities drifted"):
            validate_sbc_timing_profile_admission_t0_audit(
                document,
                STATUS_ROOT.parent,
            )


if __name__ == "__main__":
    unittest.main()
