from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from chart_layouts import (
    DRAWING_CONTRACT,
    LAYOUT_CONTRACT,
    LayoutRevisionConflict,
    delete_chart_layout,
    delete_drawing_template,
    ensure_chart_layout_schema,
    get_chart_layout,
    list_chart_layouts,
    list_drawing_templates,
    save_chart_layout,
    save_drawing_template,
)


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        result = super().__exit__(exc_type, exc_value, traceback)
        self.close()
        return result


class LayoutRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE schema_meta(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                )
                """
            )
            connection.commit()
        ensure_chart_layout_schema(self)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, factory=ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection


def horizontal_drawing(drawing_id: str = "line-1") -> dict:
    return {
        "drawingId": drawing_id,
        "type": "horizontal_line",
        "name": "Support",
        "anchors": [{"timeUtc": "2026-07-13T10:00:00Z", "price": 147.125}],
        "style": {"color": "#49a7d1", "lineWidth": 2},
        "settings": {},
        "guardrails": {"executionAllowed": True},
    }


class ChartLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = LayoutRepository(Path(self.temp_dir.name) / "layouts.sqlite")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def payload(self, **overrides: object) -> dict:
        payload = {
            "name": "Default USDJPY H1",
            "workspaceKind": "main",
            "symbol": "USDJPY",
            "timeframe": "H1",
            "familyKey": "",
            "autosave": True,
            "chartState": {"showAspects": True, "showSrLines": True},
            "drawings": [horizontal_drawing()],
        }
        payload.update(overrides)
        return payload

    def test_create_update_and_reject_stale_revision(self) -> None:
        created = save_chart_layout(self.repository, self.payload())
        self.assertEqual(created["contract"], LAYOUT_CONTRACT)
        self.assertEqual(created["revision"], 1)
        self.assertTrue(created["isDefault"])
        self.assertEqual(created["drawings"][0]["contract"], DRAWING_CONTRACT)
        self.assertFalse(created["drawings"][0]["guardrails"]["executionAllowed"])
        self.assertFalse(created["drawings"][0]["guardrails"]["consumedByLiveInference"])
        self.assertEqual(created["drawings"][0]["style"]["lineStyle"], "solid")
        self.assertEqual(created["drawings"][0]["style"]["opacity"], 0.9)

        updated = save_chart_layout(
            self.repository,
            self.payload(
                layoutId=created["layoutId"],
                expectedRevision=1,
                drawings=[horizontal_drawing("line-2")],
            ),
        )
        self.assertEqual(updated["revision"], 2)
        self.assertEqual([item["drawingId"] for item in updated["drawings"]], ["line-2"])

        with self.assertRaisesRegex(LayoutRevisionConflict, "expected 1, current 2"):
            save_chart_layout(
                self.repository,
                self.payload(
                    layoutId=created["layoutId"],
                    expectedRevision=1,
                    drawings=[],
                ),
            )
        unchanged = get_chart_layout(self.repository, created["layoutId"])
        self.assertEqual(unchanged["revision"], 2)
        self.assertEqual(len(unchanged["drawings"]), 1)

    def test_default_moves_and_delete_promotes_replacement(self) -> None:
        first = save_chart_layout(self.repository, self.payload(name="First"))
        second = save_chart_layout(
            self.repository,
            self.payload(name="Second", isDefault=True),
        )
        self.assertEqual(second["drawings"][0]["drawingId"], "line-1")
        layouts = list_chart_layouts(
            self.repository, workspace_kind="main", symbol="USDJPY", timeframe="H1"
        )
        self.assertEqual(layouts[0]["layoutId"], second["layoutId"])
        self.assertFalse(next(item for item in layouts if item["layoutId"] == first["layoutId"])["isDefault"])

        self.assertTrue(delete_chart_layout(self.repository, second["layoutId"]))
        replacement = get_chart_layout(self.repository, first["layoutId"])
        self.assertTrue(replacement["isDefault"])
        with self.repository.connect() as connection:
            drawing_count = connection.execute(
                "SELECT COUNT(*) FROM app_chart_drawings WHERE layout_id = ?",
                (second["layoutId"],),
            ).fetchone()[0]
        self.assertEqual(drawing_count, 0)

    def test_analysis_layout_requires_family_and_two_anchor_drawings(self) -> None:
        with self.assertRaisesRegex(ValueError, "familyKey is required"):
            save_chart_layout(
                self.repository,
                self.payload(workspaceKind="analysis", familyKey=""),
            )
        bad_fan = horizontal_drawing()
        bad_fan["type"] = "gann_fan"
        with self.assertRaisesRegex(ValueError, "requires at least 2"):
            save_chart_layout(self.repository, self.payload(drawings=[bad_fan]))

        duplicate_fan = horizontal_drawing()
        duplicate_fan["type"] = "gann_fan"
        duplicate_fan["anchors"] = [duplicate_fan["anchors"][0]] * 2
        with self.assertRaisesRegex(ValueError, "require distinct times"):
            save_chart_layout(self.repository, self.payload(drawings=[duplicate_fan]))

    def test_drawing_template_round_trip(self) -> None:
        saved = save_drawing_template(
            self.repository,
            {
                "name": "Blue research fan",
                "drawingType": "gann_fan",
                "style": {"color": "#4bb7e5", "lineWidth": 2},
                "settings": {"ratios": [0.5, 1, 2]},
            },
        )
        self.assertEqual(saved["drawingType"], "gann_fan")
        self.assertEqual(list_drawing_templates(self.repository), [saved])
        self.assertTrue(delete_drawing_template(self.repository, saved["templateId"]))
        self.assertEqual(list_drawing_templates(self.repository), [])


if __name__ == "__main__":
    unittest.main()
