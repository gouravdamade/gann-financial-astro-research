"""Focused root-purity tests for MO-R4A-S3R1-R3-R3."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]).resolve()
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
for root in (
    PROJECT_ROOT,
    PROJECT_ROOT / "gann-astro-desk",
    BACKEND_ROOT,
    PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects",
    PROJECT_ROOT / "research_labs" / "instrument_relative_sbc",
):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import outcome_analysis_s3r1_r2 as r2  # noqa: E402
import outcome_analysis_s3r1_r3 as r3  # noqa: E402
import outcome_analysis_s3r1_r3_r1 as r3r1  # noqa: E402
import outcome_analysis_s3r1_r3_r2 as r3r2  # noqa: E402


PREDICTION_FREEZE_RELATIVE = Path("status/audits/mo_r4a_s2r1_r1_blinded_market_bridge_prediction_freeze.json")
HISTORICAL_PARSER_RELATIVE = Path("gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3.py")
SUCCESSOR_PARSER_RELATIVE = Path("gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py")
R3R1_ACCEPTANCE_RELATIVE = Path(
    "status/acceptance/mo_r4a_s3r1_r3_r1_outcome_analysis_preregistration.json"
)

EXPECTED_HISTORICAL_PARSER_SHA256 = "47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E"
EXPECTED_SUCCESSOR_PARSER_SHA256 = "F3D49AFBC055D9C1CF2E513194C9A98C8D55769FF974343B99A4D00EE4A35BC8"
EXPECTED_PARSER_CONTRACT_HASH = "18259325D9C8B245C05F4ECF596AD86395406A485E58DF3DF18C6B638C86BABE"
EXPECTED_ACQUISITION_HASH = "BE4C378E368956F46F69D004D0C7522B32EA784C15894106B98DA8AA9A983CAC"
EXPECTED_PREREGISTRATION_HASH = "23564E1F41C441EC1FB98B3FBD025F43643AEF75C27AD080550F7DCB7D64F272"
EXPECTED_POPULATION_HASH = "7F3CB6DE622A71FDA7F66E89BDAE2D0B7E3228E94BCAC403220DB17CF2686317"
EXPECTED_CLUSTERS_HASH = "6D4968B9C7DB7B912FFF2567088AECFEE7AC00C5329BD0245E6BDE3A6613CC0E"
EXPECTED_INVARIANCE_HASH = "C53F5EB8C6ADAB19D090A834FBCFABA6D9207ADC9640C6E08CD8534D137748F9"
EXPECTED_CORE_HASH = "9B7D06C3F3BD7470478C75F9313EFBF9EB6C29E8BE766A74693FF77DA60A5C64"
EXPECTED_ACCEPTANCE_HASH = "632D2B0C10D2F44287D8493495EC06E5CEDF6D7AD9DBC7374F2F2968327F9D8B"
TEST_TEMP_PARENT = PROJECT_ROOT / "tmp" / "mo_r4a_s3r1_r3_r3_tests"
TEST_TEMP_PARENT.mkdir(parents=True, exist_ok=True)


def _copy_contract_tree(destination: Path) -> None:
    for relative in (Path("configs/research"), Path("status/audits"), Path("status/acceptance")):
        shutil.copytree(PROJECT_ROOT / relative, destination / relative)
    for relative in (HISTORICAL_PARSER_RELATIVE, SUCCESSOR_PARSER_RELATIVE):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / relative, target)


def _mutate_prediction_freeze(path: Path) -> None:
    freeze = json.loads(path.read_text(encoding="utf-8"))
    prediction = freeze["predictions"][0]
    shifted = datetime.fromisoformat(prediction["applyingStartUtc"].replace("Z", "+00:00")) + timedelta(seconds=1)
    prediction["applyingStartUtc"] = shifted.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prediction_body = {key: copy.deepcopy(value) for key, value in prediction.items() if key != "eventPredictionHash"}
    prediction["eventPredictionHash"] = r3r2._canonical_hash(prediction_body)
    freeze_body = {key: copy.deepcopy(value) for key, value in freeze.items() if key != "predictionFreezeHash"}
    freeze["predictionFreezeHash"] = r3r2._canonical_hash(freeze_body)
    path.write_text(json.dumps(freeze, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _mutate_acceptance(path: Path) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    value["executionAllowed"] = True
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _assert_contexts_clear(test: unittest.TestCase) -> None:
    test.assertIsNone(r2._R1_VALIDATION_CONTEXT.get())
    test.assertIsNone(r3._R2_VALIDATION_CONTEXT.get())
    test.assertIsNone(r3r1._R3_VALIDATION_CONTEXT.get())
    test.assertIsNone(r3r2._R3_R1_VALIDATION_CONTEXT.get())


class OutcomeAnalysisS3R1R3R3Tests(unittest.TestCase):
    def test_canonical_r3r2_package_is_stable_and_locked(self) -> None:
        paths = r3r2._artifact_paths(PROJECT_ROOT)
        before = {name: path.read_bytes() for name, path in paths.items() if path.is_file()}
        r3r2.validate_artifacts(PROJECT_ROOT)
        r3r2.write_artifacts(PROJECT_ROOT)
        r3r2.write_artifacts(PROJECT_ROOT)
        after = {name: path.read_bytes() for name, path in paths.items() if path.is_file()}
        self.assertEqual(before, after)

        parser_contract = json.loads(paths["parserContract"].read_text(encoding="utf-8"))
        acquisition = json.loads(paths["acquisition"].read_text(encoding="utf-8"))
        preregistration = json.loads(paths["preregistration"].read_text(encoding="utf-8"))
        population = json.loads(paths["population"].read_text(encoding="utf-8"))
        clusters = json.loads(paths["clusters"].read_text(encoding="utf-8"))
        invariance = json.loads(paths["invariance"].read_text(encoding="utf-8"))
        core = json.loads(paths["core"].read_text(encoding="utf-8"))
        acceptance = json.loads(paths["acceptance"].read_text(encoding="utf-8"))
        self.assertEqual(parser_contract["parserContractHash"], EXPECTED_PARSER_CONTRACT_HASH)
        self.assertEqual(acquisition["marketDataAcquisitionContractHash"], EXPECTED_ACQUISITION_HASH)
        self.assertEqual(preregistration["preregistrationHash"], EXPECTED_PREREGISTRATION_HASH)
        self.assertEqual(population["primaryPopulationHash"], EXPECTED_POPULATION_HASH)
        self.assertEqual(clusters["overlapClustersHash"], EXPECTED_CLUSTERS_HASH)
        self.assertEqual(invariance["analysisPlanInvarianceAuditHash"], EXPECTED_INVARIANCE_HASH)
        self.assertEqual(core["analysisCoreManifestHash"], EXPECTED_CORE_HASH)
        self.assertEqual(acceptance["acceptanceManifestHash"], EXPECTED_ACCEPTANCE_HASH)
        self.assertEqual(r3r2.parser_source_sha256(PROJECT_ROOT), EXPECTED_SUCCESSOR_PARSER_SHA256)
        self.assertFalse(acceptance["outcomeUnlocked"])
        self.assertFalse(acceptance["executionAllowed"])
        self.assertTrue(all(value is False for value in acceptance["outcomeAccessFlags"].values()))

    def test_two_root_prediction_freeze_attack_isolated_in_both_directions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prediction-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            root_a = root / "A"
            root_b = root / "B"
            _copy_contract_tree(root_a)
            _copy_contract_tree(root_b)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

            freeze_a = root_a / PREDICTION_FREEZE_RELATIVE
            original_a = freeze_a.read_bytes()
            _mutate_prediction_freeze(freeze_a)
            with self.assertRaises(ValueError):
                r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)
            freeze_a.write_bytes(original_a)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

            freeze_b = root_b / PREDICTION_FREEZE_RELATIVE
            original_b = freeze_b.read_bytes()
            _mutate_prediction_freeze(freeze_b)
            r3r2.validate_artifacts(root_a)
            with self.assertRaises(ValueError):
                r3r2.validate_artifacts(root_b)
            freeze_b.write_bytes(original_b)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

    def test_exact_astra_reproduction_mutating_a_cannot_break_b(self) -> None:
        with tempfile.TemporaryDirectory(prefix="astra-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            root_a = root / "A"
            root_b = root / "B"
            _copy_contract_tree(root_a)
            _copy_contract_tree(root_b)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)
            freeze_a = root_a / PREDICTION_FREEZE_RELATIVE
            original = freeze_a.read_bytes()
            _mutate_prediction_freeze(freeze_a)
            r3r2.validate_artifacts(root_b)
            freeze_a.write_bytes(original)
            r3r2.validate_artifacts(root_b)
            r3r2.validate_artifacts(root_a)

    def test_historical_parser_source_mutation_is_root_local(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parser-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            root_a = root / "A"
            root_b = root / "B"
            _copy_contract_tree(root_a)
            _copy_contract_tree(root_b)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)
            parser_a = root_a / HISTORICAL_PARSER_RELATIVE
            original = parser_a.read_bytes()
            parser_a.write_bytes(original + b"\n# isolated root mutation\n")
            with self.assertRaises(ValueError):
                r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)
            parser_a.write_bytes(original)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

    def test_historical_r3r1_acceptance_mutation_is_root_local(self) -> None:
        with tempfile.TemporaryDirectory(prefix="acceptance-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            root_a = root / "A"
            root_b = root / "B"
            _copy_contract_tree(root_a)
            _copy_contract_tree(root_b)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)
            acceptance_a = root_a / R3R1_ACCEPTANCE_RELATIVE
            original = acceptance_a.read_bytes()
            _mutate_acceptance(acceptance_a)
            with self.assertRaises(ValueError):
                r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)
            acceptance_a.write_bytes(original)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

    def test_all_schema_builders_are_root_pure_for_explicit_and_implicit_payloads(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            root_a = root / "A"
            root_b = root / "B"
            _copy_contract_tree(root_a)
            _copy_contract_tree(root_b)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

            r2_payload = r2.build_s3r1_r2_preregistration(root_b)
            r3_payload = r3.build_s3r1_r3_preregistration(root_b)
            r3r1_payload = r3r1.build_preregistration(root_b)
            r3r2_payload = r3r2.build_preregistration(root_b)
            builders = (
                lambda: r2.build_s3r1_r2_schema(r2_payload, resource_root=root_b),
                lambda: r2.build_s3r1_r2_schema(resource_root=root_b),
                lambda: r3.build_s3r1_r3_schema(r3_payload, resource_root=root_b),
                lambda: r3.build_s3r1_r3_schema(resource_root=root_b),
                lambda: r3r1.build_schema(r3r1_payload, resource_root=root_b),
                lambda: r3r1.build_schema(resource_root=root_b),
                lambda: r3r2.build_schema(root_b, r3r2_payload),
                lambda: r3r2.build_schema(root_b),
            )
            before = [builder() for builder in builders]
            freeze_a = root_a / PREDICTION_FREEZE_RELATIVE
            original = freeze_a.read_bytes()
            _mutate_prediction_freeze(freeze_a)
            after = [builder() for builder in builders]
            self.assertEqual(before, after)
            freeze_a.write_bytes(original)
            r3r2.validate_artifacts(root_a)
            r3r2.validate_artifacts(root_b)

    def test_b_materialization_is_unchanged_when_a_is_corrupted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="materialize-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            root_a = root / "A"
            root_b = root / "B"
            _copy_contract_tree(root_a)
            _copy_contract_tree(root_b)
            r3r2.validate_artifacts(root_a)
            paths = r3r2.write_artifacts(root_b)
            before = {name: path.read_bytes() for name, path in paths.items() if path.is_file()}

            freeze_a = root_a / PREDICTION_FREEZE_RELATIVE
            original_a = freeze_a.read_bytes()
            _mutate_prediction_freeze(freeze_a)
            r3r2.write_artifacts(root_b)
            after = {name: path.read_bytes() for name, path in paths.items() if path.is_file()}
            self.assertEqual(before, after)
            freeze_a.write_bytes(original_a)

            freeze_b = root_b / PREDICTION_FREEZE_RELATIVE
            original_b = freeze_b.read_bytes()
            _mutate_prediction_freeze(freeze_b)
            with self.assertRaises(ValueError):
                r3r2.write_artifacts(root_b)
            freeze_b.write_bytes(original_b)
            r3r2.validate_artifacts(root_b)

    def test_same_root_mutation_rejects_and_exception_cleanup_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="context-", dir=TEST_TEMP_PARENT) as temporary:
            root = Path(temporary)
            _copy_contract_tree(root)
            _assert_contexts_clear(self)
            r3r2.validate_artifacts(root)
            _assert_contexts_clear(self)
            freeze = root / PREDICTION_FREEZE_RELATIVE
            original = freeze.read_bytes()
            _mutate_prediction_freeze(freeze)
            with self.assertRaises(ValueError):
                r3r2.validate_artifacts(root)
            _assert_contexts_clear(self)
            freeze.write_bytes(original)
            r3r2.validate_artifacts(root)
            _assert_contexts_clear(self)

    def test_static_root_purity_guards_target_file_backed_misuse(self) -> None:
        r2_source = Path(r2.__file__).read_text(encoding="utf-8")
        r3_source = Path(r3.__file__).read_text(encoding="utf-8")
        r3r1_source = Path(r3r1.__file__).read_text(encoding="utf-8")
        self.assertNotIn("build_s3r1_r2_preregistration(PROJECT_ROOT)", r2_source)
        self.assertNotIn("PARSER_SOURCE_PATH.read_text", r3_source)
        self.assertNotIn("PARSER_SOURCE_PATH.read_bytes", r3_source)
        self.assertNotIn("build_s3r1_r3_preregistration(PROJECT_ROOT)", r3r1_source)
        self.assertNotIn("build_preregistration(PROJECT_ROOT)", r3r1_source)

        for source in (r2_source, r3_source, r3r1_source, Path(r3r2.__file__).read_text(encoding="utf-8")):
            tree = ast.parse(source)
            self.assertIsNotNone(tree)
            self.assertIn("PROJECT_ROOT", source)
        self.assertEqual(r2.build_s3r1_r2_schema.__defaults__, (None,))
        self.assertEqual(r3.build_s3r1_r3_schema.__defaults__, (None,))
        self.assertEqual(r3r1.build_schema.__defaults__, (None,))

    def test_parser_and_acquisition_contract_identities_remain_exact(self) -> None:
        historical_parser = hashlib.sha256((BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r3.py").read_bytes()).hexdigest().upper()
        successor_parser = hashlib.sha256((BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r3_r2.py").read_bytes()).hexdigest().upper()
        self.assertEqual(historical_parser, EXPECTED_HISTORICAL_PARSER_SHA256)
        self.assertEqual(successor_parser, EXPECTED_SUCCESSOR_PARSER_SHA256)
        paths = r3r2._artifact_paths(PROJECT_ROOT)
        parser_contract = json.loads(paths["parserContract"].read_text(encoding="utf-8"))
        acquisition = json.loads(paths["acquisition"].read_text(encoding="utf-8"))
        self.assertEqual(parser_contract["parserContractHash"], EXPECTED_PARSER_CONTRACT_HASH)
        self.assertEqual(parser_contract["parserSourceSha256"], EXPECTED_SUCCESSOR_PARSER_SHA256)
        self.assertEqual(acquisition["marketDataAcquisitionContractHash"], EXPECTED_ACQUISITION_HASH)
        self.assertFalse(acquisition["providerAccessPerformed"])
        self.assertFalse(acquisition["marketOutcomeRead"])
        self.assertFalse(acquisition["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
