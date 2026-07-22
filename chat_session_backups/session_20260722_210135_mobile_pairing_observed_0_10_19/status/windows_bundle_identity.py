from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONTRACT = "GANN_WINDOWS_BUNDLE_IDENTITY_V1"
BUNDLE_MARKER_PREFIX = b"__TAURI_BUNDLE_TYPE_VAR_"
CANONICAL_BUNDLE_TYPE = b"UNK"
SUPPORTED_BUNDLE_TYPES = {b"UNK", b"NSS"}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _marker_offset(value: bytes) -> int:
    offsets: list[int] = []
    start = 0
    while True:
        found = value.find(BUNDLE_MARKER_PREFIX, start)
        if found < 0:
            break
        offsets.append(found + len(BUNDLE_MARKER_PREFIX))
        start = found + len(BUNDLE_MARKER_PREFIX)
    if len(offsets) != 1:
        raise ValueError(
            "expected exactly one Tauri bundle marker, "
            f"found {len(offsets)}"
        )
    return offsets[0]


def bundle_type(value: bytes) -> str:
    offset = _marker_offset(value)
    marker = value[offset : offset + 3]
    if marker not in SUPPORTED_BUNDLE_TYPES:
        raise ValueError(f"unsupported Tauri bundle marker: {marker!r}")
    return marker.decode("ascii")


def canonicalize_bundle_marker(value: bytes) -> bytes:
    offset = _marker_offset(value)
    marker = value[offset : offset + 3]
    if marker not in SUPPORTED_BUNDLE_TYPES:
        raise ValueError(f"unsupported Tauri bundle marker: {marker!r}")
    if marker == CANONICAL_BUNDLE_TYPE:
        return value
    normalized = bytearray(value)
    normalized[offset : offset + 3] = CANONICAL_BUNDLE_TYPE
    return bytes(normalized)


def compare_bundle_payloads(candidate_path: Path, installed_path: Path) -> dict[str, Any]:
    candidate = candidate_path.expanduser().resolve()
    installed = installed_path.expanduser().resolve()
    candidate_bytes = candidate.read_bytes()
    installed_bytes = installed.read_bytes()
    candidate_canonical = canonicalize_bundle_marker(candidate_bytes)
    installed_canonical = canonicalize_bundle_marker(installed_bytes)
    differing_offsets = [
        offset
        for offset, (left, right) in enumerate(zip(candidate_bytes, installed_bytes))
        if left != right
    ]
    differing_bytes = len(differing_offsets) + abs(
        len(candidate_bytes) - len(installed_bytes)
    )
    normalized_match = candidate_canonical == installed_canonical
    return {
        "contract": CONTRACT,
        "auditedAtUtc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "candidate": {
            "path": str(candidate),
            "bytes": len(candidate_bytes),
            "sha256": _sha256(candidate_bytes),
            "bundleType": bundle_type(candidate_bytes),
            "normalizedSha256": _sha256(candidate_canonical),
        },
        "installed": {
            "path": str(installed),
            "bytes": len(installed_bytes),
            "sha256": _sha256(installed_bytes),
            "bundleType": bundle_type(installed_bytes),
            "normalizedSha256": _sha256(installed_canonical),
        },
        "comparison": {
            "normalizedMatch": normalized_match,
            "bundleMarkerOnlyDifference": normalized_match and differing_bytes <= 3,
            "differingBytes": differing_bytes,
            "differingOffsets": [f"0x{offset:X}" for offset in differing_offsets],
        },
        "promotionAllowed": False,
        "executionAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a Tauri portable executable against its installed NSIS payload."
    )
    parser.add_argument("candidate", type=Path)
    parser.add_argument("installed", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compare_bundle_payloads(args.candidate, args.installed)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["comparison"]["normalizedMatch"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
