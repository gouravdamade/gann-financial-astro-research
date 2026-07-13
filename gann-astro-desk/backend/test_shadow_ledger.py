from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from decision_engine import ENGINE
from shadow_ledger import (
    DECISION_CONTRACT,
    LEDGER_CONTRACT,
    TRIAL_CONTRACT,
    ShadowLedgerStore,
    ShadowLedgerSupervisor,
    _canonical_json,
    _entry_hash_payload,
    _fingerprint,
    _sha256,
    bars_to_price_frame,
    first_closed_outcome_bar,
    last_closed_anchor,
)


NOW = pd.Timestamp("2026-07-02T12:00:00Z")
SCORES = {
    "fx_hypothesis_direction": "BEARISH",
    "fx_pair_net_score": -0.2,
    "fx_pair_conflict_ratio": 0.0,
    "fx_doctrine_hypothesis_direction": "BEARISH",
    "fx_doctrine_pair_net_score": -0.15,
    "fx_doctrine_pair_conflict_ratio": 0.0,
}


def event_fixture() -> dict:
    return {
        "event_id": "event-shadow-1",
        "event_family_key": "TN::MERCURY->MARS::trine",
        "event_transit_body": "MERCURY",
        "event_natal_body": "MARS",
        "timestamp": "2026-07-02T10:00:00Z",
        "event_end": "2026-07-02T13:00:00Z",
        "ticker": "USDJPY",
        "astronomy_contract_version": "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2",
    }


def touch_fixture() -> dict:
    return {
        "event_id": "event-shadow-1",
        "touch_id": "touch-shadow-1",
        "event_family_key": "TN::MERCURY->MARS::trine",
        "pair_key": "MARS|MERCURY",
        "aspect": "trine",
        "touch_time_local": "2026-07-02T11:00:00Z",
        "touch_kind": "nearest_line",
        "touch_price": 150.1,
        "touch_planets": "JUPITER",
        "tn_hits_json": "[]",
        "base_tn_hits_json": "[]",
        "base_reference_label": "USD",
        "quote_reference_label": "JPY",
    }


def mt5_bars() -> list[dict]:
    index = pd.date_range("2026-07-02T10:00:00Z", "2026-07-05T12:00:00Z", freq="h")
    output: list[dict] = []
    for offset, timestamp in enumerate(index):
        close = 150.0 + (offset * 0.01)
        output.append(
            {
                "time": int(timestamp.timestamp()),
                "open": close - 0.02,
                "high": close + 0.05,
                "low": close - 0.05,
                "close": close,
                "volume": 10,
            }
        )
    return output


def artifact_fixture() -> dict:
    return {
        "artifactId": "tn-prospective-fixture",
        "label": "Prospective fixture",
        "symbol": "USDJPY",
        "sourceTimeframe": "H1",
        "astronomyContract": "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2",
        "builtIn": False,
        "createdAtUtc": NOW.isoformat(),
        "parameters": {
            "priceSourceId": "snapshot-fixture",
            "priceSourceSha256": "A" * 64,
            "priceSourceAsOfUtc": NOW.isoformat(),
            "priceSourceContract": "PROMOTED_MT5_PRICE_SOURCE_V1",
        },
    }


class FakeRepository:
    def __init__(self, database_path: Path) -> None:
        self.paths = SimpleNamespace(annotation_db=database_path)
        self.artifact = artifact_fixture()
        self.engine_version_override: str | None = None

    def shadow_candidate_snapshot(self) -> dict:
        return {
            "artifact": self.artifact,
            "timeframe": "H1",
            "touches": [
                {
                    "eventId": "event-shadow-1",
                    "touchId": "touch-shadow-1",
                    "touchTime": "2026-07-02T11:00:00Z",
                }
            ],
        }

    def live_decision_packet(
        self,
        event_id: str,
        decision_time: pd.Timestamp,
        *,
        price_override: pd.DataFrame,
    ) -> dict:
        if event_id != "event-shadow-1":
            raise KeyError(event_id)
        packet = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=touch_fixture(),
            price=price_override,
            decision_time=decision_time,
            timeframe="H1",
            artifact=self.artifact,
        )
        if self.engine_version_override:
            packet["engineVersion"] = self.engine_version_override
        return packet


class FakeGateway:
    def bars(self, symbol: str, timeframe: str, count: int = 500) -> list[dict]:
        if symbol != "USDJPY" or timeframe != "H1":
            raise ValueError("unexpected market request")
        return mt5_bars()[-count:]


class ShadowLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary.name) / "shadow.sqlite"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_closed_bar_helpers_do_not_use_future_bars(self) -> None:
        price = bars_to_price_frame(mt5_bars())
        anchor_time, anchor_price = last_closed_anchor(price, "H1", NOW)
        self.assertEqual(anchor_time, NOW)
        self.assertAlmostEqual(anchor_price, 150.01)
        self.assertIsNone(
            first_closed_outcome_bar(price, "H1", NOW + pd.Timedelta(hours=72), NOW)
        )
        outcome = first_closed_outcome_bar(
            price,
            "H1",
            NOW + pd.Timedelta(hours=72),
            NOW + pd.Timedelta(hours=73),
        )
        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(outcome[0], NOW + pd.Timedelta(hours=72))

    def test_supervisor_captures_once_and_settles_only_after_horizon(self) -> None:
        repository = FakeRepository(self.database_path)
        supervisor = ShadowLedgerSupervisor(repository, FakeGateway(), autostart=False)
        with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
            first = supervisor.scan_once(NOW)
            duplicate = supervisor.scan_once(NOW + pd.Timedelta(minutes=1))
        self.assertEqual(first["summary"]["decisionCount"], 1)
        self.assertEqual(first["summary"]["pendingOutcomeCount"], 1)
        trial = first["summary"]["trial"]
        self.assertEqual(trial["contract"], TRIAL_CONTRACT)
        self.assertEqual(trial["status"], "frozen_policy_cohort")
        self.assertTrue(trial["policyLocked"])
        self.assertTrue(trial["integrityValid"])
        self.assertEqual(trial["cohortCount"], 1)
        self.assertEqual(
            trial["nextOutcomeDueTimeUtc"], (NOW + pd.Timedelta(hours=72)).isoformat()
        )
        self.assertEqual(trial["dueOutcomeCount"], 0)
        self.assertEqual(
            trial["progress"]["watchClusters"], {"current": 0, "target": 100}
        )
        self.assertEqual(
            trial["progress"]["calendarMonths"], {"current": 0, "target": 4}
        )
        self.assertEqual(duplicate["summary"]["decisionCount"], 1)
        self.assertEqual(duplicate["supervisor"]["lastCaptureCount"], 0)

        due = supervisor.store.summary(NOW + pd.Timedelta(hours=72))
        self.assertEqual(due["trial"]["dueOutcomeCount"], 1)
        self.assertEqual(due["trial"]["notYetDueOutcomeCount"], 0)

        settled = supervisor.scan_once(NOW + pd.Timedelta(hours=73))
        self.assertEqual(settled["summary"]["settledDecisionCount"], 1)
        self.assertEqual(settled["summary"]["pendingOutcomeCount"], 0)
        self.assertTrue(settled["summary"]["chain"]["valid"])
        record = settled["records"][0]
        self.assertEqual(record["action"], "WATCH_SHORT")
        self.assertEqual(record["status"], "settled")
        self.assertFalse(record["hit"])
        self.assertFalse(record["executionOccurred"])
        self.assertEqual(settled["summary"]["trial"]["dueOutcomeCount"], 0)
        self.assertIsNone(settled["summary"]["trial"]["nextOutcomeDueTimeUtc"])

    def test_frozen_trial_rejects_a_different_engine_policy_cohort(self) -> None:
        repository = FakeRepository(self.database_path)
        supervisor = ShadowLedgerSupervisor(repository, FakeGateway(), autostart=False)
        with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
            first = supervisor.scan_once(NOW)
            repository.engine_version_override = (
                "timestamp_safe_auto_suggest_v2_unapproved"
            )
            rejected = supervisor.scan_once(NOW + pd.Timedelta(minutes=1))
        self.assertEqual(first["summary"]["decisionCount"], 1)
        self.assertEqual(rejected["summary"]["decisionCount"], 1)
        self.assertTrue(rejected["summary"]["trial"]["integrityValid"])
        self.assertIn(
            "frozen prospective trial refuses", rejected["supervisor"]["lastError"]
        )

    def test_existing_legacy_decision_seeds_immutable_trial_manifest_once(self) -> None:
        repository = FakeRepository(self.database_path)
        supervisor = ShadowLedgerSupervisor(repository, FakeGateway(), autostart=False)
        with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
            supervisor.scan_once(NOW)

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            connection.executescript(
                """
                DROP TRIGGER trg_shadow_ledger_no_update;
                DROP TRIGGER trg_shadow_trial_manifest_no_update;
                DROP TRIGGER trg_shadow_trial_manifest_no_delete;
                DELETE FROM app_shadow_trial_manifest;
                """
            )
            row = connection.execute(
                "SELECT * FROM app_shadow_ledger_entries WHERE entry_type = 'decision'"
            ).fetchone()
            assert row is not None
            payload = json.loads(str(row["payload_json"]))
            payload.pop("trialIdentity")
            encoded = _canonical_json(payload)
            payload_sha = _sha256(encoded)
            item = dict(row)
            item["payload_sha256"] = payload_sha
            item["entry_id"] = _fingerprint(
                {
                    "contract": LEDGER_CONTRACT,
                    "entryType": "decision",
                    "shadowId": item["shadow_id"],
                    "payloadSha256": payload_sha,
                }
            )
            item["entry_hash"] = _fingerprint(_entry_hash_payload(item))
            connection.execute(
                """
                UPDATE app_shadow_ledger_entries
                SET entry_id = ?, payload_json = ?, payload_sha256 = ?, entry_hash = ?
                WHERE ledger_sequence = ?
                """,
                (
                    item["entry_id"],
                    encoded,
                    payload_sha,
                    item["entry_hash"],
                    item["ledger_sequence"],
                ),
            )
            connection.commit()
        finally:
            connection.close()

        migrated = ShadowLedgerStore(self.database_path)
        manifest = migrated.trial_manifest()
        self.assertIsNotNone(manifest)
        assert manifest is not None
        self.assertEqual(manifest["manifestSource"], "existing_decision_backfill_v1")
        self.assertTrue(migrated.summary(NOW)["trial"]["integrityValid"])
        self.assertTrue(migrated.verify_chain()["valid"])

    def test_stale_artifact_is_never_backfilled_into_prospective_trial(self) -> None:
        repository = FakeRepository(self.database_path)
        supervisor = ShadowLedgerSupervisor(repository, FakeGateway(), autostart=False)
        snapshot = supervisor.scan_once(NOW + pd.Timedelta(hours=2))
        self.assertEqual(snapshot["summary"]["decisionCount"], 0)
        self.assertEqual(
            snapshot["supervisor"]["readiness"]["code"],
            "artifact_price_snapshot_stale",
        )

    def test_sqlite_guards_reject_decision_update_and_delete(self) -> None:
        repository = FakeRepository(self.database_path)
        supervisor = ShadowLedgerSupervisor(repository, FakeGateway(), autostart=False)
        with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
            supervisor.scan_once(NOW)
        store = ShadowLedgerStore(self.database_path)
        self.assertEqual(store.summary()["contract"], LEDGER_CONTRACT)
        connection = sqlite3.connect(self.database_path)
        try:
            with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
                connection.execute(
                    "UPDATE app_shadow_ledger_entries SET family_key = 'changed' WHERE entry_type = 'decision'"
                )
            connection.rollback()
            with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
                connection.execute("DELETE FROM app_shadow_ledger_entries")
            manifest = connection.execute(
                "SELECT trial_id, contract FROM app_shadow_trial_manifest WHERE singleton_id = 1"
            ).fetchone()
            self.assertIsNotNone(manifest)
            assert manifest is not None
            self.assertEqual(manifest[1], TRIAL_CONTRACT)
            with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
                connection.execute(
                    "UPDATE app_shadow_trial_manifest SET source = 'changed' WHERE singleton_id = 1"
                )
            connection.rollback()
            with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
                connection.execute("DELETE FROM app_shadow_trial_manifest")
        finally:
            connection.close()
        self.assertTrue(store.verify_chain()["valid"])

    def test_decision_payload_is_explicitly_prospective_and_execution_locked(
        self,
    ) -> None:
        repository = FakeRepository(self.database_path)
        supervisor = ShadowLedgerSupervisor(repository, FakeGateway(), autostart=False)
        with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
            supervisor.scan_once(NOW)
        decisions, _ = supervisor.store._payload_sets()
        self.assertEqual(decisions[0]["contract"], DECISION_CONTRACT)
        self.assertEqual(decisions[0]["trialIdentity"]["contract"], TRIAL_CONTRACT)
        self.assertEqual(
            decisions[0]["trialIdentity"]["trialId"],
            supervisor.store.trial_manifest()["trialId"],
        )
        self.assertFalse(decisions[0]["executionAllowed"])
        self.assertFalse(decisions[0]["packet"]["guardrails"]["executionAllowed"])
        self.assertEqual(
            decisions[0]["labelDueTimeUtc"],
            (NOW + pd.Timedelta(hours=72)).isoformat(),
        )


if __name__ == "__main__":
    unittest.main()
