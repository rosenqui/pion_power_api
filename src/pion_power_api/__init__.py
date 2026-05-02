"""Pion Power API async client package."""

__version__ = "2026.5.2"  # TODO(rosenqui): automate version management

from .client import PionPowerAPIClient
from .device import Device
from .device_data import DeviceData
from .device_stats import DeviceStats
from .exceptions import (
    PionApiError,
    PionAuthError,
    PionConnectionError,
    PionInvalidJsonError,
    PionLoginError,
    PionUnexpectedResponseError,
)
from .station import Station

__all__ = [
    "Device",
    "DeviceData",
    "DeviceStats",
    "PionApiError",
    "PionAuthError",
    "PionConnectionError",
    "PionInvalidJsonError",
    "PionLoginError",
    "PionPowerAPIClient",
    "PionUnexpectedResponseError",
    "Station",
]
