"""Custom exceptions for pion_power_api."""

from __future__ import annotations

import typing as t

class APIError(Exception):
    """Raised when an API request fails."""

    def __init__(self, message: str, status_code: int | None = None, response: t.Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response
