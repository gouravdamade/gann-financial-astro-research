from __future__ import annotations

import unittest

from api_security import private_api_request_authorized


class PrivateApiSecurityTests(unittest.TestCase):
    def test_development_mode_without_a_token_remains_available(self) -> None:
        self.assertTrue(private_api_request_authorized("GET", "", ""))

    def test_packaged_api_requires_the_exact_launch_token(self) -> None:
        self.assertFalse(private_api_request_authorized("GET", "private-token", ""))
        self.assertFalse(
            private_api_request_authorized("POST", "private-token", "wrong-token")
        )
        self.assertTrue(
            private_api_request_authorized("GET", "private-token", "private-token")
        )

    def test_preflight_requests_are_allowed(self) -> None:
        self.assertTrue(private_api_request_authorized("OPTIONS", "private-token", ""))


if __name__ == "__main__":
    unittest.main()
