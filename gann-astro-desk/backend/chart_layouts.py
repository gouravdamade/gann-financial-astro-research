from __future__ import annotations

import json
import math
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Protocol


LAYOUT_CONTRACT = "GANN_CHART_LAYOUT_V1"
LAYOUT_SCHEMA_VERSION = 1
DRAWING_CONTRACT = "GANN_RESEARCH_CHART_DRAWING_V1"
DRAWING_SCHEMA_VERSION = 1
TEMPLATE_CONTRACT = "GANN_DRAWING_TEMPLATE_V1"
TEMPLATE_SCHEMA_VERSION = 1

ALLOWED_WORKSPACES = {"main", "analysis"}
ALLOWED_DRAWING_TYPES = {
    "horizontal_line",
    "vertical_line",
    "gann_fan",
    "fibonacci_retracement",
    "square_of_nine",
}
RESEARCH_GUARDRAILS = {
    "researchOnly": True,
    "consumedByLiveInference": False,
    "consumedByShadowLedger": False,
    "executionAllowed": False,
}


class LayoutRepository(Protocol):
    def connect(self) -> sqlite3.Connection: ...


class LayoutRevisionConflict(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_chart_layout_schema(repository: LayoutRepository) -> None:
    with repository.connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_chart_layouts (
                layout_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                workspace_kind TEXT NOT NULL CHECK(workspace_kind IN ('main', 'analysis')),
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                family_key TEXT NOT NULL DEFAULT '',
                contract TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                revision INTEGER NOT NULL,
                is_default INTEGER NOT NULL DEFAULT 0,
                autosave INTEGER NOT NULL DEFAULT 1,
                chart_state_json TEXT NOT NULL DEFAULT '{}',
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_app_chart_layouts_scope
                ON app_chart_layouts(
                    workspace_kind, symbol, timeframe, family_key, is_default, updated_at_utc
            );
            CREATE TABLE IF NOT EXISTS app_chart_drawings (
                drawing_id TEXT NOT NULL,
                layout_id TEXT NOT NULL,
                drawing_type TEXT NOT NULL,
                contract TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                z_index INTEGER NOT NULL,
                drawing_json TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                PRIMARY KEY(layout_id, drawing_id),
                FOREIGN KEY(layout_id) REFERENCES app_chart_layouts(layout_id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_app_chart_drawings_layout
                ON app_chart_drawings(layout_id, z_index, drawing_id);
            CREATE TABLE IF NOT EXISTS app_drawing_templates (
                template_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                drawing_type TEXT NOT NULL,
                contract TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                template_json TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_app_drawing_templates_type
                ON app_drawing_templates(drawing_type, name);
            """
        )
        connection.execute(
            """
            INSERT INTO schema_meta(key, value, updated_at_utc)
            VALUES('chart_layout_schema_version', ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at_utc=excluded.updated_at_utc
            WHERE schema_meta.value <> excluded.value
            """,
            (str(LAYOUT_SCHEMA_VERSION), utc_now()),
        )
        connection.commit()


def _required_text(value: Any, label: str, limit: int) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text[:limit]


def _json_size(value: Any, label: str, limit: int) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be valid JSON") from exc
    if len(encoded.encode("utf-8")) > limit:
        raise ValueError(f"{label} exceeds {limit // 1024} KB")
    return encoded


def _iso_utc(value: Any, label: str) -> str:
    text = _required_text(value, label, 64).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite_number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _normalize_style(drawing_type: str, value: Any) -> dict[str, Any]:
    defaults = {
        "horizontal_line": ("#62c6ed", "solid", 0.9),
        "vertical_line": ("#d68ac0", "solid", 0.9),
        "gann_fan": ("#d7a63e", "dashed", 0.82),
        "fibonacci_retracement": ("#57b8a6", "solid", 0.86),
        "square_of_nine": ("#58a6c6", "solid", 0.84),
    }
    color, line_style, opacity = defaults[drawing_type]
    source = value if isinstance(value, dict) else {}
    candidate_color = str(source.get("color") or color).strip()
    if (
        len(candidate_color) == 7
        and candidate_color.startswith("#")
        and all(character in "0123456789abcdefABCDEF" for character in candidate_color[1:])
    ):
        color = candidate_color.lower()
    candidate_style = str(source.get("lineStyle") or line_style)
    if candidate_style in {"solid", "dashed", "dotted"}:
        line_style = candidate_style
    try:
        line_width = int(source.get("lineWidth", 1))
    except (TypeError, ValueError):
        line_width = 1
    try:
        opacity = float(source.get("opacity", opacity))
    except (TypeError, ValueError):
        opacity = defaults[drawing_type][2]
    return {
        "color": color,
        "lineWidth": min(4, max(1, line_width)),
        "lineStyle": line_style,
        "opacity": min(1.0, max(0.1, opacity)),
    }


def _normalize_settings(
    drawing_type: str,
    value: Any,
    anchors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    if drawing_type == "gann_fan":
        raw_ratios = source.get("ratios")
        ratios = []
        if isinstance(raw_ratios, list):
            for raw in raw_ratios[:16]:
                try:
                    ratio = float(raw)
                except (TypeError, ValueError):
                    continue
                if math.isfinite(ratio) and ratio != 0:
                    ratios.append(ratio)
        return {"ratios": ratios or [0.25, 0.5, 1.0, 2.0, 4.0]}
    if drawing_type == "fibonacci_retracement":
        raw_levels = source.get("levels")
        levels = []
        if isinstance(raw_levels, list):
            for raw in raw_levels[:24]:
                try:
                    level = float(raw)
                except (TypeError, ValueError):
                    continue
                if math.isfinite(level) and -5.0 <= level <= 5.0 and level not in levels:
                    levels.append(level)
        if len(levels) < 2:
            levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        return {
            "levels": levels,
            "showLabels": bool(source.get("showLabels", True)),
            "showPrices": bool(source.get("showPrices", True)),
            "extendLines": bool(source.get("extendLines", False)),
        }
    if drawing_type != "square_of_nine":
        return source
    anchor_price = anchors[0]["price"] if anchors else 1.0
    try:
        center = float(source.get("centerValue", anchor_price))
    except (TypeError, ValueError):
        center = anchor_price
    if not math.isfinite(center) or center <= 0:
        center = anchor_price if anchor_price > 0 else 1.0
    try:
        increment = float(source.get("increment", 0.01))
    except (TypeError, ValueError):
        increment = 0.01
    if not math.isfinite(increment) or increment <= 0:
        increment = 0.01
    try:
        rings = int(source.get("rings", 3))
    except (TypeError, ValueError):
        rings = 3
    try:
        angle_offset = float(source.get("angleOffsetDeg", 0))
    except (TypeError, ValueError):
        angle_offset = 0.0
    if not math.isfinite(angle_offset):
        angle_offset = 0.0
    highlighted = []
    raw_highlighted = source.get("highlightedAngles")
    if isinstance(raw_highlighted, list):
        for raw in raw_highlighted[:32]:
            try:
                angle = float(raw)
            except (TypeError, ValueError):
                continue
            if math.isfinite(angle):
                highlighted.append(angle)
    number_rotation = str(source.get("numberRotation") or "clockwise")
    angle_rotation = str(source.get("angleRotation") or "clockwise")
    return {
        "centerValue": center,
        "increment": increment,
        "rings": min(12, max(1, rings)),
        "numberRotation": (
            number_rotation
            if number_rotation in {"clockwise", "counterclockwise"}
            else "clockwise"
        ),
        "angleRotation": (
            angle_rotation
            if angle_rotation in {"clockwise", "counterclockwise"}
            else "clockwise"
        ),
        "angleOffsetDeg": max(-360.0, min(360.0, angle_offset)),
        "highlightedAngles": highlighted or [0, 45, 90, 135, 180, 225, 270, 315],
        "showCardinals": bool(source.get("showCardinals", True)),
        "showDiagonals": bool(source.get("showDiagonals", True)),
        "showLabels": bool(source.get("showLabels", True)),
        "showPriceProjections": bool(source.get("showPriceProjections", False)),
        "showTimeProjections": bool(source.get("showTimeProjections", False)),
    }


def normalize_drawing(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    drawing_type = _required_text(payload.get("type"), "drawing type", 40)
    if drawing_type not in ALLOWED_DRAWING_TYPES:
        raise ValueError(f"unsupported drawing type: {drawing_type}")
    drawing_id = str(payload.get("drawingId") or uuid.uuid4())
    anchors = payload.get("anchors")
    if not isinstance(anchors, list):
        raise ValueError("drawing anchors must be a list")
    two_anchor_types = {"gann_fan", "fibonacci_retracement", "square_of_nine"}
    minimum_anchors = 2 if drawing_type in two_anchor_types else 1
    if len(anchors) < minimum_anchors or len(anchors) > 8:
        raise ValueError(f"{drawing_type} requires at least {minimum_anchors} anchor(s)")
    normalized_anchors = []
    for anchor_index, anchor in enumerate(anchors):
        if not isinstance(anchor, dict):
            raise ValueError("drawing anchor must be an object")
        normalized_anchors.append(
            {
                "timeUtc": _iso_utc(
                    anchor.get("timeUtc"), f"anchor {anchor_index + 1} timeUtc"
                ),
                "price": _finite_number(
                    anchor.get("price"), f"anchor {anchor_index + 1} price"
                ),
            }
        )
    if drawing_type in two_anchor_types:
        first_anchor, second_anchor = normalized_anchors[:2]
        if first_anchor["timeUtc"] == second_anchor["timeUtc"]:
            raise ValueError(f"{drawing_type} anchors require distinct times")
        price_tolerance = max(abs(first_anchor["price"]) * 1e-10, 1e-8)
        if math.isclose(
            first_anchor["price"],
            second_anchor["price"],
            rel_tol=0.0,
            abs_tol=price_tolerance,
        ):
            raise ValueError(f"{drawing_type} anchors require distinct prices")
    style = _normalize_style(drawing_type, payload.get("style"))
    settings = _normalize_settings(drawing_type, payload.get("settings"), normalized_anchors)
    normalized = {
        "contract": DRAWING_CONTRACT,
        "schemaVersion": DRAWING_SCHEMA_VERSION,
        "drawingId": drawing_id,
        "type": drawing_type,
        "name": str(payload.get("name") or drawing_type.replace("_", " ").title())[:80],
        "visible": bool(payload.get("visible", True)),
        "locked": bool(payload.get("locked", False)),
        "zIndex": int(payload.get("zIndex", index)),
        "anchors": normalized_anchors,
        "style": style,
        "settings": settings,
        "guardrails": dict(RESEARCH_GUARDRAILS),
    }
    _json_size(normalized, "drawing", 256 * 1024)
    return normalized


def _scope(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    workspace = _required_text(payload.get("workspaceKind"), "workspaceKind", 20)
    if workspace not in ALLOWED_WORKSPACES:
        raise ValueError("workspaceKind must be main or analysis")
    symbol = _required_text(payload.get("symbol"), "symbol", 32).upper()
    timeframe = _required_text(payload.get("timeframe"), "timeframe", 16).upper()
    family_key = str(payload.get("familyKey") or "").strip()[:240]
    if workspace == "analysis" and not family_key:
        raise ValueError("familyKey is required for analysis layouts")
    return workspace, symbol, timeframe, family_key


def _drawing_rows(connection: sqlite3.Connection, layout_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT drawing_json
        FROM app_chart_drawings
        WHERE layout_id = ?
        ORDER BY z_index, drawing_id
        """,
        (layout_id,),
    ).fetchall()
    drawings = []
    for row in rows:
        try:
            drawing = json.loads(str(row["drawing_json"]))
        except json.JSONDecodeError:
            continue
        if isinstance(drawing, dict):
            drawings.append(drawing)
    return drawings


def _layout_record(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    try:
        chart_state = json.loads(str(item.get("chart_state_json") or "{}"))
    except json.JSONDecodeError:
        chart_state = {}
    return {
        "contract": str(item["contract"]),
        "schemaVersion": int(item["schema_version"]),
        "layoutId": str(item["layout_id"]),
        "name": str(item["name"]),
        "workspaceKind": str(item["workspace_kind"]),
        "symbol": str(item["symbol"]),
        "timeframe": str(item["timeframe"]),
        "familyKey": str(item["family_key"]),
        "revision": int(item["revision"]),
        "isDefault": bool(item["is_default"]),
        "autosave": bool(item["autosave"]),
        "chartState": chart_state if isinstance(chart_state, dict) else {},
        "drawings": _drawing_rows(connection, str(item["layout_id"])),
        "createdAtUtc": str(item["created_at_utc"]),
        "updatedAtUtc": str(item["updated_at_utc"]),
    }


def list_chart_layouts(
    repository: LayoutRepository,
    *,
    workspace_kind: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    family_key: str | None = None,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    values: list[Any] = []
    for column, value in (
        ("workspace_kind", workspace_kind),
        ("symbol", symbol.upper() if symbol else None),
        ("timeframe", timeframe.upper() if timeframe else None),
        ("family_key", family_key),
    ):
        if value is not None:
            clauses.append(f"{column} = ?")
            values.append(value)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with repository.connect() as connection:
        rows = connection.execute(
            f"""
            SELECT * FROM app_chart_layouts {where}
            ORDER BY is_default DESC, updated_at_utc DESC, name
            """,
            values,
        ).fetchall()
        return [_layout_record(connection, row) for row in rows]


def get_chart_layout(repository: LayoutRepository, layout_id: str) -> dict[str, Any]:
    with repository.connect() as connection:
        row = connection.execute(
            "SELECT * FROM app_chart_layouts WHERE layout_id = ?", (layout_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown chart layout: {layout_id}")
        return _layout_record(connection, row)


def save_chart_layout(repository: LayoutRepository, payload: dict[str, Any]) -> dict[str, Any]:
    workspace, symbol, timeframe, family_key = _scope(payload)
    name = _required_text(payload.get("name"), "layout name", 80)
    layout_id = str(payload.get("layoutId") or uuid.uuid4())
    chart_state = payload.get("chartState") if isinstance(payload.get("chartState"), dict) else {}
    chart_state_json = _json_size(chart_state, "chart state", 256 * 1024)
    raw_drawings = payload.get("drawings", [])
    if not isinstance(raw_drawings, list) or len(raw_drawings) > 500:
        raise ValueError("drawings must be a list with no more than 500 items")
    drawings = [normalize_drawing(item, index) for index, item in enumerate(raw_drawings)]
    if len({item["drawingId"] for item in drawings}) != len(drawings):
        raise ValueError("drawingId values must be unique within a layout")
    expected_revision = payload.get("expectedRevision")
    if expected_revision is not None and not isinstance(expected_revision, int):
        raise ValueError("expectedRevision must be an integer")
    now = utc_now()
    with repository.connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            "SELECT * FROM app_chart_layouts WHERE layout_id = ?", (layout_id,)
        ).fetchone()
        if existing is not None and expected_revision is not None:
            current_revision = int(existing["revision"])
            if current_revision != expected_revision:
                raise LayoutRevisionConflict(
                    f"layout revision changed: expected {expected_revision}, current {current_revision}"
                )
        if existing is None and expected_revision not in {None, 0}:
            raise LayoutRevisionConflict("new layouts must use expectedRevision 0")
        revision = int(existing["revision"]) + 1 if existing is not None else 1
        created_at = str(existing["created_at_utc"]) if existing is not None else now
        requested_default = bool(payload.get("isDefault", False))
        has_scope_default = connection.execute(
            """
            SELECT 1 FROM app_chart_layouts
            WHERE workspace_kind = ? AND symbol = ? AND timeframe = ? AND family_key = ?
              AND is_default = 1 AND layout_id <> ?
            LIMIT 1
            """,
            (workspace, symbol, timeframe, family_key, layout_id),
        ).fetchone()
        is_default = requested_default or (existing is not None and bool(existing["is_default"]))
        if existing is None and has_scope_default is None:
            is_default = True
        if requested_default:
            connection.execute(
                """
                UPDATE app_chart_layouts SET is_default = 0
                WHERE workspace_kind = ? AND symbol = ? AND timeframe = ? AND family_key = ?
                """,
                (workspace, symbol, timeframe, family_key),
            )
        connection.execute(
            """
            INSERT INTO app_chart_layouts(
                layout_id, name, workspace_kind, symbol, timeframe, family_key,
                contract, schema_version, revision, is_default, autosave,
                chart_state_json, created_at_utc, updated_at_utc
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(layout_id) DO UPDATE SET
                name=excluded.name,
                workspace_kind=excluded.workspace_kind,
                symbol=excluded.symbol,
                timeframe=excluded.timeframe,
                family_key=excluded.family_key,
                contract=excluded.contract,
                schema_version=excluded.schema_version,
                revision=excluded.revision,
                is_default=excluded.is_default,
                autosave=excluded.autosave,
                chart_state_json=excluded.chart_state_json,
                updated_at_utc=excluded.updated_at_utc
            """,
            (
                layout_id,
                name,
                workspace,
                symbol,
                timeframe,
                family_key,
                LAYOUT_CONTRACT,
                LAYOUT_SCHEMA_VERSION,
                revision,
                int(is_default),
                int(bool(payload.get("autosave", True))),
                chart_state_json,
                created_at,
                now,
            ),
        )
        existing_created = {
            str(row["drawing_id"]): str(row["created_at_utc"])
            for row in connection.execute(
                "SELECT drawing_id, created_at_utc FROM app_chart_drawings WHERE layout_id = ?",
                (layout_id,),
            ).fetchall()
        }
        connection.execute("DELETE FROM app_chart_drawings WHERE layout_id = ?", (layout_id,))
        for drawing in drawings:
            encoded = _json_size(drawing, "drawing", 256 * 1024)
            connection.execute(
                """
                INSERT INTO app_chart_drawings(
                    drawing_id, layout_id, drawing_type, contract, schema_version,
                    z_index, drawing_json, created_at_utc, updated_at_utc
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    drawing["drawingId"],
                    layout_id,
                    drawing["type"],
                    DRAWING_CONTRACT,
                    DRAWING_SCHEMA_VERSION,
                    drawing["zIndex"],
                    encoded,
                    existing_created.get(drawing["drawingId"], now),
                    now,
                ),
            )
        connection.commit()
    return get_chart_layout(repository, layout_id)


def delete_chart_layout(repository: LayoutRepository, layout_id: str) -> bool:
    with repository.connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            "SELECT * FROM app_chart_layouts WHERE layout_id = ?", (layout_id,)
        ).fetchone()
        if existing is None:
            return False
        connection.execute("DELETE FROM app_chart_layouts WHERE layout_id = ?", (layout_id,))
        if bool(existing["is_default"]):
            replacement = connection.execute(
                """
                SELECT layout_id FROM app_chart_layouts
                WHERE workspace_kind = ? AND symbol = ? AND timeframe = ? AND family_key = ?
                ORDER BY updated_at_utc DESC LIMIT 1
                """,
                (
                    existing["workspace_kind"],
                    existing["symbol"],
                    existing["timeframe"],
                    existing["family_key"],
                ),
            ).fetchone()
            if replacement is not None:
                connection.execute(
                    "UPDATE app_chart_layouts SET is_default = 1 WHERE layout_id = ?",
                    (replacement["layout_id"],),
                )
        connection.commit()
        return True


def _template_record(row: sqlite3.Row) -> dict[str, Any]:
    try:
        template = json.loads(str(row["template_json"]))
    except json.JSONDecodeError:
        template = {}
    return {
        "contract": str(row["contract"]),
        "schemaVersion": int(row["schema_version"]),
        "templateId": str(row["template_id"]),
        "name": str(row["name"]),
        "drawingType": str(row["drawing_type"]),
        "style": template.get("style", {}) if isinstance(template, dict) else {},
        "settings": template.get("settings", {}) if isinstance(template, dict) else {},
        "createdAtUtc": str(row["created_at_utc"]),
        "updatedAtUtc": str(row["updated_at_utc"]),
    }


def list_drawing_templates(repository: LayoutRepository) -> list[dict[str, Any]]:
    with repository.connect() as connection:
        rows = connection.execute(
            "SELECT * FROM app_drawing_templates ORDER BY drawing_type, name"
        ).fetchall()
    return [_template_record(row) for row in rows]


def save_drawing_template(repository: LayoutRepository, payload: dict[str, Any]) -> dict[str, Any]:
    drawing_type = _required_text(payload.get("drawingType"), "drawingType", 40)
    if drawing_type not in ALLOWED_DRAWING_TYPES:
        raise ValueError(f"unsupported drawing type: {drawing_type}")
    name = _required_text(payload.get("name"), "template name", 80)
    template_id = str(payload.get("templateId") or uuid.uuid4())
    template = {
        "style": _normalize_style(drawing_type, payload.get("style")),
        "settings": _normalize_settings(drawing_type, payload.get("settings")),
        "guardrails": dict(RESEARCH_GUARDRAILS),
    }
    encoded = _json_size(template, "drawing template", 128 * 1024)
    now = utc_now()
    with repository.connect() as connection:
        connection.execute(
            """
            INSERT INTO app_drawing_templates(
                template_id, name, drawing_type, contract, schema_version,
                template_json, created_at_utc, updated_at_utc
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(template_id) DO UPDATE SET
                name=excluded.name,
                drawing_type=excluded.drawing_type,
                contract=excluded.contract,
                schema_version=excluded.schema_version,
                template_json=excluded.template_json,
                updated_at_utc=excluded.updated_at_utc
            """,
            (
                template_id,
                name,
                drawing_type,
                TEMPLATE_CONTRACT,
                TEMPLATE_SCHEMA_VERSION,
                encoded,
                now,
                now,
            ),
        )
        connection.commit()
    return next(
        item for item in list_drawing_templates(repository) if item["templateId"] == template_id
    )


def delete_drawing_template(repository: LayoutRepository, template_id: str) -> bool:
    with repository.connect() as connection:
        cursor = connection.execute(
            "DELETE FROM app_drawing_templates WHERE template_id = ?", (template_id,)
        )
        connection.commit()
        return cursor.rowcount > 0
