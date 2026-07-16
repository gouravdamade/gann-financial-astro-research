from __future__ import annotations

import unittest

from aspect_timeframe import effective_aspect_min_duration_minutes


class AspectTimeframePolicyTests(unittest.TestCase):
    def test_auto_policy_requires_one_selected_timeframe_bar(self) -> None:
        self.assertEqual(effective_aspect_min_duration_minutes("M30"), 30.0)
        self.assertEqual(effective_aspect_min_duration_minutes("H1"), 60.0)
        self.assertEqual(effective_aspect_min_duration_minutes("H4"), 240.0)
        self.assertEqual(effective_aspect_min_duration_minutes("D1"), 1440.0)
        self.assertEqual(effective_aspect_min_duration_minutes("W1"), 10080.0)

    def test_manual_policy_preserves_explicit_minutes(self) -> None:
        self.assertEqual(
            effective_aspect_min_duration_minutes("W1", "manual", 30240),
            30240.0,
        )

    def test_invalid_policy_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported aspect duration mode"):
            effective_aspect_min_duration_minutes("H1", "adaptive", 0)


if __name__ == "__main__":
    unittest.main()
