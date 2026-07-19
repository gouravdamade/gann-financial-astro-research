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
        self.assertIsNone(created["drawings"][0]["groupId"])
        self.assertEqual(created["drawings"][0]["syncScope"], "layout")

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

    def test_fibonacci_retracement_is_normalized_and_research_only(self) -> None:
        fibonacci = horizontal_drawing("fib-1")
        fibonacci["type"] = "fibonacci_retracement"
        fibonacci["anchors"] = [
            {"timeUtc": "2026-07-13T10:00:00Z", "price": 148.25},
            {"timeUtc": "2026-07-13T14:00:00Z", "price": 147.5},
        ]
        fibonacci["settings"] = {
            "levels": [0, 0.382, 0.618, 1, 0.618, float("nan"), 99],
            "showLabels": False,
            "showPrices": True,
            "extendLines": True,
        }
        saved = save_chart_layout(self.repository, self.payload(drawings=[fibonacci]))
        drawing = saved["drawings"][0]
        self.assertEqual(drawing["type"], "fibonacci_retracement")
        self.assertEqual(drawing["settings"]["levels"], [0.0, 0.382, 0.618, 1.0])
        self.assertFalse(drawing["settings"]["showLabels"])
        self.assertTrue(drawing["settings"]["extendLines"])
        self.assertEqual(drawing["style"]["color"], "#49a7d1")
        self.assertFalse(drawing["guardrails"]["consumedByLiveInference"])

        fibonacci["anchors"] = [fibonacci["anchors"][0]]
        with self.assertRaisesRegex(ValueError, "requires at least 2"):
            save_chart_layout(self.repository, self.payload(drawings=[fibonacci]))

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

    def test_rsi_pane_and_settings_round_trip(self) -> None:
        rsi_level = horizontal_drawing("rsi-level")
        rsi_level["pane"] = "rsi"
        rsi_level["anchors"][0]["price"] = 62.5
        saved = save_chart_layout(
            self.repository,
            self.payload(
                chartState={
                    "showAspects": True,
                    "showSrLines": True,
                    "rsi": {"visible": True, "period": 21, "levels": [20, 50, 80]},
                },
                drawings=[rsi_level],
            ),
        )
        self.assertEqual(saved["chartState"]["rsi"]["period"], 21)
        self.assertEqual(saved["drawings"][0]["pane"], "rsi")
        self.assertEqual(saved["drawings"][0]["anchors"][0]["price"], 62.5)

        invalid = horizontal_drawing("invalid-rsi-fan")
        invalid["type"] = "gann_fan"
        invalid["pane"] = "rsi"
        invalid["anchors"] = [
            {"timeUtc": "2026-07-13T10:00:00Z", "price": 40},
            {"timeUtc": "2026-07-13T11:00:00Z", "price": 60},
        ]
        normalized = save_chart_layout(
            self.repository,
            self.payload(name="Invalid RSI fan", isDefault=False, drawings=[invalid]),
        )
        self.assertEqual(normalized["drawings"][0]["pane"], "price")

    def test_symbol_synced_drawing_round_trips_across_timeframes(self) -> None:
        synced = horizontal_drawing("shared-line")
        synced["syncScope"] = "symbol"
        synced["groupId"] = "levels"
        synced["groupName"] = "Shared levels"
        h1 = save_chart_layout(
            self.repository,
            self.payload(timeframe="H1", drawings=[synced]),
        )
        m30 = save_chart_layout(
            self.repository,
            self.payload(
                name="USDJPY M30",
                timeframe="M30",
                isDefault=False,
                drawings=[],
            ),
        )

        loaded_m30 = get_chart_layout(self.repository, m30["layoutId"])
        shared = next(
            item for item in loaded_m30["drawings"]
            if item["drawingId"] == "shared-line"
        )
        self.assertEqual(shared["syncScope"], "symbol")
        self.assertEqual(shared["groupId"], "levels")
        self.assertEqual(shared["anchors"], h1["drawings"][0]["anchors"])

        shared["anchors"][0]["price"] = 148.5
        save_chart_layout(
            self.repository,
            self.payload(
                layoutId=m30["layoutId"],
                expectedRevision=m30["revision"],
                name=m30["name"],
                timeframe="M30",
                isDefault=m30["isDefault"],
                drawings=[shared],
            ),
        )
        reloaded_h1 = get_chart_layout(self.repository, h1["layoutId"])
        self.assertEqual(reloaded_h1["drawings"][0]["anchors"][0]["price"], 148.5)

    def test_removing_symbol_sync_deletes_shared_copy_but_keeps_local_copy(self) -> None:
        synced = horizontal_drawing("shared-line")
        synced["syncScope"] = "symbol"
        h1 = save_chart_layout(self.repository, self.payload(drawings=[synced]))
        m30 = save_chart_layout(
            self.repository,
            self.payload(name="M30", timeframe="M30", drawings=[]),
        )
        local = dict(h1["drawings"][0])
        local["syncScope"] = "layout"
        save_chart_layout(
            self.repository,
            self.payload(
                layoutId=h1["layoutId"],
                expectedRevision=h1["revision"],
                drawings=[local],
            ),
        )
        self.assertEqual(
            [item["drawingId"] for item in get_chart_layout(self.repository, h1["layoutId"])["drawings"]],
            ["shared-line"],
        )
        self.assertEqual(get_chart_layout(self.repository, m30["layoutId"])["drawings"], [])


if __name__ == "__main__":
    unittest.main()
