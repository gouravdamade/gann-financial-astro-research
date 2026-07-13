from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


WORKSPACE_PREFERENCE_DEFAULTS = {
    "inspectorOpen": True,
    "bottomOpen": True,
    "showAspects": True,
    "showSrLines": True,
}


def read_workspace_preferences(repository: Any) -> dict[str, bool]:
    connection = repository.connect()
    try:
        row = connection.execute(
            "SELECT value FROM schema_meta WHERE key = 'workspace_preferences_v1'"
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        return dict(WORKSPACE_PREFERENCE_DEFAULTS)
    try:
        saved = json.loads(str(row["value"]))
    except (TypeError, json.JSONDecodeError):
        saved = {}
    if not isinstance(saved, dict):
        saved = {}
    return {
        key: saved[key] if isinstance(saved.get(key), bool) else default
        for key, default in WORKSPACE_PREFERENCE_DEFAULTS.items()
    }


def update_workspace_preferences(repository: Any, payload: Any) -> dict[str, bool]:
    if not isinstance(payload, dict):
        raise ValueError("Preferences must be a JSON object")
    preferences = read_workspace_preferences(repository)
    for key in WORKSPACE_PREFERENCE_DEFAULTS:
        if key not in payload:
            continue
        if not isinstance(payload[key], bool):
            raise ValueError(f"{key} must be a boolean")
        preferences[key] = payload[key]
    connection = repository.connect()
    try:
        connection.execute(
            """
            INSERT INTO schema_meta(key, value, updated_at_utc)
            VALUES('workspace_preferences_v1', ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at_utc = excluded.updated_at_utc
            """,
            (
                json.dumps(preferences, sort_keys=True),
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        connection.commit()
    finally:
        connection.close()
    return preferences
