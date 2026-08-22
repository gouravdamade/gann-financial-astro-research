from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cgvo_service import _g3_r1_source_composition_adjudication, build_cgvo_status


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_SOURCE_SKIP_REASON = "PRIVATE_G3_S1_SOURCE_WITNESS_NOT_AVAILABLE"


def _private_source_path(filename: str, private_root: Path | None = None) -> Path | None:
    if private_root is None:
        configured_root = os.environ.get("GANN_ASTRO_PRIVATE_SOURCE_ROOT")
        private_root = Path(configured_root) if configured_root else None
    return private_root / filename if private_root is not None else None


def _verify_private_witness_hash_or_skip(testcase: unittest.TestCase, witness: dict[str, object], private_root: Path | None = None) -> None:
    source_path = _private_source_path(str(witness["filename"]), private_root)
    if source_path is None or not source_path.is_file():
        testcase.skipTest(PRIVATE_SOURCE_SKIP_REASON)
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest().upper()
    testcase.assertEqual(digest, witness["pdfSha256"])


class CgvoG3S1SourceWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = PROJECT_ROOT / "configs" / "research" / "cgvo"
        cls.ledger = json.loads((root / "cgvo_g3_s1_root_witness_ledger_v1.json").read_text(encoding="utf-8"))
        cls.audit = json.loads((root / "cgvo_g3_s1_semantic_composition_audit_v1.json").read_text(encoding="utf-8"))
        cls.readiness = json.loads((root / "cgvo_g3_s1_readiness_matrix_v1.json").read_text(encoding="utf-8"))

    def test_static_source_ledger_is_portable_and_does_not_leak_private_absolute_paths(self) -> None:
        witness = self.ledger["witness"]
        self.assertEqual(witness["pdfSha256"], "D7425625010C621FF6651BF6BF916506791E3D4381078251AC7DC8EFBBA6577A")
        self.assertEqual(witness["pdfPageCount"], 1116)
        self.assertEqual(witness["sourceBytePolicy"], "PRIVATE_NOT_TRACKED")
        serialized = json.dumps(self.ledger).lower()
        self.assertNotIn("d:\\gannfinancialastro", serialized)
        self.assertIn("gann_astro_private_source_root", serialized)

    def test_private_witness_hash_passes_only_when_bytes_are_present_and_match(self) -> None:
        _verify_private_witness_hash_or_skip(self, self.ledger["witness"])

    def test_private_witness_absence_is_an_explicit_skip(self) -> None:
        class AbsentWitnessProbe(unittest.TestCase):
            def runTest(probe_self) -> None:
                _verify_private_witness_hash_or_skip(probe_self, self.ledger["witness"], Path("missing-private-source-root"))

        result = unittest.TestResult()
        AbsentWitnessProbe().run(result)
        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])
        self.assertEqual(result.skipped, [(unittest.defaultTestLoader.loadTestsFromTestCase(AbsentWitnessProbe)._tests[0], PRIVATE_SOURCE_SKIP_REASON)])

    def test_private_witness_hash_mismatch_fails_instead_of_skipping(self) -> None:
        with TemporaryDirectory() as directory:
            source_root = Path(directory)
            source_path = source_root / self.ledger["witness"]["filename"]
            source_path.write_bytes(b"not the controlled witness")
            with self.assertRaises(AssertionError):
                _verify_private_witness_hash_or_skip(self, self.ledger["witness"], source_root)

    def test_required_page_packets_separate_root_text_translation_and_ocr_roles(self) -> None:
        packets = {packet["packetId"]: packet for packet in self.ledger["passagePackets"]}
        self.assertEqual(set(packets), {
            "CGVO_G3_S1_BS_V11_LOCAL_VISIBILITY",
            "CGVO_G3_S1_BS_V42_XIV_REFERENCE",
            "CGVO_G3_S1_BS_XIV_1_KURMA_GEOGRAPHY",
            "CGVO_G3_S1_BS_XIV_NORTH_TAKSASILA_PUSKALAVATA_GANDHARA",
        })
        self.assertEqual(self.ledger["witness"]["ocrRole"], "NAVIGATION_ONLY")
        self.assertNotEqual(self.ledger["translationWitness"]["role"], "CONTROLLING")
        self.assertEqual(packets["CGVO_G3_S1_BS_V11_LOCAL_VISIBILITY"]["controllingAuthority"], "ORIGINAL_PAGE_IMAGE_IN_CHECKSUM_IDENTIFIED_SCAN")
        v42 = packets["CGVO_G3_S1_BS_V42_XIV_REFERENCE"]
        self.assertEqual(v42["rootReferenceStatus"], "SOURCE_CLOSED_ROOT_KURMA_REFERENCE")
        self.assertEqual(v42["rootReferenceTerm"], "कूर्मोपदेशाद्")
        self.assertEqual(v42["rootReferenceIast"], "kūrmopadeśād")
        self.assertEqual(v42["operativeClause"], "भफलं कूर्मोपदेशाद्वदेत्")
        self.assertNotEqual(v42["rootReferenceStatus"], "COMMENTARY_ONLY_REFERENCE")
        self.assertEqual(v42["editorialReferenceStatus"], "TRANSLATION_EDITORIAL_LOCATOR_NOT_CONTROLLING_ROOT_TRANSCRIPTION")

    def test_source_closed_context_does_not_create_region_or_effect_operator(self) -> None:
        relations = self.audit["relations"]
        self.assertEqual(relations["localDifferentialVisibilityStatus"]["status"], "SOURCE_CLOSED_SOLAR_LOCAL_DIFFERENTIAL_VISIBILITY")
        self.assertEqual(relations["chapterVtoXivReferenceStatus"]["status"], "SOURCE_CLOSED_ROOT_KURMA_REFERENCE")
        self.assertEqual(relations["chapterXivGeographyStatus"]["status"], "SOURCE_CLOSED_CONTEXTUAL_MAPPING")
        self.assertEqual(relations["siteToRegionRuleStatus"]["status"], "SOURCE_SILENT_SITE_TO_REGION_OPERATOR")
        self.assertEqual(relations["siteVisibilityToRegionVisibilityStatus"]["status"], "NOT_AUTHORIZED")
        self.assertEqual(relations["localVisibilityToSourceEffectStatus"]["status"], "NOT_AUTHORIZED")
        self.assertIsNone(self.audit["regionVisibility"])
        self.assertIsNone(self.audit["sourceEffectActivation"])
        self.assertEqual(self.readiness["g1SourceOccurrences"], 308)
        self.assertEqual(self.readiness["g2ResearchFootprints"], 12)
        self.assertEqual(self.readiness["g2R1aCoordinateBearingFootprints"], 1)
        self.assertEqual(self.readiness["s1bPhaseMappings"], "UNCHANGED_UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED")
        for value in self.audit["guardrails"].values():
            self.assertTrue(value is False or value is True)
        for key, value in self.audit["guardrails"].items():
            self.assertTrue(value if key == "readOnly" else not value, key)

    def test_runtime_exposes_only_static_fail_closed_source_metadata(self) -> None:
        status = build_cgvo_status(PROJECT_ROOT)
        self.assertEqual(status["milestone"], "CGVO-G3-S1-R1")
        source = status["sourceCompositionAdjudication"]
        self.assertEqual(source["rootWitnessStatus"], "ACQUIRED_CHECKSUM_VERIFIED")
        self.assertEqual(source["semanticVerdict"], "SOURCE_CLOSED_CONTEXTUAL_PROVENANCE_ONLY")
        self.assertEqual(source["chapterVtoXivReferenceStatus"], "SOURCE_CLOSED_ROOT_KURMA_REFERENCE")
        self.assertEqual(source["siteToRegionInference"], "NOT_AUTHORIZED")
        self.assertIsNone(source["regionVisibility"])
        self.assertIsNone(source["sourceEffectActivation"])
        self.assertFalse(status["guardrails"]["executionAllowed"])
        adjudication = _g3_r1_source_composition_adjudication(PROJECT_ROOT)
        self.assertEqual(adjudication["chapterVtoXivReferenceStatus"], "SOURCE_CLOSED_ROOT_KURMA_REFERENCE")
        self.assertEqual(adjudication["siteToRegionRuleStatus"], "SOURCE_SILENT_SITE_TO_REGION_OPERATOR")


if __name__ == "__main__":
    unittest.main()
