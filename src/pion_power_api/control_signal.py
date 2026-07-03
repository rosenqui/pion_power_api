"""Control signal data model for Pion Power API."""

from __future__ import annotations

import typing as t


class ControlSignal:
    """Represents the JSON structure used in the signalString field for control commands."""

    def __init__(
        self,
        pile_sn: str,
        start_time: str,
        duration: int,
        current: float,
        power: float,
        status: int,
    ) -> None:
        """
        Initialize the ControlSignal instance.

        Args:
            pile_sn: The device code (Pile Serial Number).
            start_time: The scheduled start time (e.g., "YYYY-MM-DD HH:mm:ss").
            duration: The duration of the operation in hours.
            current: The charging current in Amperes.
            power: The charging power in Watts.
            status: The status code for the control signal.

        """
        self.pile_sn = pile_sn
        self.start_time = start_time
        self.duration = duration
        self.current = current
        self.power = power
        self.status = status

    def __repr__(self) -> str:
        """Return a string representation of the ControlSignal instance."""
        return (
            f"ControlSignal(pile_sn={self.pile_sn!r}, start_time={self.start_time!r}, "
            f"duration={self.duration!r}, current={self.current!r}, "
            f"power={self.power!r}, status={self.status!r})"
        )

    def to_dict(self) -> dict[str, t.Any]:
        """
        Convert the ControlSignal instance to a dictionary compatible with the API's signalString.

        Returns:
            Dictionary representation of the control signal with PascalCase keys.

        """
        return {
            "PileSn": self.pile_sn,
            "StartTime": self.start_time,
            "Duration": self.duration,
            "Current": self.current,
            "Power": self.power,
            "Status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> ControlSignal:
        """
        Create a ControlSignal instance from a dictionary.

        Args:
            data: Dictionary containing control signal data.

        Returns:
            A ControlSignal instance.

        """
        return cls(
            pile_sn=str(data.get("PileSn", "")),
            start_time=str(data.get("StartTime", "")),
            duration=int(data.get("Duration", 0)),
            current=float(data.get("Current", 0.0)),
            power=float(data.get("Power", 0.0)),
            status=int(data.get("Status", 0)),
        )
