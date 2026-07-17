from __future__ import annotations

import secrets


def private_api_request_authorized(
    method: str,
    expected_token: str,
    provided_token: str,
) -> bool:
    expected = str(expected_token or "")
    if not expected or str(method or "").upper() == "OPTIONS":
        return True
    return secrets.compare_digest(str(provided_token or ""), expected)
