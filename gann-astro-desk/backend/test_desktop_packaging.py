from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repository import DataPaths


class DesktopPackagingTests(unittest.TestCase):
    def test_default_paths_respect_packaged_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            annotation = root / "state" / "annotations.sqlite"
            with patch.dict(
                os.environ,
                {
                    "GANN_ASTRO_PROJECT_ROOT": str(root),
                    "GANN_ASTRO_ANNOTATION_DB": str(annotation),
                    "GANN_ASTRO_ARTIFACTS_DIR": str(root / "artifacts"),
                    "GANN_ASTRO_MARKET_SNAPSHOTS_DIR": str(root / "market_snapshots"),
                    "GANN_ASTRO_PRICE_SOURCES_DIR": str(root / "price_sources"),
                },
                clear=False,
            ):
                paths = DataPaths.default()
        self.assertEqual(paths.project_root, root)
        self.assertEqual(paths.annotation_db, annotation)
        self.assertEqual(paths.artifacts_dir, root / "artifacts")
        self.assertEqual(paths.market_snapshots_dir, root / "market_snapshots")
        self.assertEqual(paths.price_sources_dir, root / "price_sources")
        self.assertEqual(paths.source_events.parent, root)

    def test_arghya_research_contract_is_packaged_fail_closed(self) -> None:
        app_root = Path(__file__).resolve().parents[1]
        sidecar_spec = (
            app_root / "packaging" / "gann_backend_sidecar.spec"
        ).read_text(encoding="utf-8")
        windows_build = (
            app_root / "packaging" / "build_tauri_windows.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn(
            '"research_labs.trailokya_arghya.reconcile"', sidecar_spec
        )
        self.assertIn(
            'arghya_reconciliation_contract = "TRAILOKYA_ARGHYA_RECONCILIATION_V1"',
            windows_build,
        )
        self.assertIn("arghya_price_formula_certified = $false", windows_build)
        self.assertIn("arghya_market_mapping_allowed = $false", windows_build)
        self.assertIn("arghya_auto_suggest_allowed = $false", windows_build)
        self.assertIn("arghya_live_inference_allowed = $false", windows_build)
        self.assertIn("arghya_official_ml_note_allowed = $false", windows_build)
        self.assertIn("arghya_execution_allowed = $false", windows_build)

    def test_collective_refinement_and_audit_are_packaged_fail_closed(self) -> None:
        app_root = Path(__file__).resolve().parents[1]
        sidecar_spec = (
            app_root / "packaging" / "gann_backend_sidecar.spec"
        ).read_text(encoding="utf-8")
        windows_build = (
            app_root / "packaging" / "build_tauri_windows.ps1"
        ).read_text(encoding="utf-8")

        for module in (
            "planetary_lines",
            "collective_geometry",
            "collective_influence",
            "collective_motion",
            "collective_refinement",
        ):
            self.assertIn(f'"{module}"', sidecar_spec)
        self.assertIn(
            'collective_event_refinement_contract = '
            '"GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1"',
            windows_build,
        )
        self.assertIn(
            'collective_event_refinement_policy = '
            '"AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1"',
            windows_build,
        )
        self.assertIn(
            'collective_audit_snapshot_contract = '
            '"GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1"',
            windows_build,
        )
        self.assertIn("collective_research_only = $true", windows_build)
        self.assertIn(
            "collective_counts_as_independent_vote = $false", windows_build
        )
        self.assertIn(
            "collective_directional_contribution = 0.0", windows_build
        )
        self.assertIn(
            "collective_live_inference_allowed = $false", windows_build
        )
        self.assertIn(
            "collective_auto_suggest_allowed = $false", windows_build
        )
        self.assertIn(
            "collective_shadow_ledger_allowed = $false", windows_build
        )
        self.assertIn(
            "collective_official_ml_note_allowed = $false", windows_build
        )
        self.assertIn("collective_execution_allowed = $false", windows_build)
        self.assertIn(
            'collective_visual_study_dossier_contract = '
            '"GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1"',
            windows_build,
        )
        self.assertIn(
            'collective_prospective_freeze_candidate_contract = '
            '"GANN_AVG_ALL_PROSPECTIVE_FREEZE_CANDIDATE_V1"',
            windows_build,
        )
        self.assertIn(
            "collective_visual_study_outcome_labels_included = $false",
            windows_build,
        )
        self.assertIn(
            "collective_visual_study_trial_registered = $false",
            windows_build,
        )
        self.assertIn(
            "collective_visual_study_existing_shadow_trial_modified = $false",
            windows_build,
        )

    def test_chart_conditioned_profiles_are_packaged_for_independent_fields(self) -> None:
        app_root = Path(__file__).resolve().parents[1]
        sidecar_spec = (
            app_root / "packaging" / "gann_backend_sidecar.spec"
        ).read_text(encoding="utf-8")
        sidecar_build = (
            app_root / "packaging" / "build_backend_sidecar.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn(
            'chart_conditioned_profile_root = (',
            sidecar_spec,
        )
        self.assertIn(
            '(str(chart_conditioned_profile_root), "profiles")',
            sidecar_spec,
        )
        for filename in (
            "target_aware_polarity_catalogue_v1.json",
            "target_aware_polarity_evidence_packets_v1.json",
            "founder_chart_hypotheses_v1.json",
        ):
            self.assertIn(filename, sidecar_spec)
            self.assertIn(
                f'_internal\\profiles\\{filename}',
                sidecar_build,
            )


if __name__ == "__main__":
    unittest.main()
