"""Control signal data model for Pion Power API."""

from __future__ import annotations

import typing as t


class ControlSignal:
    """Represents the JSON structure used in the signalString field for control commands."""

    def __init__(
        self,
        pile_sn: str,
        status: int,
        duration: int | None = None,
        current: float | None = None,
        power: float | None = None,
        start_time: str | None = None,
    ) -> None:
        """
        Initialize the ControlSignal instance.

        Args:
            pile_sn: The device code (Pile Serial Number).
            status: The status code for the control signal.
            duration: The duration of the operation in hours.
            current: The charging current in Amperes.
            power: The charging power in Watts.
            start_time: The scheduled start time (e.g., "YYYY-MM-DD HH:mm:ss").

        """
        self.pile_sn = pile_sn
        self.status = status
        self.duration = duration
        self.current = current
        self.power = power
        self.start_time = start_time or None  # Normalize empty string to None for start_time

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
        values = {
            "PileSn": self.pile_sn,
            "StartTime": self.start_time,
            "Duration": self.duration,
            "Current": self.current,
            "Power": self.power,
            "Status": self.status,
        }
        return {key: value for key, value in values.items() if value is not None}

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> ControlSignal:
        """
        Create a ControlSignal instance from a dictionary.

        Args:
            data: Dictionary containing control signal data.

        Returns:
            A ControlSignal instance.

        """
        raw_power = data.get("Power")
        # Treat empty string or None as missing (None)
        if raw_power in (None, ""):
            power: float | None = None
        else:
            try:
                power = float(raw_power)
            except TypeError, ValueError:
                power = None

        raw_start = data.get("StartTime")
        start_time = str(raw_start) if raw_start not in (None, "") else None

        return cls(
            pile_sn=str(data.get("PileSn", "")),
            status=int(data.get("Status", 0)),
            duration=data.get("Duration"),
            current=data.get("Current"),
            power=power,
            start_time=start_time,
        )
