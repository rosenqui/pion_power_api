"""DeviceData data model for Pion Power API."""

from __future__ import annotations

import typing as t


class DeviceData:
    """Represents a Pion Power device signal data point."""

    def __init__(
        self,
        signal_id: str,
        signal_name: str,
        signal_value: str,
        signal_meaning: str,
        signal_unit: str,
        block_type: str,
        update_time: str,
    ) -> None:
        self.signal_id = signal_id
        self.signal_name = signal_name
        self.signal_value = signal_value
        self.signal_meaning = signal_meaning
        self.signal_unit = signal_unit
        self.block_type = block_type
        self.update_time = update_time

    def __repr__(self) -> str:
        return (
            f"DeviceData(signal_id={self.signal_id!r}, "
            f"signal_name={self.signal_name!r}, "
            f"signal_value={self.signal_value!r}, "
            f"signal_meaning={self.signal_meaning!r}, "
            f"signal_unit={self.signal_unit!r}, "
            f"block_type={self.block_type!r}, "
            f"update_time={self.update_time!r})"
        )

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> DeviceData:
        """Create a DeviceData instance from a dictionary.

        Args:
            data: Dictionary containing device data.

        Returns:
            A DeviceData instance populated with data from the dictionary.
        """
        return cls(
            signal_id=data.get("SignalId"),
            signal_name=data.get("SignalName"),
            signal_value=data.get("SignalValue"),
            signal_meaning=data.get("SignalMeaning"),
            signal_unit=data.get("SignalUnit"),
            block_type=data.get("BlockType"),
            update_time=data.get("UpdateTime"),
        )

    def to_dict(self) -> dict[str, t.Any]:
        """Convert the DeviceData instance to a dictionary.

        Returns:
            Dictionary representation of the device data.
        """
        return {
            "SignalId": self.signal_id,
            "SignalName": self.signal_name,
            "SignalValue": self.signal_value,
            "SignalMeaning": self.signal_meaning,
            "SignalUnit": self.signal_unit,
            "BlockType": self.block_type,
            "UpdateTime": self.update_time,
        }
