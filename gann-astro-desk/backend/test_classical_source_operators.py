"""Outcome-free regression coverage for MO-R4A-S1 source operators."""

from __future__ import annotations

import copy
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
for root in (PROJECT_ROOT, PROJECT_ROOT / "gann-astro-desk", PROJECT_ROOT / "gann-astro-desk" / "backend", LAB_ROOT, INSTRUMENT_SBC_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import classical_source_operators as operators  # noqa: E402
import machine_assisted_interpretation as machine_interpretation  # noqa: E402
import multi_oscillator_activity_service as activity  # noqa: E402


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ClassicalSourceOperatorTests(unittest.TestCase):
    """The only real inputs exercised here are immutable identity-safe fields."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = operators.load_source_operator_ledger()
        cls.hardened_ledger = operators.build_s1r1_provenance_hardened_ledger(PROJECT_ROOT)
        cls.dependencies = operators.load_unresolved_dependency_registry()
        cls.matrix = operators.load_cross_text_matrix()

    def test_ledger_has_unique_versioned_operators_and_required_fields(self) -> None:
        operators.validate_source_operator_ledger(self.ledger)
        identities = [(item["operatorId"], item["operatorVersion"]) for item in self.ledger["operators"]]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertGreaterEqual(len(identities), 17)
        for item in self.ledger["operators"]:
            self.assertTrue(operators.REQUIRED_LEDGER_FIELDS.issubset(item))

    def test_every_closed_operator_has_locator_and_no_market_authorization(self) -> None:
        for item in self.ledger["operators"]:
            if item["sourceStatus"].startswith("SOURCE_CLOSED"):
                self.assertTrue(item["verseOrLocator"])
            self.assertFalse(item["marketDirectionAuthorized"])
            self.assertFalse(item["marketMagnitudeAuthorized"])
            self.assertTrue(item["prohibitedInterpretations"], item["operatorId"])

    def test_s1r1_provenance_hardening_covers_each_historical_operator_once(self) -> None:
        operators.validate_source_operator_ledger(self.hardened_ledger)
        old_identities = {(item["operatorId"], item["operatorVersion"]) for item in self.ledger["operators"]}
        hardened_identities = {
            (item["operatorId"], item["operatorVersion"]) for item in self.hardened_ledger["operators"]
        }
        self.assertEqual(hardened_identities, old_identities)
        self.assertEqual(len(hardened_identities), 17)
        self.assertEqual(
            self.hardened_ledger["provenanceHardening"]["baseLedgerCanonicalHash"],
            operators._canonical_hash(self.ledger),
        )

    def test_s1r1_checked_in_successor_ledger_matches_the_deterministic_overlay(self) -> None:
        checked_in = _load_json(
            PROJECT_ROOT
            / "configs"
            / "research"
            / "machine_interpretation"
            / "source_operators"
            / "classical_source_operator_ledger_s1r1_v1.json"
        )
        self.assertEqual(checked_in, self.hardened_ledger)
        self.assertEqual(operators._canonical_hash(checked_in), "9704821AB7A3777ABA6DB7671246B989ACBE0403FF511EED7CC38303BDBE2867")

    def test_s1r1_closed_operators_have_exact_non_central_source_locators(self) -> None:
        for item in self.hardened_ledger["operators"]:
            locators = item["sourceLocators"]
            self.assertTrue(locators, item["operatorId"])
            if item["sourceStatus"].startswith("SOURCE_CLOSED"):
                exact = [locator for locator in locators if locator["provenanceStatus"] == "SOURCE_CLOSED_EXACT_PAGE_IMAGE"]
                self.assertTrue(exact, item["operatorId"])
                for locator in exact:
                    self.assertNotIn("CENTRAL_AUDIT", locator["witnessId"])
                    self.assertNotEqual(locator["sourceLayer"], "HISTORICAL_CENTRAL_AUDIT")
                    self.assertTrue(locator["printedPage"])
                    self.assertTrue(locator["scanPage"])

    def test_s1r1_rejects_generic_central_audit_as_exact_root_provenance(self) -> None:
        invalid = copy.deepcopy(self.hardened_ledger)
        target = next(item for item in invalid["operators"] if item["operatorId"] == "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1")
        target["sourceLocators"][0]["witnessId"] = "MO_R4A_S1_CENTRAL_SOURCE_AUDIT"
        with self.assertRaisesRegex(operators.ClassicalSourceOperatorError, "Central-audit"):
            operators.validate_source_operator_ledger(invalid)

    def test_s1r1_root_commentary_and_translation_layers_cannot_be_collapsed(self) -> None:
        commentary_invalid = copy.deepcopy(self.hardened_ledger)
        compound = next(
            item for item in commentary_invalid["operators"] if item["operatorId"] == "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1"
        )
        commentary = next(locator for locator in compound["sourceLocators"] if locator["sourceLayer"] == "BHATTOPALA_COMMENTARY")
        commentary["propositionRole"] = "BRIHAT_JATAKA_ROOT_COMPOUND_RULE"
        with self.assertRaisesRegex(operators.ClassicalSourceOperatorError, "Bhatotpala commentary"):
            operators.validate_source_operator_ledger(commentary_invalid)

        translation_invalid = copy.deepcopy(self.hardened_ledger)
        ordinary = next(
            item for item in translation_invalid["operators"] if item["operatorId"] == "SARAVALI_4_32_ORDINARY_DRSTI_V1"
        )
        translation = next(locator for locator in ordinary["sourceLocators"] if locator["sourceLayer"] == "SANTHANAM_TRANSLATION")
        translation["propositionRole"] = "SARAVALI_ROOT_ORDINARY_DRSTI"
        with self.assertRaisesRegex(operators.ClassicalSourceOperatorError, "Santhanam layer"):
            operators.validate_source_operator_ledger(translation_invalid)

    def test_s1r1_preserves_saravali_432_translation_mismatch_and_trailokya_page_locks(self) -> None:
        ordinary = next(
            item for item in self.hardened_ledger["operators"] if item["operatorId"] == "SARAVALI_4_32_ORDINARY_DRSTI_V1"
        )
        root = next(locator for locator in ordinary["sourceLocators"] if locator["sourceLayer"] == "SARAVALI_ROOT")
        translation = next(locator for locator in ordinary["sourceLocators"] if locator["sourceLayer"] == "SANTHANAM_TRANSLATION")
        self.assertEqual((root["printedPage"], root["scanPage"], root["verse"]), ("58", "62", "32-33"))
        self.assertEqual(translation["provenanceStatus"], "TRANSLATION_EDITORIAL_MISMATCH")
        self.assertIn("SANTHANAM_ENGLISH_4_32_TRANSLATION_EDITORIAL_MISMATCH", ordinary["knownTranslationIssues"])
        trailokya = next(
            item for item in self.hardened_ledger["operators"] if item["operatorId"] == "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1"
        )
        trailokya_locator = next(
            locator for locator in trailokya["sourceLocators"] if locator["sourceFamily"] == "TRAILOKYA_DIPIKA_1972"
        )
        self.assertEqual((trailokya_locator["printedPage"], trailokya_locator["scanPage"]), ("82, 84", "98, 100"))

    def test_s1r1_unresolved_source_locator_stays_unbound_and_unexecutable(self) -> None:
        partial = next(
            item for item in self.hardened_ledger["operators"] if item["operatorId"] == "SARAVALI_NAISARGIKA_STRENGTH_V1"
        )
        locator = partial["sourceLocators"][0]
        self.assertEqual(locator["provenanceStatus"], "EXACT_SOURCE_LOCATOR_NOT_DURABLY_BOUND")
        self.assertEqual(locator["printedPage"], "")
        self.assertEqual(locator["scanPage"], "")
        self.assertFalse(partial["machineEvaluable"])
        self.assertFalse(partial["modeOneEligible"])

    def test_commentary_only_cannot_claim_root_family(self) -> None:
        invalid = copy.deepcopy(self.ledger)
        invalid["operators"][0]["rootOrCommentary"] = "COMMENTARY_ONLY"
        invalid["operators"][0]["sourceFamily"] = "TRAILOKYA_ROOT"
        with self.assertRaisesRegex(operators.ClassicalSourceOperatorError, "Commentary-only"):
            operators.validate_source_operator_ledger(invalid)

    def test_translation_mismatch_is_explicit_and_does_not_change_saravali_root_operator(self) -> None:
        topic = next(item for item in self.matrix["topics"] if item["topicId"] == "ORDINARY_DRSTI_FRACTIONS")
        root = next(item for item in topic["records"] if item["sourceFamily"] == "SARAVALI_ROOT")
        translation = next(item for item in topic["records"] if item["sourceFamily"] == "SANTHANAM_TRANSLATION")
        self.assertEqual(root["status"], "SOURCE_CLOSED_EXECUTABLE")
        self.assertEqual(translation["status"], "TRANSLATION_EDITORIAL_MISMATCH")
        self.assertEqual(translation["doesNotAlter"], "SARAVALI_4_32_ORDINARY_DRSTI_V1")
        self.assertEqual(operators.evaluate_ordinary_dristi(5, ledger=self.ledger)["sourceMeasurement"]["value"], "1/2")
        self.assertEqual(operators.evaluate_ordinary_dristi(4, ledger=self.ledger)["sourceMeasurement"]["value"], "3/4")

    def test_cross_text_agreement_retains_individual_provenance(self) -> None:
        topic = next(item for item in self.matrix["topics"] if item["topicId"] == "SPECIAL_DRSTI_GEOMETRY")
        source_families = {item["sourceFamily"] for item in topic["records"]}
        self.assertEqual(
            source_families,
            {"BRIHAT_JATAKA_ROOT", "SARAVALI_ROOT", "TRAILOKYA_DIPIKA_1972"},
        )
        self.assertEqual(topic["relationshipStatus"], "CROSS_TEXT_AGREEMENT")

    def test_partial_or_unresolved_operator_cannot_claim_mode_one_closure(self) -> None:
        invalid = copy.deepcopy(self.ledger)
        partial = next(item for item in invalid["operators"] if item["sourceStatus"] == "SOURCE_PARTIAL")
        partial["modeOneEligible"] = True
        with self.assertRaisesRegex(operators.ClassicalSourceOperatorError, "Unresolved operator"):
            operators.validate_source_operator_ledger(invalid)

    def test_unresolved_dependency_registry_has_required_fail_closed_entries(self) -> None:
        ids = {item["dependencyId"] for item in self.dependencies["dependencies"]}
        self.assertTrue(
            {
                "MULTI_MODIFIER_STACKING_UNRESOLVED",
                "UNIVERSAL_MULTI_PLANET_PRECEDENCE_NOT_SOURCE_CLOSED",
                "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED",
                "CONTEXT_SPECIFIC_RESOLVER_REQUIRED",
                "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT",
                "NO_AUTHORIZED_MARKET_BRIDGE",
                "TRAILOKYA_ARTHA_CONTEXT_NOT_GENERALIZABLE",
                "LATTA_NOT_ORDINARY_VEDHA",
                "ARGHYA_NOT_GENERIC_MARKET_OPERATOR",
            }.issubset(ids)
        )
        for item in self.dependencies["dependencies"]:
            self.assertTrue(item["failClosedBehavior"])
            self.assertTrue(item["whatWouldCloseIt"])
            self.assertTrue(item["prohibitedFallback"])

    def test_trailokya_natural_relationship_fixture(self) -> None:
        self.assertEqual(
            operators.evaluate_trailokya_natural_relationship("SUN", "MOON", ledger=self.ledger)["outputState"],
            "FRIEND",
        )
        self.assertEqual(
            operators.evaluate_trailokya_natural_relationship("SUN", "MERCURY", ledger=self.ledger)["outputState"],
            "NEUTRAL",
        )
        self.assertEqual(
            operators.evaluate_trailokya_natural_relationship("SUN", "VENUS", ledger=self.ledger)["outputState"],
            "ENEMY",
        )
        node_relation = operators.evaluate_trailokya_natural_relationship("MOON", "RAHU", ledger=self.ledger)
        self.assertEqual(node_relation["status"], "SOURCE_UNRESOLVED")

    def test_temporary_relationship_all_positions_and_wraparound(self) -> None:
        friendly = {2, 3, 4, 10, 11, 12}
        for place in range(1, 13):
            target = operators.SIGNS[(operators.SIGN_INDEX["ARIES"] + place - 1) % 12]
            result = operators.evaluate_temporary_relationship("ARIES", target, ledger=self.ledger)
            self.assertEqual(result["inputSnapshot"]["relativePlace"], place)
            self.assertEqual(
                result["outputState"],
                "TEMPORARY_FRIEND" if place in friendly else "TEMPORARY_ENEMY",
            )
        wrapped = operators.evaluate_temporary_relationship("PISCES", "ARIES", ledger=self.ledger)
        self.assertEqual(wrapped["inputSnapshot"]["relativePlace"], 2)
        self.assertEqual(wrapped["outputState"], "TEMPORARY_FRIEND")

    def test_compound_relationship_has_all_five_states_without_numeric_sign(self) -> None:
        fixtures = {
            ("FRIEND", "TEMPORARY_FRIEND"): "GREAT_FRIEND",
            ("FRIEND", "TEMPORARY_ENEMY"): "NEUTRAL",
            ("NEUTRAL", "TEMPORARY_FRIEND"): "FRIEND",
            ("NEUTRAL", "TEMPORARY_ENEMY"): "ENEMY",
            ("ENEMY", "TEMPORARY_ENEMY"): "GREAT_ENEMY",
        }
        states = set()
        for inputs, expected in fixtures.items():
            result = operators.evaluate_compound_relationship(*inputs, ledger=self.ledger)
            states.add(result["outputState"])
            self.assertEqual(result["outputState"], expected)
            self.assertIsNone(result["sourceMeasurement"])
            self.assertFalse(result["marketDirectionAuthorized"])
            self.assertNotIn("signedUnit", result)
        self.assertEqual(states, {"GREAT_FRIEND", "NEUTRAL", "FRIEND", "ENEMY", "GREAT_ENEMY"})

    def test_ordinary_dristi_fractions_are_exact_and_typed(self) -> None:
        expected = {
            3: "1/4",
            10: "1/4",
            5: "1/2",
            9: "1/2",
            4: "3/4",
            8: "3/4",
            7: "FULL",
        }
        for place, value in expected.items():
            result = operators.evaluate_ordinary_dristi(place, ledger=self.ledger)
            self.assertEqual(result["sourceMeasurement"]["measurementType"], "DRSTI_FRACTION")
            self.assertEqual(result["sourceMeasurement"]["value"], value)
            self.assertIsNone(result["sourceMeasurement"]["oscillatorMagnitude"])
            self.assertFalse(result["marketMagnitudeAuthorized"])

    def test_special_dristi_full_overrides_are_exact(self) -> None:
        for body, places in {"SATURN": (3, 10), "JUPITER": (5, 9), "MARS": (4, 8)}.items():
            for place in places:
                result = operators.evaluate_special_dristi(body, place, ledger=self.ledger)
                self.assertEqual(result["outputState"], "SPECIAL_FULL_DRSTI")
                self.assertEqual(result["sourceMeasurement"]["value"], "FULL")
        self.assertEqual(
            operators.evaluate_special_dristi("SATURN", 5, ledger=self.ledger)["outputState"],
            "NO_SPECIAL_FULL_OVERRIDE",
        )

    def test_sthana_bala_and_phala_remain_distinct_typed_measurements(self) -> None:
        bala = operators.evaluate_trailokya_sthana_bala("FRIEND", ledger=self.ledger)
        phala = operators.evaluate_trailokya_sthana_phala("SAUMYA", "FRIEND", ledger=self.ledger)
        self.assertEqual(bala["sourceMeasurement"]["measurementType"], "STHANA_BALA_FRACTION")
        self.assertEqual(bala["sourceMeasurement"]["value"], "3/4")
        self.assertEqual(phala["sourceMeasurement"]["measurementType"], "TRAILOKYA_STHANA_PHALA")
        self.assertEqual(phala["sourceMeasurement"]["value"], "15")
        self.assertNotEqual(bala["sourceMeasurement"]["measurementType"], phala["sourceMeasurement"]["measurementType"])
        self.assertIsNone(phala["sourceMeasurement"]["oscillatorMagnitude"])

    def test_sthana_phala_tables_are_exact_and_not_normalized(self) -> None:
        for relationship, expected in {"OWN": "20", "FRIEND": "15", "NEUTRAL": "10", "ENEMY": "5"}.items():
            result = operators.evaluate_trailokya_sthana_phala("SAUMYA", relationship, ledger=self.ledger)
            self.assertEqual(result["sourceMeasurement"]["value"], expected)
        for relationship, expected in {"OWN": "5", "FRIEND": "10", "NEUTRAL": "15", "ENEMY": "20"}.items():
            result = operators.evaluate_trailokya_sthana_phala("KRURA", relationship, ledger=self.ledger)
            self.assertEqual(result["sourceMeasurement"]["value"], expected)
            self.assertNotIn("normalizedValue", result["sourceMeasurement"])

    def test_v166_individual_modifiers_and_multi_modifier_failure(self) -> None:
        base = operators.evaluate_trailokya_sthana_phala("SAUMYA", "FRIEND", ledger=self.ledger)["sourceMeasurement"]
        self.assertEqual(
            operators.evaluate_trailokya_v166_modifier(base, ["RETROGRADE"], ledger=self.ledger)["sourceMeasurement"]["value"],
            "30",
        )
        self.assertEqual(
            operators.evaluate_trailokya_v166_modifier(base, ["EXALTATION"], ledger=self.ledger)["sourceMeasurement"]["value"],
            "45",
        )
        self.assertEqual(
            operators.evaluate_trailokya_v166_modifier(base, ["DEBILITATION"], ledger=self.ledger)["sourceMeasurement"]["value"],
            "15/2",
        )
        swift = operators.evaluate_trailokya_v166_modifier(base, ["SWIFT"], ledger=self.ledger)
        self.assertEqual(swift["sourceMeasurement"]["value"], "15")
        self.assertIsNone(swift["sourceMeasurement"]["sourceModifierFactor"])
        combined = operators.evaluate_trailokya_v166_modifier(base, ["RETROGRADE", "EXALTATION"], ledger=self.ledger)
        self.assertEqual(combined["status"], "SOURCE_UNRESOLVED")
        self.assertIn("MULTI_MODIFIER_STACKING_UNRESOLVED", combined["unresolvedDependencies"])

    def test_categorical_nature_is_not_numeric_modifier(self) -> None:
        retrograde = operators.evaluate_trailokya_planet_nature(
            "SATURN",
            motion_state="RETROGRADE",
            ledger=self.ledger,
        )
        swift = operators.evaluate_trailokya_planet_nature("SATURN", motion_state="SWIFT", ledger=self.ledger)
        self.assertEqual(retrograde["outputState"], "MAHAKRURA")
        self.assertEqual(swift["outputState"], "KRURA")
        self.assertIsNone(retrograde["sourceMeasurement"])
        self.assertFalse(retrograde["marketMagnitudeAuthorized"])

    def test_trailokya_dignity_preserves_paramocca_and_sign_lords_without_composition(self) -> None:
        dignity = next(
            operator
            for operator in self.ledger["operators"]
            if operator["operatorId"] == "TRAILOKYA_1972_DIGNITY_V1"
        )
        expected_paramocca = {
            "SUN": 10,
            "MOON": 3,
            "MARS": 28,
            "MERCURY": 15,
            "JUPITER": 5,
            "VENUS": 27,
            "SATURN": 20,
        }
        self.assertEqual(
            {
                body: rule["paramoccaDegrees"]
                for body, rule in dignity["rule"]["planets"].items()
            },
            expected_paramocca,
        )
        self.assertEqual(
            dignity["rule"]["signLords"],
            {
                "ARIES": "MARS",
                "TAURUS": "VENUS",
                "GEMINI": "MERCURY",
                "CANCER": "MOON",
                "LEO": "SUN",
                "VIRGO": "MERCURY",
                "LIBRA": "VENUS",
                "SCORPIO": "MARS",
                "SAGITTARIUS": "JUPITER",
                "CAPRICORN": "SATURN",
                "AQUARIUS": "SATURN",
                "PISCES": "JUPITER",
            },
        )
        result = operators.evaluate_trailokya_dignity("SUN", "ARIES", ledger=self.ledger)
        self.assertEqual(result["outputState"], "EXALTATION")
        self.assertIsNone(result["sourceMeasurement"])
        self.assertFalse(result["marketDirectionAuthorized"])
        self.assertFalse(result["marketMagnitudeAuthorized"])

    def test_latta_arghya_and_context_boundaries_cannot_become_global_resolvers(self) -> None:
        latta = operators.evaluate_latta_source_boundary(ledger=self.ledger)
        arghya = operators.evaluate_arghya_source_boundary(ledger=self.ledger)
        self.assertEqual(latta["status"], "SOURCE_UNRESOLVED")
        self.assertIn("LATTA_NOT_ORDINARY_VEDHA", latta["unresolvedDependencies"])
        self.assertEqual(arghya["status"], "SOURCE_UNRESOLVED")
        self.assertIn("ARGHYA_NOT_GENERIC_MARKET_OPERATOR", arghya["unresolvedDependencies"])
        self.assertIn("TRAILOKYA_ARTHA_CONTEXT_NOT_GENERALIZABLE", arghya["unresolvedDependencies"])

    def test_motion_and_dik_bala_are_bounded_and_non_market(self) -> None:
        motion = operators.evaluate_trailokya_motion_class("SATURN", 3, ledger=self.ledger)
        self.assertEqual(motion["outputState"], "SAMA")
        self.assertTrue(motion["machineEvaluated"])
        unknown_motion = operators.evaluate_trailokya_motion_class("MOON", 3, ledger=self.ledger)
        self.assertEqual(unknown_motion["status"], "SOURCE_UNRESOLVED")
        dik = operators.evaluate_dik_bala_condition("JUPITER", "EAST", ledger=self.ledger)
        self.assertEqual(dik["outputState"], "DIRECTIONAL_STRENGTH_CONDITION_PRESENT")
        self.assertFalse(dik["marketDirectionAuthorized"])
        self.assertFalse(dik["marketMagnitudeAuthorized"])

    def test_no_source_output_can_create_currency_direction_or_magnitude(self) -> None:
        outputs = [
            operators.evaluate_trailokya_planet_nature("SATURN", ledger=self.ledger),
            operators.evaluate_compound_relationship("ENEMY", "TEMPORARY_ENEMY", ledger=self.ledger),
            operators.evaluate_ordinary_dristi(7, ledger=self.ledger),
            operators.evaluate_trailokya_sthana_phala("KRURA", "ENEMY", ledger=self.ledger),
            operators.evaluate_trailokya_dignity("SUN", "ARIES", ledger=self.ledger),
        ]
        composition = operators.compose_source_operator_outputs(outputs)
        self.assertEqual(composition["astrologicalInterpretationState"], "UNKNOWN_ASTRO_STATE")
        self.assertEqual(composition["compositionStatus"], operators.NO_COMPOSITION_CONTRACT)
        for output in outputs:
            self.assertFalse(output["marketDirectionAuthorized"])
            self.assertFalse(output["marketMagnitudeAuthorized"])
            if output["sourceMeasurement"] is not None:
                self.assertIsNone(output["sourceMeasurement"]["signedUnit"])
                self.assertIsNone(output["sourceMeasurement"]["oscillatorMagnitude"])

    def test_all_source_operator_json_and_schema_files_parse(self) -> None:
        root = PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "source_operators"
        files = list(root.glob("*.json"))
        self.assertGreaterEqual(len(files), 4)
        for path in files:
            self.assertIsInstance(_load_json(path), dict, path.name)
        schema = _load_json(root / "classical_source_operator_ledger_v1.schema.json")
        self.assertEqual(schema["properties"]["contract"]["const"], operators.CLASSICAL_SOURCE_OPERATOR_LEDGER_CONTRACT)
        self.assertEqual(schema["$defs"]["operator"]["properties"]["marketDirectionAuthorized"]["const"], False)
        self.assertEqual(schema["$defs"]["operator"]["properties"]["marketMagnitudeAuthorized"]["const"], False)

    def test_real_coverage_is_identity_only_and_does_not_resolve_review_store(self) -> None:
        with patch.object(
            machine_interpretation.founder_review,
            "review_store_root",
            side_effect=AssertionError("real Founder Review store must not be resolved"),
        ) as review_root:
            report = operators.build_real_source_operator_coverage_report(PROJECT_ROOT)
        review_root.assert_not_called()
        self.assertFalse(report["reviewStoreRead"])
        self.assertFalse(report["founderDecisionRead"])
        self.assertFalse(report["priceOrOutcomeRead"])

    def test_real_coverage_preserves_24_verified_identities_and_times(self) -> None:
        baseline = machine_interpretation.build_real_identity_only_coverage_report(PROJECT_ROOT)
        report = operators.build_real_source_operator_coverage_report(PROJECT_ROOT)
        baseline_events = [
            event["eventIdentity"]
            for side in baseline["sides"]
            for event in side["events"]
        ]
        bound_events = [event for side in report["sides"] for event in side["events"]]
        self.assertEqual(len(bound_events), 24)
        self.assertEqual(report["summary"]["usdEventCount"], 12)
        self.assertEqual(report["summary"]["jpyEventCount"], 12)
        self.assertEqual(report["summary"]["singlePassVerifiedCount"], 24)
        for source, bound in zip(baseline_events, bound_events, strict=True):
            self.assertEqual(bound["eventId"], source["eventId"])
            self.assertEqual(bound["eventHash"], source["eventHash"])
            self.assertEqual(bound["exactUtc"], source["exactUtc"])
            self.assertEqual(bound["identityStatus"], "SINGLE_PASS_VERIFIED")
            self.assertEqual(bound["inputPolicy"], "IMMUTABLE_EVENT_IDENTITY_PLUS_APPROVED_CHART_ASTRONOMY_ONLY")

    def test_s1r1_rebinding_preserves_each_immutable_identity_and_evaluator_math(self) -> None:
        baseline = operators.build_real_source_operator_coverage_report(PROJECT_ROOT)
        hardened = operators.build_real_source_operator_coverage_report(
            PROJECT_ROOT,
            source_ledger=self.hardened_ledger,
            milestone="MO-R4A-S1R1",
            coverage_contract=operators.CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT,
        )
        self.assertEqual(hardened["contract"], operators.CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT)
        self.assertEqual(hardened["summary"]["eventCount"], 24)
        self.assertEqual(hardened["summary"]["usdEventCount"], 12)
        self.assertEqual(hardened["summary"]["jpyEventCount"], 12)
        self.assertEqual(hardened["summary"]["singlePassVerifiedCount"], 24)
        before_events = [event for side in baseline["sides"] for event in side["events"]]
        after_events = [event for side in hardened["sides"] for event in side["events"]]
        identity_keys = ("eventId", "eventHash", "sideIdentity", "transitBody", "natalTarget", "aspectType", "exactUtc")
        for before, after in zip(before_events, after_events, strict=True):
            self.assertEqual({key: before[key] for key in identity_keys}, {key: after[key] for key in identity_keys})
            self.assertEqual(before["astronomySnapshot"], after["astronomySnapshot"])
            self.assertEqual(before["applicableOperatorIds"], after["applicableOperatorIds"])
            self.assertEqual(before["evaluatedOperatorIds"], after["evaluatedOperatorIds"])
            self.assertEqual(before["unresolvedOperatorIds"], after["unresolvedOperatorIds"])
            self.assertEqual(before["sourceCoverageStatus"], after["sourceCoverageStatus"])
            self.assertEqual(before["astrologicalCompositionStatus"], after["astrologicalCompositionStatus"])
            self.assertEqual(before["astrologicalInterpretationState"], after["astrologicalInterpretationState"])
            self.assertEqual(before["marketBridgeStatus"], after["marketBridgeStatus"])
            self.assertEqual(before["currencyDirectionStatus"], after["currencyDirectionStatus"])
            self.assertEqual(before["magnitudeStatus"], after["magnitudeStatus"])
            self.assertNotEqual(before["operatorOutputs"], after["operatorOutputs"])
        self.assertNotEqual(
            baseline["sourceOperatorLedgerCanonicalHash"],
            hardened["sourceOperatorLedgerCanonicalHash"],
        )
        self.assertNotEqual(baseline["sourceOperatorCoverageHash"], hardened["sourceOperatorCoverageHash"])

    def test_s1r1_rebinding_comparison_proves_all_changed_bytes_are_provenance_only(self) -> None:
        comparison = operators.build_s1r1_rebinding_identity_comparison(PROJECT_ROOT)
        self.assertEqual(comparison["eventCount"], 24)
        self.assertEqual(comparison["usdEventCount"], 12)
        self.assertEqual(comparison["jpyEventCount"], 12)
        self.assertEqual(comparison["singlePassVerifiedCount"], 24)
        for item in comparison["comparisons"]:
            self.assertTrue(item["identityUnchanged"], item["eventId"])
            self.assertTrue(item["astronomySnapshotUnchanged"], item["eventId"])
            self.assertTrue(item["evaluationSemanticsUnchanged"], item["eventId"])
            self.assertTrue(item["eventFieldsOutsideOperatorOutputsUnchanged"], item["eventId"])
            self.assertTrue(item["operatorOutputSemanticsUnchanged"], item["eventId"])
            self.assertTrue(item["changedReportBytesRestrictedToProvenanceOrHash"], item["eventId"])
        self.assertTrue(comparison["summary"]["reportChangesRestrictedToProvenanceOrHash"])
        self.assertFalse(comparison["summary"]["outcomeDataRead"])
        self.assertFalse(comparison["summary"]["executionAllowed"])

    def test_s1r1_checked_in_provenance_audit_covers_all_operators_without_math_change(self) -> None:
        dynamic = operators.build_s1r1_source_provenance_audit(PROJECT_ROOT)
        checked_in = _load_json(PROJECT_ROOT / "status" / "audits" / "mo_r4a_s1r1_source_provenance_audit.json")
        self.assertEqual(checked_in, dynamic)
        self.assertEqual(dynamic["operatorCount"], 17)
        self.assertFalse(dynamic["summary"]["evaluatorMathematicsChanged"])
        self.assertFalse(dynamic["summary"]["eventOutputSemanticsChanged"])
        for row in dynamic["rows"]:
            self.assertTrue(row["previousSourceLocator"], row["operatorId"])
            self.assertTrue(row["newSourceLocators"], row["operatorId"])
            self.assertTrue(row["reasonForChange"], row["operatorId"])
            self.assertFalse(row["evaluatorMathematicsChanged"], row["operatorId"])
            self.assertFalse(row["eventOutputSemanticsChanged"], row["operatorId"])

    def test_s1r1_checked_in_identity_comparison_matches_deterministic_rebinding(self) -> None:
        dynamic = operators.build_s1r1_rebinding_identity_comparison(PROJECT_ROOT)
        checked_in = _load_json(PROJECT_ROOT / "status" / "audits" / "mo_r4a_s1r1_immutable_event_rebinding_comparison.json")
        self.assertEqual(checked_in, dynamic)

    def test_s1r1_rebinding_is_outcome_blind_and_execution_locked(self) -> None:
        with patch.object(
            machine_interpretation.founder_review,
            "review_store_root",
            side_effect=AssertionError("S1R1 must not resolve the Founder Review store"),
        ) as review_root:
            report = operators.build_real_source_operator_coverage_report(
                PROJECT_ROOT,
                source_ledger=self.hardened_ledger,
                milestone="MO-R4A-S1R1",
                coverage_contract=operators.CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT,
            )
        review_root.assert_not_called()
        self.assertFalse(report["reviewStoreRead"])
        self.assertFalse(report["founderDecisionRead"])
        self.assertFalse(report["priceOrOutcomeRead"])
        self.assertEqual(report["guardrails"]["marketHypothesisRegistryEntriesCreated"], 0)
        self.assertFalse(report["guardrails"]["catalogueAdmission"])
        self.assertFalse(report["guardrails"]["evidenceAdmission"])
        self.assertFalse(report["guardrails"]["magnitudeConfigured"])
        self.assertFalse(report["guardrails"]["executionAllowed"])

    def test_real_coverage_has_no_market_bridge_currency_direction_or_signed_waves(self) -> None:
        report = operators.build_real_source_operator_coverage_report(PROJECT_ROOT)
        self.assertEqual(report["summary"]["eventCount"], 24)
        self.assertEqual(report["summary"]["marketBridgeAvailableCount"], 0)
        self.assertEqual(report["summary"]["currencyDirectionUnknownCount"], 24)
        self.assertEqual(report["summary"]["magnitudeConfiguredCount"], 0)
        self.assertEqual(report["summary"]["astrologyUnknownCount"], 24)
        self.assertEqual(report["summary"]["astrologyMixedCount"], 0)
        self.assertEqual(report["summary"]["astrologySourceStateCount"], 0)
        self.assertEqual(
            report["summary"]["sourceOperatorNoneCount"]
            + report["summary"]["sourceOperatorPartialCount"]
            + report["summary"]["sourceOperatorSubstantialCount"]
            + report["summary"]["sourceOperatorCompleteForDeclaredScopeCount"],
            24,
        )
        for event in [event for side in report["sides"] for event in side["events"]]:
            self.assertEqual(event["marketBridgeStatus"], operators.NO_MARKET_BRIDGE)
            self.assertEqual(event["currencyDirectionStatus"], operators.UNKNOWN_CURRENCY_DIRECTION)
            self.assertEqual(event["magnitudeStatus"], operators.MAGNITUDE_NOT_CONFIGURED)
            self.assertEqual(event["mode"], operators.EXPLORATORY_UNSIGNED_MODE)
            self.assertEqual(event["astrologicalInterpretationState"], "UNKNOWN_ASTRO_STATE")
            self.assertEqual(event["astrologicalCompositionStatus"], operators.NO_COMPOSITION_CONTRACT)
            self.assertNotIn("signedUnit", event)
            self.assertNotIn("signedWave", event)
            self.assertNotIn("pairResultant", event)
        self.assertFalse(report["guardrails"]["signedUsdWaveCreated"])
        self.assertFalse(report["guardrails"]["signedJpyWaveCreated"])
        self.assertFalse(report["guardrails"]["signedPairResultantCreated"])
        self.assertFalse(report["guardrails"]["executionAllowed"])

    def test_checked_in_coverage_artifacts_match_the_deterministic_projection(self) -> None:
        dynamic = operators.build_real_source_operator_coverage_report(PROJECT_ROOT)
        checked_in = _load_json(PROJECT_ROOT / "status" / "audits" / "mo_r4a_s1_real_24_source_operator_coverage.json")
        self.assertEqual(checked_in, dynamic)
        self.assertEqual(dynamic["sourceOperatorLedgerCanonicalHash"], operators._canonical_hash(self.ledger))
        rendered = operators.render_real_source_operator_coverage_markdown(dynamic)
        checked_markdown = (
            PROJECT_ROOT / "docs" / "research" / "MULTI_OSCILLATOR_MO_R4A_S1_REAL_24_SOURCE_OPERATOR_COVERAGE.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(checked_markdown, rendered)

    def test_s1r1_checked_in_coverage_artifacts_match_the_deterministic_rebinding(self) -> None:
        dynamic = operators.build_real_source_operator_coverage_report(
            PROJECT_ROOT,
            source_ledger=self.hardened_ledger,
            milestone="MO-R4A-S1R1",
            coverage_contract=operators.CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT,
        )
        checked_in = _load_json(PROJECT_ROOT / "status" / "audits" / "mo_r4a_s1r1_real_24_source_operator_coverage.json")
        self.assertEqual(checked_in, dynamic)
        self.assertEqual(dynamic["sourceOperatorLedgerCanonicalHash"], operators._canonical_hash(self.hardened_ledger))
        rendered = operators.render_real_source_operator_coverage_markdown(dynamic)
        checked_markdown = (
            PROJECT_ROOT / "docs" / "research" / "MULTI_OSCILLATOR_MO_R4A_S1R1_REAL_24_SOURCE_OPERATOR_COVERAGE.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(checked_markdown, rendered)

    def test_p0_unsigned_contract_registry_and_accepted_candidate_remain_unchanged(self) -> None:
        registry = _load_json(
            PROJECT_ROOT
            / "configs"
            / "research"
            / "machine_interpretation"
            / "experimental_market_hypothesis_registry_v1.json"
        )
        acceptance = _load_json(PROJECT_ROOT / "status" / "acceptance" / "mo_r4_p0_founder_acceptance.json")
        self.assertEqual(registry["entries"], [])
        self.assertFalse(registry["guardrails"]["executionAllowed"])
        self.assertEqual(activity.MO_ACTIVITY_RANGE_CONTRACT, "MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1")
        self.assertEqual(activity.MO_EVIDENCE_MODE, "EXPLORATORY_UNSIGNED")
        self.assertEqual(acceptance["candidateVersion"], "0.10.64-pfr-v2b-mo-r3-r2-f1-r1")
        self.assertFalse(acceptance["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
