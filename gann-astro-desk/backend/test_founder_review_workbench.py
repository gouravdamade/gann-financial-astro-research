"""Synthetic-only integrity tests for the durable Founder Review store.

The real April 2025 packets are intentionally never used as decision-bearing
test input here.  The fixture below exercises the same packet, manifest, and
identity-audit contracts with wholly synthetic event identities.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import founder_review_workbench as fr


class SyntheticFounderReviewFixture(unittest.TestCase):
    """Build isolated immutable resources and a separate mutable data root."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="founder-review-synthetic-"))
        self.resources = self.temp_dir / "resources"
        self.data = self.temp_dir / "application-data"
        self.review_root = self.data / "founder_review"
        self._write_resources()
        self.baseline_audit = copy.deepcopy(self.audit)
        self.baseline_audit_hash = self.audit_hash

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @staticmethod
    def _write_json(path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fr._json_bytes(value))

    def _write_resources(self) -> None:
        packet_dir = self.resources / "research_labs" / "chart_conditioned_aspects" / "founder_review"
        audit_path = self.resources / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json"
        side_reports: dict[str, dict] = {}
        for side in fr.SIDES:
            chart_id = f"SYNTHETIC_CHART_{side}"
            hypothesis_id = f"SYNTHETIC_HYPOTHESIS_{side}"
            event_compiler = {
                "contract": "CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1",
                "astronomyContract": "SYNTHETIC_TRUE_NODE_ASTRONOMY_V1",
                "generatorVersion": "synthetic-founder-review-generator-v1",
                "ephemerisVersion": "synthetic-ephemeris-v1",
                "ephemerisProvider": "synthetic-provider",
            }
            event_records: list[dict] = []
            rows: list[dict] = []
            verified_ids: list[str] = []
            for index in range(1, 13):
                event_id = f"SYNTH-{side}-{index:02d}"
                event_hash = fr._sha256_bytes(event_id.encode("ascii"))
                exact_utc = f"2025-04-{index:02d}T12:00:00Z"
                event = {
                    "sideIdentity": side,
                    "instrumentIdentity": f"FX_CURRENCY:{side}",
                    "chartId": chart_id,
                    "chartHypothesisId": hypothesis_id,
                    "eventId": event_id,
                    "eventHash": event_hash,
                    "eventContract": event_compiler["contract"],
                    "astronomyContract": event_compiler["astronomyContract"],
                    "generatorVersion": event_compiler["generatorVersion"],
                    "transitBody": "SYNTHETIC_MOON",
                    "natalTarget": "SYNTHETIC_TARGET",
                    "aspectType": "CONJUNCTION",
                    "applyingStartUtc": f"2025-04-{index:02d}T00:00:00Z",
                    "exactUtc": exact_utc,
                    "separatingEndUtc": f"2025-04-{index:02d}T23:00:00Z",
                    "applyingStartIst": f"2025-04-{index:02d}T05:30:00+05:30",
                    "exactIst": f"2025-04-{index:02d}T17:30:00+05:30",
                    "separatingEndIst": f"2025-04-{index:02d}T04:30:00+05:30",
                }
                audit_record = {
                    **copy.deepcopy(event),
                    "status": fr.REVIEWABLE_IDENTITY_STATUS,
                    "checks": {key: True for key in fr.MANDATORY_IDENTITY_CHECKS},
                    "audit": {
                        "contract": fr.IDENTITY_AUDIT_CONTRACT,
                        "auditVersion": fr.IDENTITY_AUDIT_VERSION,
                        "motionPhaseAtExact": "SYNTHETIC_DIRECT",
                    },
                }
                event_records.append(audit_record)
                rows.append({"eventIdentity": event})
                verified_ids.append(event_id)

            packet = {
                "contract": "FOUNDER_BLANK_POLARITY_REVIEW_PACKET_V1",
                "packetVersion": 1,
                "packetStatus": "BLANK_FOUNDER_REVIEW_REQUIRED",
                "sideIdentity": side,
                "instrumentIdentity": f"FX_CURRENCY:{side}",
                "chartId": chart_id,
                "chartHypothesisId": hypothesis_id,
                "eventCompiler": event_compiler,
                "rows": rows,
            }
            packet_path = packet_dir / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
            self._write_json(packet_path, packet)
            packet_hash = fr._sha256_file(packet_path)
            manifest = {
                "contract": "FOUNDER_BLANK_POLARITY_REVIEW_V1_IDENTITY_VERIFICATION_MANIFEST_V1",
                "sideIdentity": side,
                "allRowsSinglePassVerified": True,
                "identityAuditContract": fr.IDENTITY_AUDIT_CONTRACT,
                "identityAuditVersion": fr.IDENTITY_AUDIT_VERSION,
                "packetSha256": packet_hash,
                "originalGenerationManifestOutputSha256": packet_hash,
                "verifiedEventIds": verified_ids,
            }
            self._write_json(
                packet_dir / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json",
                manifest,
            )
            side_reports[side] = {
                "acceptedChart": {
                    "instrumentIdentity": f"FX_CURRENCY:{side}",
                    "chartId": chart_id,
                    "chartHypothesisId": hypothesis_id,
                },
                "eventRecords": event_records,
            }

        self.audit = {
            "contract": fr.IDENTITY_AUDIT_ARTIFACT_CONTRACT,
            "auditVersion": fr.IDENTITY_AUDIT_VERSION,
            "sideReports": side_reports,
        }
        self._write_json(audit_path, self.audit)
        self.audit_path = audit_path
        self.audit_hash = fr._sha256_file(audit_path)

    def _restore_audit(self) -> None:
        self.audit = copy.deepcopy(self.baseline_audit)
        self._write_json(self.audit_path, self.audit)
        self.audit_hash = fr._sha256_file(self.audit_path)

    def _build(self, root: Path | None = None) -> dict:
        resource_root = root or self.resources
        audit_hash = fr._sha256_file(
            resource_root / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json"
        )
        return fr.build_founder_review_workbench(
            resource_root,
            review_root=self.review_root,
            expected_audit_sha256=audit_hash,
        )

    def _side(self, side: str, workbench: dict | None = None) -> dict:
        value = workbench or self._build()
        return next(item for item in value["sides"] if item["sideIdentity"] == side)

    @staticmethod
    def _row(side: dict, index: int = 0) -> dict:
        return copy.deepcopy(side["rows"][index])

    @staticmethod
    def _source_reference(prefix: str) -> dict:
        return {
            "sourceId": f"SYNTH_SOURCE_{prefix}",
            "edition": "Synthetic fixture edition",
            "locator": "printed p.1, synthetic row 1",
            "connection": "Synthetic founder-only test connection",
        }

    def _reviewed_row(
        self,
        side: dict,
        index: int = 0,
        decision: str = "UNKNOWN_MORE_EVIDENCE_REQUIRED",
        classification: str = "FOUNDER_RESEARCH_HYPOTHESIS",
        reasoning: str = "Synthetic founder review reasoning",
        references: list[dict] | None = None,
    ) -> dict:
        row = self._row(side, index)
        row["founderReview"].update(
            {
                "reviewedPolarity": decision,
                "evidenceClassification": classification,
                "founderReasoning": reasoning,
                "reviewer": "synthetic-founder",
                "sourceReferences": copy.deepcopy(references or []),
            }
        )
        return row

    def _export(self, side: str, rows: list[dict], base: str | None = None) -> dict:
        current = self._side(side)
        return fr.export_founder_review_packet(
            self.resources,
            {
                "side": side,
                "baseRevisionHash": current["currentRevisionHash"] if base is None else base,
                "rows": rows,
            },
            review_root=self.review_root,
            expected_audit_sha256=self.audit_hash,
        )

    def _mutate_audit_record(self, mutator) -> None:
        self.audit = copy.deepcopy(self.baseline_audit)
        mutator(self.audit["sideReports"]["USD"]["eventRecords"][0])
        self._write_json(self.audit_path, self.audit)
        self.audit_hash = fr._sha256_file(self.audit_path)

    def _resource_snapshot(self, root: Path | None = None) -> dict[str, bytes]:
        base = root or self.resources
        return {
            str(path.relative_to(base)): path.read_bytes()
            for path in base.rglob("*")
            if path.is_file()
        }

    def test_blank_rows_start_blank_and_all_guardrails_are_locked(self) -> None:
        workbench = self._build()
        self.assertEqual(workbench["schemaVersion"], 2)
        self.assertTrue(workbench["guardrails"]["blankPacketsReadOnly"])
        self.assertTrue(workbench["guardrails"]["durableReviewStore"])
        self.assertFalse(workbench["guardrails"]["executionAllowed"])
        self.assertFalse(workbench["guardrails"]["priceDataRead"])
        self.assertFalse(workbench["guardrails"]["sbcRead"])
        self.assertFalse(workbench["guardrails"]["llmRead"])
        self.assertEqual(sum(len(side["rows"]) for side in workbench["sides"]), 24)
        for side in workbench["sides"]:
            for row in side["rows"]:
                review = row["founderReview"]
                self.assertIsNone(review["reviewedPolarity"])
                self.assertIsNone(review["evidenceClassification"])
                self.assertEqual(review["founderReasoning"], "")
                self.assertEqual(review["sourceReferences"], [])
                self.assertIsNone(review["firstReviewedAtUtc"])
                self.assertIsNone(review["lastModifiedAtUtc"])
                self.assertNotIn("real", row["eventIdentity"]["eventId"].lower())

    def test_save_restart_and_application_version_replacement_retain_state(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        result = self._export("USD", [self._reviewed_row(usd)])
        self.assertEqual(result["counts"]["unknownRows"], 1)
        restarted = self._build()
        saved = self._side("USD", restarted)
        self.assertEqual(saved["rows"][0]["founderReview"]["reviewedPolarity"], "UNKNOWN_MORE_EVIDENCE_REQUIRED")
        self.assertIsNotNone(saved["rows"][0]["founderReview"]["firstReviewedAtUtc"])
        self.assertIsNotNone(saved["rows"][0]["founderReview"]["lastModifiedAtUtc"])
        replacement = self.temp_dir / "replacement-resources"
        shutil.copytree(self.resources, replacement)
        replaced = self._build(replacement)
        replaced_usd = self._side("USD", replaced)
        self.assertEqual(replaced_usd["currentRevisionHash"], saved["currentRevisionHash"])
        self.assertEqual(replaced_usd["rows"][0]["founderReview"], saved["rows"][0]["founderReview"])

    def test_readonly_resources_save_to_separate_durable_root(self) -> None:
        paths = list(self.resources.rglob("*"))
        files = [path for path in paths if path.is_file()]
        original_modes = {path: stat.S_IMODE(path.stat().st_mode) for path in files}
        try:
            for path in files:
                os.chmod(path, stat.S_IREAD)
            workbench = self._build()
            usd = self._side("USD", workbench)
            self._export("USD", [self._reviewed_row(usd, decision="NEUTRAL")])
            self.assertTrue((self.review_root / "current" / "USD.json").is_file())
        finally:
            for path, mode in original_modes.items():
                os.chmod(path, mode | stat.S_IWRITE)

    def test_revision_chain_is_append_only_and_server_ordered(self) -> None:
        first = self._build()
        usd_first = self._side("USD", first)
        first_result = self._export("USD", [self._reviewed_row(usd_first, decision="NEUTRAL")])
        second_before = self._build()
        usd_second = self._side("USD", second_before)
        second_row = self._reviewed_row(usd_second, decision="MIXED", reasoning="Second synthetic review")
        second_result = self._export("USD", [second_row])
        self.assertEqual(second_result["previousRevisionHash"], first_result["revisionHash"])
        self.assertGreater(second_result["serverCreatedAtUtc"], first_result["serverCreatedAtUtc"])
        first_dir = self.review_root / "revisions" / "USD" / first_result["revisionId"]
        second_dir = self.review_root / "revisions" / "USD" / second_result["revisionId"]
        self.assertTrue((first_dir / "reviewed_packet.json").is_file())
        self.assertTrue((second_dir / "reviewed_packet.json").is_file())
        first_packet = json.loads((first_dir / "reviewed_packet.json").read_text(encoding="utf-8"))
        self.assertEqual(first_packet["reviewedPacketHash"], first_result["reviewedPacketHash"])

    def test_same_normalized_packet_content_has_a_deterministic_packet_hash(self) -> None:
        workbench = self._build()
        usd = self._side("USD", workbench)
        rows = [self._reviewed_row(usd, decision="NEUTRAL")]
        first = fr._build_packet(
            usd,
            fr._validate_submitted_rows(usd, rows, server_now="2026-09-09T00:00:00Z"),
            revision_id="rev-fixed",
            server_created_at_utc="2026-09-09T00:00:00Z",
        )
        second = fr._build_packet(
            usd,
            fr._validate_submitted_rows(usd, rows, server_now="2026-09-09T00:00:00Z"),
            revision_id="rev-fixed",
            server_created_at_utc="2026-09-09T00:00:00Z",
        )
        self.assertEqual(first["reviewedPacketHash"], second["reviewedPacketHash"])
        self.assertEqual(first["revisionHash"], second["revisionHash"])

    def test_stale_revision_is_rejected_without_last_writer_wins(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        stale_rows = [self._reviewed_row(usd, decision="NEUTRAL")]
        fresh = self._export("USD", stale_rows)
        with self.assertRaises(fr.FounderReviewRevisionConflictError) as caught:
            fr.export_founder_review_packet(
                self.resources,
                {
                    "side": "USD",
                    "baseRevisionHash": None,
                    "rows": [self._reviewed_row(usd, decision="ADVERSE")],
                },
                review_root=self.review_root,
                expected_audit_sha256=self.audit_hash,
            )
        self.assertEqual(caught.exception.current_revision_hash, fresh["revisionHash"])
        current = self._side("USD")
        self.assertEqual(current["rows"][0]["founderReview"]["reviewedPolarity"], "NEUTRAL")

    def test_failed_publication_leaves_previous_complete_revision_authoritative(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        first = self._export("USD", [self._reviewed_row(usd, decision="NEUTRAL")])
        original = fr._atomic_write_json

        def fail_current(path: Path, value: dict) -> None:
            if path.name == "USD.json":
                raise OSError("synthetic pointer publication failure")
            original(path, value)

        with mock.patch.object(fr, "_atomic_write_json", side_effect=fail_current):
            with self.assertRaises(OSError):
                self._export("USD", [self._reviewed_row(usd, decision="MIXED")])
        current = self._side("USD")
        self.assertEqual(current["currentRevisionHash"], first["revisionHash"])
        self.assertEqual(current["rows"][0]["founderReview"]["reviewedPolarity"], "NEUTRAL")

    def test_partial_update_retains_omitted_authoritative_rows(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        first_rows = [
            self._reviewed_row(usd, 0, decision="NEUTRAL"),
            self._reviewed_row(usd, 1, decision="MIXED"),
        ]
        self._export("USD", first_rows)
        current = self._side("USD")
        self._export("USD", [self._reviewed_row(current, 1, decision="ADVERSE")])
        after = self._side("USD")
        by_id = {row["eventIdentity"]["eventId"]: row for row in after["rows"]}
        self.assertEqual(by_id["SYNTH-USD-01"]["founderReview"]["reviewedPolarity"], "NEUTRAL")
        self.assertEqual(by_id["SYNTH-USD-02"]["founderReview"]["reviewedPolarity"], "ADVERSE")

    def test_all_source_references_survive_an_edit(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        refs = [self._source_reference("ONE"), self._source_reference("TWO")]
        self._export(
            "USD",
            [
                self._reviewed_row(
                    usd,
                    decision="SUPPORTIVE",
                    classification="SOURCE_BACKED_CLASSICAL_CANDIDATE",
                    references=refs,
                )
            ],
        )
        current = self._side("USD")
        edited_refs = [self._source_reference("EDITED"), refs[1]]
        self._export(
            "USD",
            [
                self._reviewed_row(
                    current,
                    decision="SUPPORTIVE",
                    classification="SOURCE_BACKED_CLASSICAL_CANDIDATE",
                    reasoning="Edited synthetic reasoning",
                    references=edited_refs,
                )
            ],
        )
        saved = self._side("USD")
        self.assertEqual(saved["rows"][0]["founderReview"]["sourceReferences"], edited_refs)

    def test_classical_candidate_requires_exact_source_locators(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        bad_reference = {"sourceId": "SYNTH_SOURCE", "edition": "Synthetic edition"}
        with self.assertRaises(fr.FounderReviewIntegrityError):
            self._export(
                "USD",
                [
                    self._reviewed_row(
                        usd,
                        decision="SUPPORTIVE",
                        classification="SOURCE_BACKED_CLASSICAL_CANDIDATE",
                        references=[bad_reference],
                    )
                ],
            )

    def test_unknown_is_deliberately_reviewed_but_remains_unknown(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        result = self._export("USD", [self._reviewed_row(usd)])
        self.assertEqual(result["counts"]["unknownRows"], 1)
        self.assertEqual(result["counts"]["decidedRows"], 1)
        self.assertEqual(self._side("USD")["rows"][0]["founderReview"]["reviewedPolarity"], "UNKNOWN_MORE_EVIDENCE_REQUIRED")

    def test_founder_hypothesis_is_the_only_nonclassical_evidence_class(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        self._export("USD", [self._reviewed_row(usd, decision="MIXED")])
        review = self._side("USD")["rows"][0]["founderReview"]
        self.assertEqual(review["evidenceClassification"], "FOUNDER_RESEARCH_HYPOTHESIS")
        self.assertEqual(review["sourceReferences"], [])

    def test_unresolved_identity_is_nonreviewable_and_cannot_be_exported(self) -> None:
        self._mutate_audit_record(lambda record: record.update({"status": "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED"}))
        workbench = self._build()
        usd = self._side("USD", workbench)
        self.assertFalse(usd["rows"][0]["eligible"])
        with self.assertRaises(fr.FounderReviewIntegrityError):
            self._export("USD", [self._reviewed_row(usd, decision="REJECT_EVENT_IDENTITY", classification=None, reasoning="Not admitted")])
        self._restore_audit()

    def test_missing_empty_false_nonboolean_and_missing_each_mandatory_check_fail_closed(self) -> None:
        for missing in ("missing-map", "empty-map"):
            with self.subTest(case=missing):
                if missing == "missing-map":
                    self._mutate_audit_record(lambda record: record.pop("checks"))
                else:
                    self._mutate_audit_record(lambda record: record.update({"checks": {}}))
                self.assertFalse(self._side("USD", self._build())["rows"][0]["eligible"])
        for key in fr.MANDATORY_IDENTITY_CHECKS:
            with self.subTest(case=f"missing-{key}"):
                self._mutate_audit_record(lambda record, key=key: record["checks"].pop(key))
                self.assertFalse(self._side("USD", self._build())["rows"][0]["eligible"])
        self._mutate_audit_record(lambda record: record["checks"].update({fr.MANDATORY_IDENTITY_CHECKS[0]: False}))
        self.assertFalse(self._side("USD", self._build())["rows"][0]["eligible"])
        self._mutate_audit_record(lambda record: record["checks"].update({fr.MANDATORY_IDENTITY_CHECKS[0]: 1}))
        self.assertFalse(self._side("USD", self._build())["rows"][0]["eligible"])
        self._mutate_audit_record(lambda record: record["checks"].update({"unexpected": True}))
        self.assertFalse(self._side("USD", self._build())["rows"][0]["eligible"])
        self._mutate_audit_record(lambda record: record["checks"].update({fr.MANDATORY_IDENTITY_CHECKS[0]: None}))
        self.assertFalse(self._side("USD", self._build())["rows"][0]["eligible"])
        self._restore_audit()

    def test_modified_audit_digest_fails_closed(self) -> None:
        self._mutate_audit_record(lambda record: record.update({"status": "BOUNDARY_VERIFICATION_FAILED"}))
        with self.assertRaises(fr.FounderReviewIntegrityError):
            fr.build_founder_review_workbench(
                self.resources,
                review_root=self.review_root,
                expected_audit_sha256=self.baseline_audit_hash,
            )
        self._restore_audit()

    def test_manifest_binding_and_blank_packet_hash_mismatch_fail_closed(self) -> None:
        manifest_path = self.resources / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["identityAuditContract"] = "WRONG_AUDIT_CONTRACT"
        self._write_json(manifest_path, manifest)
        with self.assertRaises(fr.FounderReviewIntegrityError):
            self._build()
        self._write_resources()
        packet_path = self.resources / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
        packet_bytes = packet_path.read_bytes()
        packet_path.write_bytes(packet_bytes + b" ")
        with self.assertRaises(fr.FounderReviewIntegrityError):
            self._build()

    def test_resource_bytes_and_legacy_bundle_outputs_never_change(self) -> None:
        before = self._resource_snapshot()
        legacy = self.resources / "research_labs" / "chart_conditioned_aspects" / "founder_review" / "USD_APRIL_2025_FOUNDER_REVIEWED_POLARITY_V1.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text('{"legacy":"must not be imported"}\n', encoding="utf-8")
        before = self._resource_snapshot()
        initial = self._build()
        usd = self._side("USD", initial)
        self._export("USD", [self._reviewed_row(usd, decision="NEUTRAL")])
        self.assertEqual(before, self._resource_snapshot())
        self.assertFalse((self.resources / "status" / "founder_review").exists())

    def test_execution_and_product_boundary_locks_remain_false(self) -> None:
        workbench = self._build()
        self.assertFalse(workbench["guardrails"]["executionAllowed"])
        for side in workbench["sides"]:
            self.assertFalse(side["guardrails"]["priceDataRead"])
            self.assertFalse(side["guardrails"]["sbcRead"])
            self.assertFalse(side["guardrails"]["llmRead"])
            self.assertFalse(side["guardrails"]["catalogueAdmission"])
            self.assertFalse(side["guardrails"]["polarityAssigned"])
            self.assertFalse(side["guardrails"]["directionalWaveRendered"])

    def test_review_input_types_are_strictly_validated(self) -> None:
        initial = self._build()
        usd = self._side("USD", initial)
        cases = [
            ("reviewer", 7),
            ("founderReasoning", 7),
            ("reviewTimestampUtc", 7),
            ("sourceReferenceSourceId", 7),
        ]
        for name, value in cases:
            with self.subTest(field=name):
                row = self._reviewed_row(
                    usd,
                    decision="SUPPORTIVE" if name != "sourceReferenceSourceId" else "SUPPORTIVE",
                    classification="SOURCE_BACKED_CLASSICAL_CANDIDATE" if name == "sourceReferenceSourceId" else "FOUNDER_RESEARCH_HYPOTHESIS",
                    references=[self._source_reference("STRICT")]
                    if name == "sourceReferenceSourceId"
                    else [],
                )
                if name == "sourceReferenceSourceId":
                    row["founderReview"]["sourceReferences"][0]["sourceId"] = value
                else:
                    row["founderReview"][name] = value
                with self.assertRaises(fr.FounderReviewIntegrityError):
                    self._export("USD", [row])


if __name__ == "__main__":
    unittest.main()
