"""JWT and auth utilities — implement in a later phase."""

from typing import Any


def decode_access_token(token: str) -> dict[str, Any]:
    raise NotImplementedError("JWT validation is not configured yet.")
