from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from status.audit_shadow_trial import (
    DECISION_CONTRACT,
    GENESIS_HASH,
    LEDGER_CONTRACT,
    OUTCOME_CONTRACT,
    TRIAL_CONTRACT,
    _canonical_json,
    _entry_hash_payload,
    _fingerprint,
    _sha256_text,
    audit_database,
)


class ShadowAuditTests(unittest.TestCase):
    def build_database(self, path: Path) -> None:
        gate = {
            "minimumWatchClusters": 100,
            "minimumCoverage": 0.1,
            "wilsonLowerMustExceed": 0.5,
            "twoSidedPBelow": 0.05,
            "meanSignedReturnMustExceedPct": 0.0,
            "minimumCalendarMonths": 4,
        }
        identity = {
            "contract": TRIAL_CONTRACT,
            "ledgerContract": LEDGER_CONTRACT,
            "decisionContract": DECISION_CONTRACT,
            "packetContract": "GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1",
            "engineVersion": "engine-v1",
            "policyVersion": "policy-v1",
            "astronomyContract": "RAMAN_TEST_V1",
            "symbol": "USDJPY",
            "timeframe": "H1",
            "outcomeContract": OUTCOME_CONTRACT,
            "horizonHours": 72,
            "gateConfiguration": gate,
        }
        descriptor = {
            **identity,
            "gateConfigurationSha256": _fingerprint(gate),
            "trialId": _fingerprint(identity),
        }
        payload = {
            "contract": DECISION_CONTRACT,
            "executionAllowed": False,
            "horizonHours": 72,
            "shadowId": "S1",
            "capturedAtUtc": "2026-07-22T10:00:00+00:00",
            "labelDueTimeUtc": "2026-07-25T10:00:00+00:00",
            "captureKey": {"timeframe": "H1"},
            "artifactEvidence": {"astronomyContract": "RAMAN_TEST_V1"},
            "packet": {
                "contract": "GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1",
                "engineVersion": "engine-v1",
                "policyVersion": "policy-v1",
                "symbol": "USDJPY",
                "status": "abstain",
            },
        }
        payload_json = _canonical_json(payload)
        row = {
            "ledger_sequence": 1,
            "entry_id": "E1",
            "entry_type": "decision",
            "shadow_id": "S1",
            "event_id": "EVENT1",
            "family_key": "FAMILY",
            "symbol": "USDJPY",
            "timeframe": "H1",
            "effective_at_utc": "2026-07-22T10:00:00+00:00",
            "recorded_at_utc": "2026-07-22T10:01:00+00:00",
            "payload_json": payload_json,
            "payload_sha256": _sha256_text(payload_json),
            "previous_entry_hash": GENESIS_HASH,
        }
        row["entry_hash"] = _fingerprint(_entry_hash_payload(row))
        connection = sqlite3.connect(path)
        try:
            connection.executescript(
                """
                CREATE TABLE app_shadow_ledger_entries(
                    ledger_sequence INTEGER PRIMARY KEY, entry_id TEXT, entry_type TEXT,
                    shadow_id TEXT, event_id TEXT, family_key TEXT, symbol TEXT,
                    timeframe TEXT, effective_at_utc TEXT, recorded_at_utc TEXT,
                    payload_json TEXT, payload_sha256 TEXT, previous_entry_hash TEXT,
                    entry_hash TEXT
                );
                CREATE TABLE app_shadow_trial_manifest(
                    singleton_id INTEGER PRIMARY KEY, trial_id TEXT, contract TEXT,
                    identity_json TEXT, identity_sha256 TEXT, established_at_utc TEXT,
                    seed_shadow_id TEXT, source TEXT
                );
                CREATE TRIGGER trg_shadow_ledger_no_update BEFORE UPDATE ON app_shadow_ledger_entries BEGIN SELECT RAISE(ABORT, 'no'); END;
                CREATE TRIGGER trg_shadow_ledger_no_delete BEFORE DELETE ON app_shadow_ledger_entries BEGIN SELECT RAISE(ABORT, 'no'); END;
                CREATE TRIGGER trg_shadow_trial_manifest_no_update BEFORE UPDATE ON app_shadow_trial_manifest BEGIN SELECT RAISE(ABORT, 'no'); END;
                CREATE TRIGGER trg_shadow_trial_manifest_no_delete BEFORE DELETE ON app_shadow_trial_manifest BEGIN SELECT RAISE(ABORT, 'no'); END;
                """
            )
            connection.execute(
                "INSERT INTO app_shadow_ledger_entries VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                tuple(row[key] for key in (
                    "ledger_sequence", "entry_id", "entry_type", "shadow_id",
                    "event_id", "family_key", "symbol", "timeframe",
                    "effective_at_utc", "recorded_at_utc", "payload_json",
                    "payload_sha256", "previous_entry_hash", "entry_hash",
                )),
            )
            identity_json = _canonical_json(descriptor)
            connection.execute(
                "INSERT INTO app_shadow_trial_manifest VALUES(1,?,?,?,?,?,?,?)",
                (
                    descriptor["trialId"], TRIAL_CONTRACT, identity_json,
                    _sha256_text(identity_json), "2026-07-22T10:01:00+00:00",
                    "S1", "test_fixture",
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def test_read_only_audit_validates_chain_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "shadow.sqlite"
            self.build_database(database)
            report = audit_database(
                database,
                observed_at=datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc),
            )
        self.assertEqual(report["status"], "pass_frozen_cohort_collecting")
        self.assertTrue(report["database"]["openedReadOnly"])
        self.assertTrue(report["database"]["unchangedDuringAudit"])
        self.assertEqual(report["ledger"]["decisionCount"], 1)
        self.assertFalse(report["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
