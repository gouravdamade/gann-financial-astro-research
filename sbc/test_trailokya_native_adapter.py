from __future__ import annotations

import unittest
from unittest.mock import patch

from .chakra_lab import ChakraLabActorSelection, ChakraLabRequest
from .models import GeoLocation
from .trailokya_native_adapter import (
    NATIVE_GRID_PROFILE_ID,
    TRAILOKYA_PROFILE_ID,
    build_trailokya_native_snapshot,
    load_trailokya_native_profile,
    resolve_trailokya_targets,
)


class TrailokyaNativeAdapterTests(unittest.TestCase):
    def test_native_board_is_exact_81_cell_source_projection(self) -> None:
        profile = load_trailokya_native_profile()
        self.assertEqual(profile["board"]["cellCount"], 81)
        self.assertEqual(len(profile["board"]["cells"]), 81)
        self.assertEqual(profile["board"]["orientation"]["authorVisible"], {"east": "TOP", "west": "BOTTOM", "north": "LEFT", "south": "RIGHT"})
        self.assertEqual(profile["targetAuthority"]["rowCount"], 28)
        self.assertFalse(profile["readiness"]["genericGridFallbackAllowed"])

    def test_enumerated_row_keeps_source_order_and_single_front_target(self) -> None:
        resolution = resolve_trailokya_targets("JYESHTHA", "LEFT")
        self.assertEqual(
            [item["canonicalToken"] for item in resolution["directTargets"]],
            ["YA", "SAGITTARIUS", "VISARGA", "PISCES", "CHA", "ASHVINI"],
        )
        front = resolve_trailokya_targets("JYESHTHA", "FRONT")
        self.assertEqual(len(front["directTargets"]), 1)
        self.assertEqual(front["directTargets"][0]["canonicalToken"], "PUSHYA")
        self.assertEqual(front["targetAuthority"], "ENUMERATED_SOURCE_ROWS")

    def test_historic_rows_and_glyph_distinctions_are_retained(self) -> None:
        punarvasu = resolve_trailokya_targets("PUNARVASU", "RIGHT")
        self.assertEqual(punarvasu["directTargets"][-1]["canonicalToken"], "PURVA_BHADRAPADA")
        pushya = resolve_trailokya_targets("PUSHYA", "RIGHT")
        self.assertEqual(pushya["directTargets"][-1]["canonicalToken"], "SHATABHISHA")
        paired = resolve_trailokya_targets("UTTARA_ASHADHA", "LEFT")
        self.assertIn("SSA_RETROFLEX", [item["canonicalToken"] for item in paired["derivedTargets"]])
        self.assertNotIn("PA_KHA", [item["canonicalToken"] for item in paired["derivedTargets"]])
        self.assertNotEqual("ANUSVARA", "VISARGA")

    def test_expansions_share_one_causal_event_and_unwritten_letters_remain_unmapped(self) -> None:
        resolution = resolve_trailokya_targets("MRIGASHIRSHA", "LEFT")
        direct = next(item for item in resolution["directTargets"] if item["canonicalToken"] == "KA")
        derived = [item for item in resolution["derivedTargets"] if item["derivedFromTargetId"] == direct["targetId"]]
        self.assertEqual({item["canonicalToken"] for item in derived}, {"GHA", "NGA", "CHHA"})
        self.assertTrue(all(item["causalVedhaEventId"] == resolution["causalVedhaEventId"] for item in resolution["allTargets"]))
        self.assertTrue(all(item["physicalCell"] is None for item in derived))

    def test_context_missing_is_unknown_not_negative(self) -> None:
        missing = resolve_trailokya_targets("KRITTIKA", "LEFT")
        self.assertTrue(all(item["reachState"] == "UNKNOWN" for item in missing["directTargets"]))
        known = resolve_trailokya_targets("KRITTIKA", "RIGHT", {"NAKSHATRA": ["BHARANI"]})
        self.assertEqual(known["directTargets"][0]["reachState"], "REACHED")

    def test_profile_and_native_grid_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "TRAILOKYA_SOURCE_PROFILE_REQUIRED"):
            resolve_trailokya_targets("KRITTIKA", "LEFT", source_profile="phaladeepika_editor_vedha_guidance_v1")
        request = ChakraLabRequest(
            at=__import__("datetime").datetime.fromisoformat("2026-08-16T05:30:00+05:30"),
            location=GeoLocation(latitude=18.5, longitude=73.8, timezone="Asia/Kolkata"),
            bodies=("SUN",), actors=(ChakraLabActorSelection(body="SUN"),),
            vedha_profile_id=TRAILOKYA_PROFILE_ID, grid_profile_id=NATIVE_GRID_PROFILE_ID,
        )
        with patch("sbc.trailokya_native_adapter.ChakraLabEngine.snapshot_without_guidance", side_effect=AssertionError("generic snapshot must not run")):
            snapshot = build_trailokya_native_snapshot(request)
        self.assertEqual(snapshot["board"]["gridProfileId"], NATIVE_GRID_PROFILE_ID)
        self.assertFalse(snapshot["guardrails"]["executionAllowed"])
