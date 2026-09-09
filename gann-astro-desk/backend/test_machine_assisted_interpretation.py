"""Synthetic-only tests for the MO-R4A-P0 interpretation boundary."""

from __future__ import annotations

import json
import os
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))
if str(INSTRUMENT_SBC_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUMENT_SBC_ROOT))

from chart_conditioned_aspects.polarity_catalogue import TargetAwarePolarityCatalogue  # noqa: E402
from chart_conditioned_aspects.polarity_evidence import TargetAwarePolarityEvidencePacketRegistry  # noqa: E402

import machine_assisted_interpretation as interpretation  # noqa: E402
import multi_oscillator_activity_service as activity  # noqa: E402


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class MachineAssistedInterpretationTests(unittest.TestCase):
    """Every decision-bearing example is synthetic and has no market data."""

    source_locator = interpretation.SourceLocator(
        source_id="SYNTHETIC_TEST_WITNESS",
        edition="Synthetic contract-only test witness",
        locator="synthetic:line-1",
    )

    def _event(self, side: str = "USD") -> dict[str, object]:
        return {
            "eventId": f"SYNTHETIC_{side}_EVENT_001",
            "sideIdentity": side,
            "synthetic": True,
        }

    def _evidence(
        self,
        *,
        contract_id: str = "SYNTHETIC_SOURCE_OPERATOR_A_V1",
        state: interpretation.AstrologyState = interpretation.AstrologyState.SUPPORTIVE_ASTRO_STATE,
        status: interpretation.SourceEvidenceStatus = interpretation.SourceEvidenceStatus.SOURCE_CLOSED,
        unresolved: tuple[str, ...] = (),
        measurements: tuple[interpretation.SourceMeasurement, ...] = (),
    ) -> interpretation.SourceOperatorEvidence:
        return interpretation.SourceOperatorEvidence(
            operator_contract_id=contract_id,
            source_status=status,
            astrological_state=state,
            locators=(self.source_locator,),
            rationale="Synthetic source operator used only to exercise the contract boundary.",
            unresolved_dependencies=unresolved,
            source_measurements=measurements,
        )

    def _hypothesis(
        self,
        *,
        contract_ids: tuple[str, ...] = ("SYNTHETIC_SOURCE_OPERATOR_A_V1",),
        astro_state: interpretation.AstrologyState = interpretation.AstrologyState.SUPPORTIVE_ASTRO_STATE,
        currency_state: interpretation.CurrencyPressureState = interpretation.CurrencyPressureState.SUPPORTIVE,
        version: str = "1.0.0",
        reasoning: str = "Synthetic blinded-test mapping used only by an isolated regression test.",
    ) -> interpretation.ExperimentalMarketHypothesis:
        return interpretation.ExperimentalMarketHypothesis(
            hypothesis_id="SYNTHETIC-H-MO-001",
            version=version,
            author="Synthetic test author",
            created_at_utc="2026-09-09T00:00:00Z",
            input_operator_contract_ids=contract_ids,
            astrological_state_condition=astro_state,
            target_side="USD",
            currency_pressure_state=currency_state,
            reasoning=reasoning,
            source_dependencies=("SYNTHETIC_SOURCE_OPERATOR_A_V1",),
            experimental_assumptions=("Synthetic test assumption only.",),
            prohibited_generalizations=("Does not apply to real events or other instruments.",),
            validation_status="NOT_FINANCIALLY_VALIDATED",
            outcome_data_seen_at_creation=False,
            approval_status=interpretation.HypothesisApprovalStatus.AUTHORIZED_FOR_BLINDED_TEST,
        )

    def _interpret(
        self,
        evidence: tuple[interpretation.SourceOperatorEvidence, ...],
        *,
        mode: interpretation.InterpretationMode = interpretation.InterpretationMode.EXPERIMENTAL_PROFILED,
        hypothesis: interpretation.ExperimentalMarketHypothesis | None = None,
    ) -> interpretation.MachineAssistedInterpretation:
        return interpretation.interpret_synthetic_event(
            self._event(),
            source_operator_evidence=evidence,
            mode=mode,
            experimental_market_hypothesis=hypothesis,
        )

    def _assert_unsigned(self, result: interpretation.MachineAssistedInterpretation) -> None:
        mapped = result.to_mapping()
        self.assertIsNone(result.currency_side_interpretation.signed_unit)
        self.assertIsNone(mapped["currencySideInterpretation"]["signedUnit"])
        self.assertEqual(result.currency_side_interpretation.magnitude_state, "MAGNITUDE_NOT_CONFIGURED")
        self.assertNotIn("pairResultant", mapped)
        self.assertNotIn("signedWave", mapped)
        self.assertEqual(mapped["provenance"]["inputScope"], "SYNTHETIC_TEST_ONLY")
        self.assertFalse(mapped["provenance"]["reviewStoreRead"])
        self.assertFalse(mapped["provenance"]["priceOrOutcomeRead"])
        self.assertFalse(mapped["provenance"]["executionAllowed"])
        self.assertFalse(mapped["executionAllowed"])

    def test_source_evidence_and_authorized_synthetic_bridge_can_produce_experimental_supportive(self) -> None:
        result = self._interpret((self._evidence(),), hypothesis=self._hypothesis())

        self.assertEqual(result.astrological_interpretation.state, interpretation.AstrologyState.SUPPORTIVE_ASTRO_STATE)
        self.assertEqual(result.market_bridge.status, interpretation.MarketBridgeStatus.EXPERIMENTAL_MARKET_HYPOTHESIS)
        self.assertEqual(result.currency_side_interpretation.state, interpretation.CurrencyPressureState.SUPPORTIVE)
        self.assertIn("Experimental supportive interpretation.", result.explanation.why)
        self._assert_unsigned(result)

    def test_source_evidence_and_authorized_synthetic_bridge_can_produce_experimental_adverse(self) -> None:
        evidence = self._evidence(state=interpretation.AstrologyState.ADVERSE_ASTRO_STATE)
        hypothesis = self._hypothesis(
            astro_state=interpretation.AstrologyState.ADVERSE_ASTRO_STATE,
            currency_state=interpretation.CurrencyPressureState.ADVERSE,
        )
        result = self._interpret((evidence,), hypothesis=hypothesis)

        self.assertEqual(result.currency_side_interpretation.state, interpretation.CurrencyPressureState.ADVERSE)
        self.assertIn(
            "Experimental adverse interpretation. Classical evidence supports the astrology condition; "
            "the currency mapping is experimental and not yet financially validated.",
            result.explanation.why,
        )
        self._assert_unsigned(result)

    def test_source_benefic_classification_alone_does_not_create_currency_supportive(self) -> None:
        evidence = self._evidence(contract_id="SYNTHETIC_BENEFIC_CLASSIFICATION_V1")
        result = self._interpret((evidence,))

        self.assertEqual(result.astrological_interpretation.state, interpretation.AstrologyState.SUPPORTIVE_ASTRO_STATE)
        self.assertEqual(result.market_bridge.status, interpretation.MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self.assertIn(
            "Direction unknown because the astrology is source-supported but no approved USD/JPY market bridge exists.",
            result.explanation.why,
        )
        self._assert_unsigned(result)

    def test_source_malefic_classification_alone_does_not_create_currency_adverse(self) -> None:
        evidence = self._evidence(
            contract_id="SYNTHETIC_MALEFIC_CLASSIFICATION_V1",
            state=interpretation.AstrologyState.ADVERSE_ASTRO_STATE,
        )
        result = self._interpret((evidence,))

        self.assertEqual(result.astrological_interpretation.state, interpretation.AstrologyState.ADVERSE_ASTRO_STATE)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self._assert_unsigned(result)

    def test_aspect_geometry_alone_does_not_create_a_sign(self) -> None:
        geometry = self._evidence(
            contract_id="SYNTHETIC_DRSTI_GEOMETRY_ONLY_V1",
            state=interpretation.AstrologyState.UNKNOWN_ASTRO_STATE,
        )
        result = self._interpret((geometry,))

        self.assertEqual(result.astrological_interpretation.state, interpretation.AstrologyState.UNKNOWN_ASTRO_STATE)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self.assertEqual(result.market_bridge.status, interpretation.MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE)
        self._assert_unsigned(result)

    def test_source_measurement_alone_does_not_create_magnitude_or_direction(self) -> None:
        measurement = interpretation.SourceMeasurement(
            component_id="SYNTHETIC_BALA_LITERAL",
            literal_value="synthetic literal only",
            locator=self.source_locator,
        )
        measurement_only = self._evidence(
            contract_id="SYNTHETIC_STRENGTH_RECORD_ONLY_V1",
            state=interpretation.AstrologyState.UNKNOWN_ASTRO_STATE,
            measurements=(measurement,),
        )
        result = self._interpret((measurement_only,))

        self.assertEqual(result.currency_side_interpretation.magnitude_state, "MAGNITUDE_NOT_CONFIGURED")
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self._assert_unsigned(result)

    def test_partial_source_dependency_fails_closed(self) -> None:
        partial = self._evidence(
            contract_id="SYNTHETIC_PARTIAL_OPERATOR_V1",
            state=interpretation.AstrologyState.UNKNOWN_ASTRO_STATE,
            status=interpretation.SourceEvidenceStatus.PARTIAL,
            unresolved=("SYNTHETIC_PRECEDENCE_NOT_CLOSED",),
        )
        result = self._interpret((partial,))

        self.assertEqual(result.astrological_interpretation.state, interpretation.AstrologyState.UNKNOWN_ASTRO_STATE)
        self.assertIn("SYNTHETIC_PRECEDENCE_NOT_CLOSED", result.astrological_interpretation.unresolved_operator_ids)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self._assert_unsigned(result)

    def test_conflicting_closed_source_operators_remain_mixed_without_precedence(self) -> None:
        result = self._interpret(
            (
                self._evidence(contract_id="SYNTHETIC_OPERATOR_SUPPORTIVE_V1"),
                self._evidence(
                    contract_id="SYNTHETIC_OPERATOR_ADVERSE_V1",
                    state=interpretation.AstrologyState.ADVERSE_ASTRO_STATE,
                ),
            )
        )

        self.assertEqual(result.astrological_interpretation.state, interpretation.AstrologyState.MIXED_ASTRO_STATE)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self.assertIn(
            "Mixed interpretation because two applicable operators conflict and no approved precedence rule exists.",
            result.explanation.why,
        )
        self._assert_unsigned(result)

    def test_mode_one_cannot_use_an_experimental_market_bridge(self) -> None:
        result = self._interpret(
            (self._evidence(),),
            mode=interpretation.InterpretationMode.SOURCE_CERTIFIED,
            hypothesis=self._hypothesis(),
        )

        self.assertEqual(result.market_bridge.status, interpretation.MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self.assertIn("source-supported but no approved USD/JPY market bridge", result.explanation.why)
        self._assert_unsigned(result)

    def test_mode_three_exposes_unsigned_features_without_direction(self) -> None:
        result = self._interpret(
            (self._evidence(),),
            mode=interpretation.InterpretationMode.EXPLORATORY_UNSIGNED,
            hypothesis=self._hypothesis(),
        )

        self.assertEqual(result.mode, interpretation.InterpretationMode.EXPLORATORY_UNSIGNED)
        self.assertEqual(result.market_bridge.status, interpretation.MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE)
        self.assertEqual(
            result.currency_side_interpretation.state,
            interpretation.CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
        )
        self._assert_unsigned(result)

    def test_experimental_hypothesis_hash_changes_with_decision_bearing_content(self) -> None:
        original = self._hypothesis()
        changed = replace(original, version="1.0.1", hypothesis_hash=None)

        self.assertNotEqual(original.hypothesis_hash, changed.hypothesis_hash)
        self.assertEqual(changed.mode, interpretation.InterpretationMode.EXPERIMENTAL_PROFILED)
        self.assertIsNone(changed.signed_unit_if_configured)
        self.assertFalse(changed.magnitude_configured)

    def test_partial_source_evidence_cannot_claim_an_astrology_sign(self) -> None:
        with self.assertRaisesRegex(interpretation.MachineInterpretationError, "must remain UNKNOWN_ASTRO_STATE"):
            self._evidence(
                state=interpretation.AstrologyState.SUPPORTIVE_ASTRO_STATE,
                status=interpretation.SourceEvidenceStatus.PARTIAL,
                unresolved=("SYNTHETIC_GAP",),
            )

    def test_synthetic_interpreter_rejects_non_synthetic_event_identity(self) -> None:
        with self.assertRaisesRegex(interpretation.MachineInterpretationError, "explicit synthetic identities"):
            interpretation.interpret_synthetic_event(
                {"eventId": "NOT_SYNTHETIC", "sideIdentity": "USD"},
                source_operator_evidence=(self._evidence(),),
                mode=interpretation.InterpretationMode.EXPLORATORY_UNSIGNED,
            )

    def test_empty_registry_and_existing_production_registries_are_isolated(self) -> None:
        registry = interpretation.ExperimentalHypothesisRegistry.load()
        production_catalogue = TargetAwarePolarityCatalogue.load()
        reviewed_evidence = TargetAwarePolarityEvidencePacketRegistry.load()

        self.assertEqual(registry.registry_status, "EMPTY_NO_AUTHORIZED_MARKET_BRIDGES")
        self.assertEqual(registry.entries, ())
        self.assertEqual(production_catalogue.entries, ())
        self.assertEqual(reviewed_evidence.packets, ())
        self.assertEqual(production_catalogue.catalogue_status, "NO_ACCEPTED_PRODUCTION_ENTRIES")
        self.assertEqual(reviewed_evidence.registry_status, "NO_REVIEWED_PACKETS")

    def test_machine_contract_and_registry_schemas_are_parseable_and_fail_closed(self) -> None:
        contract_schema = _load_json(
            PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "machine_assisted_astrological_interpretation_v1.schema.json"
        )
        registry_schema = _load_json(
            PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "experimental_market_hypothesis_registry_v1.schema.json"
        )
        registry = _load_json(
            PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "experimental_market_hypothesis_registry_v1.json"
        )

        self.assertEqual(contract_schema["properties"]["executionAllowed"]["const"], False)
        self.assertEqual(
            contract_schema["$defs"]["currencySideInterpretation"]["properties"]["signedUnit"]["const"],
            None,
        )
        self.assertEqual(registry_schema["properties"]["contract"]["const"], interpretation.HYPOTHESIS_REGISTRY_CONTRACT)
        self.assertEqual(registry["entries"], [])
        self.assertFalse(registry["guardrails"]["executionAllowed"])
        self.assertFalse(registry["guardrails"]["priceDataRead"])
        self.assertFalse(registry["guardrails"]["outcomeDataRead"])

    def test_real_identity_only_coverage_reads_no_review_store_and_returns_24_unknown_rows(self) -> None:
        with patch.object(
            interpretation.founder_review,
            "review_store_root",
            side_effect=AssertionError("real review store must not be resolved"),
        ) as review_root:
            report = interpretation.build_real_identity_only_coverage_report(PROJECT_ROOT)

        review_root.assert_not_called()
        self.assertEqual(report["summary"]["eventCount"], 24)
        self.assertEqual(report["summary"]["usdEventCount"], 12)
        self.assertEqual(report["summary"]["jpyEventCount"], 12)
        self.assertEqual(report["summary"]["singlePassVerifiedCount"], 24)
        self.assertEqual(report["summary"]["sourceOperatorAvailableCount"], 0)
        self.assertEqual(report["summary"]["marketBridgeAvailableCount"], 0)
        self.assertEqual(report["summary"]["currentDirectionUnknownCount"], 24)
        self.assertFalse(report["reviewStoreRead"])
        self.assertFalse(report["founderDecisionRead"])
        self.assertFalse(report["priceOrOutcomeRead"])
        self.assertFalse(report["guardrails"]["executionAllowed"])
        self.assertFalse(report["guardrails"]["signedWaveCreated"])
        self.assertFalse(report["guardrails"]["pairResultantCreated"])
        for side in report["sides"]:
            self.assertEqual(side["eventCount"], 12)
            for event in side["events"]:
                self.assertEqual(event["identityStatus"], "SINGLE_PASS_VERIFIED")
                self.assertEqual(event["sourceOperatorCoverage"], "OPERATOR_NOT_YET_AVAILABLE")
                self.assertEqual(event["unresolvedOperatorCount"], 1)
                self.assertEqual(event["marketBridgeStatus"], "NO_AUTHORIZED_MARKET_BRIDGE")
                self.assertEqual(event["currentDirectionStatus"], "UNKNOWN_MORE_EVIDENCE_REQUIRED")
                self.assertEqual(event["magnitudeState"], "MAGNITUDE_NOT_CONFIGURED")
                self.assertEqual(event["mode"], "EXPLORATORY_UNSIGNED")

    def test_real_identity_only_coverage_does_not_mutate_immutable_inputs(self) -> None:
        immutable_inputs = [
            PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json",
            PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json",
            PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json",
            PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json",
            PROJECT_ROOT / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json",
        ]
        before = {path: path.read_bytes() for path in immutable_inputs}
        interpretation.build_real_identity_only_coverage_report(PROJECT_ROOT)
        after = {path: path.read_bytes() for path in immutable_inputs}

        self.assertEqual(before, after)

    def test_checked_in_identity_only_coverage_report_matches_the_verified_projection(self) -> None:
        dynamic = interpretation.build_real_identity_only_coverage_report(PROJECT_ROOT)
        checked_in = _load_json(PROJECT_ROOT / "status" / "audits" / "mo_r4a_p0_real_24_identity_only_coverage.json")
        expected_sides = []
        for side in dynamic["sides"]:
            expected_sides.append(
                {
                    **{
                        key: side[key]
                        for key in (
                            "sideIdentity",
                            "blankPacketSha256",
                            "identityIntegrityManifestSha256",
                            "identityAuditSha256",
                            "eventCount",
                        )
                    },
                    "events": [
                        {
                            "eventId": event["eventIdentity"]["eventId"],
                            "eventHash": event["eventIdentity"]["eventHash"],
                            **{
                                key: event[key]
                                for key in (
                                    "identityStatus",
                                    "sourceOperatorCoverage",
                                    "unresolvedOperatorCount",
                                    "unresolvedOperatorIds",
                                    "marketBridgeStatus",
                                    "currentDirectionStatus",
                                    "magnitudeState",
                                    "mode",
                                )
                            },
                        }
                        for event in side["events"]
                    ],
                }
            )

        self.assertEqual(checked_in["contract"], dynamic["contract"])
        self.assertEqual(checked_in["schemaVersion"], dynamic["schemaVersion"])
        self.assertEqual(checked_in["inputPolicy"], dynamic["inputPolicy"])
        self.assertEqual(checked_in["identityOnlyCoverageHash"], dynamic["identityOnlyCoverageHash"])
        self.assertEqual(checked_in["summary"], dynamic["summary"])
        self.assertEqual(checked_in["guardrails"], dynamic["guardrails"])
        self.assertEqual(checked_in["sides"], expected_sides)

    def test_accepted_candidate_record_and_unsigned_mo_contract_remain_unchanged(self) -> None:
        acceptance = _load_json(PROJECT_ROOT / "status" / "acceptance" / "mo_r4_p0_founder_acceptance.json")

        self.assertEqual(acceptance["candidateVersion"], "0.10.64-pfr-v2b-mo-r3-r2-f1-r1")
        self.assertEqual(acceptance["candidateSourceCommit"], "9208a552cbed5ec0228e7811c9189393a1581797")
        self.assertEqual(
            acceptance["candidateHashes"],
            {
                "portableSha256": "A43ED1EF1CFD5CCFFDD7E7A14B5BCCB79538C5AF536638035B3C984D8D832545",
                "installerSha256": "3DC5ED637DDEE4C0625BAA745C8CB06D19EF87700699228AFE1E8CE61883BADB",
                "sidecarSha256": "B82F66D5A913232DB20BF081BF1328D18B77E9D872ED144A67DFC57A8A362852",
                "buildReceiptSha256": "A570E42C5843CC70BDB5EE34F73F43D4DA9EA8C90F409511BEC23841C6454E13",
                "releaseManifestSha256": "AC48605BFF0884D0F48F70719356D852C68EBBD12EC717977D353EAB49E19275",
                "immutableResourceTreeSha256": "0BBCE6E888974C28A59FA62589AE4604C8360675DC5FE3FA36F26FA82729F266",
            },
        )
        self.assertEqual(activity.MO_ACTIVITY_RANGE_CONTRACT, "MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1")
        self.assertEqual(activity.MO_EVIDENCE_MODE, "EXPLORATORY_UNSIGNED")
        self.assertEqual(activity.MO_ACTIVITY_SCHEMA_VERSION, 2)

    def test_protocol_supersession_preserves_history_and_all_fail_closed_locks(self) -> None:
        protocol = _load_json(
            PROJECT_ROOT / "status" / "acceptance" / "mo_r4a_p0_machine_assisted_interpretation_protocol.json"
        )

        self.assertEqual(protocol["startingMaster"], "e1cfdbaafcb3244e502b825d46f3119f0704a1d3")
        self.assertEqual(
            protocol["protocolSupersession"]["status"],
            "SUPERSEDED_BEFORE_FIRST_REAL_DECISION",
        )
        self.assertEqual(protocol["newPilot"]["name"], "BLINDED_MACHINE_ASSISTED_INTERPRETATION")
        self.assertEqual(protocol["newPilot"]["realPilotUniverse"]["canonicalEventCount"], 24)
        self.assertEqual(protocol["newPilot"]["realPilotUniverse"]["realFounderDecisionsAtSupersession"], 0)
        self.assertFalse(protocol["newPilot"]["outcomeDataRead"])
        self.assertFalse(protocol["newPilot"]["realFounderReviewDataReadByThisMilestone"])
        self.assertFalse(protocol["newPilot"]["realFounderReviewDataWrittenByThisMilestone"])
        self.assertFalse(protocol["newPilot"]["realPolarityGeneratedByThisMilestone"])
        self.assertEqual(protocol["preservedHistoricalInfrastructure"]["founderReviewWorkbench"], "PRESERVED")
        self.assertEqual(protocol["preservedHistoricalInfrastructure"]["founderReviewFreezeVerifier"], "PRESERVED_NOT_EXECUTED")
        self.assertEqual(protocol["futureFreezeDesign"]["status"], "DESIGN_ONLY_NOT_IMPLEMENTED")
        self.assertEqual(protocol["researchState"]["marketHypothesisRegistry"], "EMPTY_NO_AUTHORIZED_MARKET_BRIDGES")
        self.assertEqual(protocol["researchState"]["signedUsdRuntime"], "NOT_AUTHORIZED")
        self.assertEqual(protocol["researchState"]["signedJpyRuntime"], "NOT_AUTHORIZED")
        self.assertEqual(protocol["researchState"]["signedUsdJpyRuntime"], "NOT_AUTHORIZED")
        self.assertEqual(protocol["researchState"]["magnitude"], "NOT_CONFIGURED")
        self.assertFalse(protocol["researchState"]["executionAllowed"])
        self.assertTrue(all(value is False for value in protocol["locks"].values()))


if __name__ == "__main__":
    unittest.main()
