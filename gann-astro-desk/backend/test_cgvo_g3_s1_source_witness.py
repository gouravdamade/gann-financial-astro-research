from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest

from cgvo_service import _g3_r1_source_composition_adjudication, build_cgvo_status


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_SOURCE_ROOT = Path(os.environ.get("GANN_ASTRO_PRIVATE_SOURCE_ROOT", r"D:\GannFinancialAstro\sources\private"))


class CgvoG3S1SourceWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = PROJECT_ROOT / "configs" / "research" / "cgvo"
        cls.ledger = json.loads((root / "cgvo_g3_s1_root_witness_ledger_v1.json").read_text(encoding="utf-8"))
        cls.audit = json.loads((root / "cgvo_g3_s1_semantic_composition_audit_v1.json").read_text(encoding="utf-8"))
        cls.readiness = json.loads((root / "cgvo_g3_s1_readiness_matrix_v1.json").read_text(encoding="utf-8"))

    def test_private_witness_hash_matches_the_immutable_ledger_without_tracking_source_bytes(self) -> None:
        witness = self.ledger["witness"]
        source_path = PRIVATE_SOURCE_ROOT / witness["filename"]
        self.assertTrue(source_path.is_file(), source_path)
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest().upper()
        self.assertEqual(digest, witness["pdfSha256"])
        self.assertEqual(witness["sourceBytePolicy"], "PRIVATE_NOT_TRACKED")
        self.assertNotIn(str(PRIVATE_SOURCE_ROOT).lower(), json.dumps(self.ledger).lower())

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
        self.assertEqual(packets["CGVO_G3_S1_BS_V42_XIV_REFERENCE"]["editorialReferenceStatus"], "TRANSLATOR_OR_EDITORIAL_PROSE_NOT_ROOT_SANSKRIT")

    def test_source_closed_context_does_not_create_region_or_effect_operator(self) -> None:
        relations = self.audit["relations"]
        self.assertEqual(relations["localDifferentialVisibilityStatus"]["status"], "SOURCE_CLOSED_SOLAR_LOCAL_DIFFERENTIAL_VISIBILITY")
        self.assertEqual(relations["chapterVtoXivReferenceStatus"]["status"], "COMMENTARY_ONLY_REFERENCE")
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
        self.assertEqual(status["milestone"], "CGVO-G3-S1")
        source = status["sourceCompositionAdjudication"]
        self.assertEqual(source["rootWitnessStatus"], "ACQUIRED_CHECKSUM_VERIFIED")
        self.assertEqual(source["semanticVerdict"], "SOURCE_CLOSED_CONTEXTUAL_PROVENANCE_ONLY")
        self.assertEqual(source["siteToRegionInference"], "NOT_AUTHORIZED")
        self.assertIsNone(source["regionVisibility"])
        self.assertIsNone(source["sourceEffectActivation"])
        self.assertFalse(status["guardrails"]["executionAllowed"])
        adjudication = _g3_r1_source_composition_adjudication(PROJECT_ROOT)
        self.assertEqual(adjudication["siteToRegionRuleStatus"], "SOURCE_SILENT_SITE_TO_REGION_OPERATOR")


if __name__ == "__main__":
    unittest.main()
