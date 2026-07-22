from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from status.windows_bundle_identity import (
    BUNDLE_MARKER_PREFIX,
    canonicalize_bundle_marker,
    compare_bundle_payloads,
)


class WindowsBundleIdentityTests(unittest.TestCase):
    def test_nsis_marker_normalizes_to_portable_payload(self) -> None:
        portable = b"prefix" + BUNDLE_MARKER_PREFIX + b"UNK" + b"suffix"
        installed = b"prefix" + BUNDLE_MARKER_PREFIX + b"NSS" + b"suffix"
        self.assertEqual(
            canonicalize_bundle_marker(portable),
            canonicalize_bundle_marker(installed),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate_path = root / "candidate.exe"
            installed_path = root / "installed.exe"
            candidate_path.write_bytes(portable)
            installed_path.write_bytes(installed)
            result = compare_bundle_payloads(candidate_path, installed_path)
        self.assertTrue(result["comparison"]["normalizedMatch"])
        self.assertTrue(result["comparison"]["bundleMarkerOnlyDifference"])
        self.assertEqual(result["comparison"]["differingBytes"], 3)
        self.assertEqual(result["candidate"]["bundleType"], "UNK")
        self.assertEqual(result["installed"]["bundleType"], "NSS")

    def test_non_marker_difference_is_rejected(self) -> None:
        portable = b"left" + BUNDLE_MARKER_PREFIX + b"UNK" + b"right"
        installed = b"LEFT" + BUNDLE_MARKER_PREFIX + b"NSS" + b"right"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate_path = root / "candidate.exe"
            installed_path = root / "installed.exe"
            candidate_path.write_bytes(portable)
            installed_path.write_bytes(installed)
            result = compare_bundle_payloads(candidate_path, installed_path)
        self.assertFalse(result["comparison"]["normalizedMatch"])
        self.assertFalse(result["comparison"]["bundleMarkerOnlyDifference"])


if __name__ == "__main__":
    unittest.main()
