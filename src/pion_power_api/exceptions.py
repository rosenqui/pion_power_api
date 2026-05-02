"""Custom exceptions for pion_power_api."""

from __future__ import annotations

import typing as t


class PionApiError(Exception):
    """Base class for all Pion API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: t.Any = None) -> None:
        """Initialize the PionApiError exception."""
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class PionAuthError(PionApiError):
    """Raised when an API request fails due to authorization issues."""

    def __init__(self, message: str | None = None, status_code: int | None = None, response: t.Any = None) -> None:
        """Initialize the PionAuthError exception."""
        super().__init__(message or "Authentication token is expired or invalid.", status_code, response)


class PionConnectionError(PionApiError):
    """Raised when an API request fails due to a connection-related issue."""

    def __init__(self, status_code: int | None = None, response: t.Any = None) -> None:
        """Initialize the PionConnectionError exception."""
        super().__init__("Connection error occurred.", status_code, response)


class PionInvalidJsonError(PionApiError):
    """Raised when an API response contains invalid JSON."""

    def __init__(self, status_code: int | None = None, response: t.Any = None) -> None:
        """Initialize the PionInvalidJsonError exception."""
        super().__init__("Response is not valid JSON.", status_code, response)


class PionLoginError(PionAuthError):
    """Raised when login fails due to invalid credentials or other authentication issues."""

    def __init__(self, status_code: int | None = None, response: t.Any = None) -> None:
        """Initialize the PionLoginError exception."""
        super().__init__(response.get("Msg") or "Login failed.", status_code, response)


class PionUnexpectedResponseError(PionApiError):
    """Raised when an API response contains unexpected data."""

    def __init__(self, status_code: int | None = None, response: t.Any = None) -> None:
        """Initialize the PionUnexpectedResponseError exception."""
        message = f"Unexpected response received: {response['Msg']}" if response["Msg"] else "Unexpected response received."
        super().__init__(message, status_code, response)
