from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import PLANETS, SIGN_NAMES
from .evidence import natal_tables


def load_external_export(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("External calculator export must be a JSON object")
    return payload


def compare_external_export(config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    required_metadata = ("calculator_name", "calculator_version", "profile_id", "ayanamsa", "reductions")
    missing_metadata = [key for key in required_metadata if not str(payload.get(key, "")).strip()]
    if missing_metadata:
        raise ValueError(f"Missing external-calculator metadata: {missing_metadata}")
    if str(payload["ayanamsa"]).strip().lower() != "raman":
        raise ValueError("External comparison must use Raman ayanamsa for this lab version")
    if str(payload["reductions"]).strip().lower() not in {"none", "unreduced"}:
        raise ValueError("External comparison must provide unreduced BAV/SAV values")

    profile_id = str(payload["profile_id"])
    local = natal_tables(config, profile_id)
    external_bav = payload.get("bav")
    external_sav = payload.get("sav")
    if not isinstance(external_bav, dict) or not isinstance(external_sav, list):
        raise ValueError("External export requires `bav` object and `sav` array")

    differences = []
    for planet in PLANETS:
        values = external_bav.get(planet)
        if not isinstance(values, list) or len(values) != 12:
            raise ValueError(f"External {planet} BAV row must contain 12 values")
        for index, (local_value, external_value) in enumerate(zip(local["bav"][planet], values, strict=True)):
            if int(local_value) != int(external_value):
                differences.append(
                    {
                        "table": "BAV",
                        "planet": planet,
                        "sign": SIGN_NAMES[index],
                        "local": int(local_value),
                        "external": int(external_value),
                    }
                )
    if len(external_sav) != 12:
        raise ValueError("External SAV row must contain 12 values")
    for index, (local_value, external_value) in enumerate(zip(local["sav"], external_sav, strict=True)):
        if int(local_value) != int(external_value):
            differences.append(
                {
                    "table": "SAV",
                    "sign": SIGN_NAMES[index],
                    "local": int(local_value),
                    "external": int(external_value),
                }
            )

    return {
        "status": "exact_match" if not differences else "mismatch",
        "passed": not differences,
        "calculator_name": str(payload["calculator_name"]),
        "calculator_version": str(payload["calculator_version"]),
        "profile_id": profile_id,
        "ayanamsa": str(payload["ayanamsa"]),
        "reductions": str(payload["reductions"]),
        "differences": differences,
        "difference_count": len(differences),
        "trading_permission": False,
    }
