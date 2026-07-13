from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from workspace_preferences import (
    WORKSPACE_PREFERENCE_DEFAULTS,
    read_workspace_preferences,
    update_workspace_preferences,
)


class PreferenceRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        connection = self.connect()
        try:
            connection.execute(
                "CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at_utc TEXT NOT NULL)"
            )
            connection.commit()
        finally:
            connection.close()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection


class WorkspacePreferenceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = PreferenceRepository(Path(self.temp_dir.name) / "preferences.sqlite")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_defaults_partial_update_and_persistence(self) -> None:
        initial = read_workspace_preferences(self.repository)
        self.assertEqual(initial, WORKSPACE_PREFERENCE_DEFAULTS)

        response = update_workspace_preferences(
            self.repository,
            {"bottomOpen": False, "showAspects": False},
        )
        self.assertFalse(response["bottomOpen"])
        self.assertTrue(response["inspectorOpen"])

        saved = read_workspace_preferences(self.repository)
        self.assertFalse(saved["bottomOpen"])
        self.assertFalse(saved["showAspects"])
        self.assertTrue(saved["showSrLines"])

    def test_rejects_string_boolean(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be a boolean"):
            update_workspace_preferences(self.repository, {"inspectorOpen": "false"})


if __name__ == "__main__":
    unittest.main()
