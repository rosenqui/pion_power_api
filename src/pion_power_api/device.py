"""Device data model for Pion Power API."""

from __future__ import annotations

import typing as t

from .control_signal import ControlSignal

if t.TYPE_CHECKING:
    from .client import PionPowerAPIClient
    from .device_data import DeviceData
    from .device_stats import DeviceStats


class Device:
    """Represents a Pion Power device with configuration and status information."""

    def __init__(  # noqa: PLR0913
        self,
        station_code: str,
        device_code: str,
        device_name: str,
        device_type: str,
        parent_code: str,
        master_or_slave: str,
        device_share_status: str,
        product_id: str,
        product_code: str,
        product_name: str,
        hardware_version: str,
        software_version: str,
        upgrade_version: str,
        upgrade_progress: str,
        client: PionPowerAPIClient,
    ) -> None:
        """Initialize the Device instance."""
        self.station_code = station_code
        self.device_code = device_code
        self.device_name = device_name
        self.device_type = device_type
        self.parent_code = parent_code
        self.master_or_slave = master_or_slave
        self.device_share_status = device_share_status
        self.product_id = product_id
        self.product_code = product_code
        self.product_name = product_name
        self.hardware_version = hardware_version
        self.software_version = software_version
        self.upgrade_version = upgrade_version
        self.upgrade_progress = upgrade_progress
        self.client = client

    def __repr__(self) -> str:
        """Return a string representation of the Device instance."""
        return (
            f"Device(station_code={self.station_code!r}, "
            f"device_code={self.device_code!r}, "
            f"device_name={self.device_name!r}, "
            f"device_type={self.device_type!r}, "
            f"parent_code={self.parent_code!r}, "
            f"master_or_slave={self.master_or_slave!r}, "
            f"device_share_status={self.device_share_status!r}, "
            f"product_id={self.product_id!r}, "
            f"product_code={self.product_code!r}, "
            f"product_name={self.product_name!r}, "
            f"hardware_version={self.hardware_version!r}, "
            f"software_version={self.software_version!r}, "
            f"upgrade_version={self.upgrade_version!r}, "
            f"upgrade_progress={self.upgrade_progress!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two Device instances for equality."""
        if self is other:
            return True
        if not isinstance(other, Device):
            return False
        return (
            self.station_code == other.station_code
            and self.device_code == other.device_code
            and self.device_name == other.device_name
            and self.device_type == other.device_type
            and self.parent_code == other.parent_code
            and self.master_or_slave == other.master_or_slave
            and self.device_share_status == other.device_share_status
            and self.product_id == other.product_id
            and self.product_code == other.product_code
            and self.product_name == other.product_name
            and self.hardware_version == other.hardware_version
            and self.software_version == other.software_version
            and self.upgrade_version == other.upgrade_version
            and self.upgrade_progress == other.upgrade_progress
        )

    def __hash__(self) -> int:
        """Return a hash based on the device identity and data."""
        return hash(
            (
                self.station_code,
                self.device_code,
                self.device_name,
                self.device_type,
                self.parent_code,
                self.master_or_slave,
                self.device_share_status,
                self.product_id,
                self.product_code,
                self.product_name,
                self.hardware_version,
                self.software_version,
                self.upgrade_version,
                self.upgrade_progress,
            )
        )

    @classmethod
    def from_dict(cls, data: dict[str, t.Any], client: PionPowerAPIClient) -> Device:
        """
        Create a Device instance from a dictionary.

        Args:
            data: Dictionary containing device data.
            client: The API client instance.

        Returns:
            A Device instance populated with data from the dictionary.

        """
        return cls(
            station_code=str(data.get("StationCode")),
            device_code=str(data.get("DeviceCode")),
            device_name=str(data.get("DeviceName")),
            device_type=str(data.get("DeviceType")),
            parent_code=str(data.get("ParentCode")),
            master_or_slave=str(data.get("MasterOrSlave")),
            device_share_status=str(data.get("DeviceShareStatus")),
            product_id=str(data.get("ProductId")),
            product_code=str(data.get("ProductCode")),
            product_name=str(data.get("ProductName")),
            hardware_version=str(data.get("HardwareVersion")),
            software_version=str(data.get("SoftwareVersion") or data.get("SoftVersion")),
            upgrade_version=str(data.get("UpgradeVersion")),
            upgrade_progress=str(data.get("UpgradeProgress")),
            client=client,
        )

    def to_dict(self) -> dict[str, t.Any]:
        """
        Convert the Device instance to a dictionary.

        Returns:
            Dictionary representation of the device.

        """
        return {
            "StationCode": self.station_code,
            "DeviceCode": self.device_code,
            "DeviceName": self.device_name,
            "DeviceType": self.device_type,
            "ParentCode": self.parent_code,
            "MasterOrSlave": self.master_or_slave,
            "DeviceShareStatus": self.device_share_status,
            "ProductId": self.product_id,
            "ProductCode": self.product_code,
            "ProductName": self.product_name,
            "HardwareVersion": self.hardware_version,
            "SoftwareVersion": self.software_version,
            "UpgradeVersion": self.upgrade_version,
            "UpgradeProgress": self.upgrade_progress,
        }

    async def get_realtime_data(self) -> dict[str, DeviceData]:
        """
        Get real-time data for this device.

        Calls the client's get_realtime_data_by_device_code method
        with this device's code.

        Returns:
            A list of DeviceData objects containing real-time signal data.

        """
        return await self.client.get_realtime_data_by_device_code(self.device_code)

    async def get_stats(self) -> DeviceStats:
        """
        Get statistic data for this device.

        Calls the client's get_device_stats method
        with this device's code.

        Returns:
            A DeviceStats object containing device statistics data.

        """
        return await self.client.get_device_stats(self.device_code)

    async def start_charging(self, current: int, duration_hours: int) -> bool:
        """
        Start charging the device.

        Args:
            current: The desired charging current in Amperes.
            duration_hours: The duration of the charging operation in hours.

        Returns:
            True if the charging command was successful, False otherwise.

        """
        return await self._charging_control(current, duration_hours, charge=True)

    async def stop_charging(self) -> bool:
        """
        Stop charging the device.

        Returns:
            True if the stop charging command was successful, False otherwise.

        """
        return await self._charging_control(0, 0, charge=False)

    async def _charging_control(self, current: int, duration_hours: int, *, charge: bool) -> bool:
        """
        Send a charging control command to the device.

        Args:
            current: The desired charging current in Amperes.
            duration_hours: The duration of the charging operation in hours.
            charge: True to start charging, False to stop.

        Returns:
            True if the control command was successful, False otherwise.

        """
        if charge:
            signal_value = 0
            signal = ControlSignal(
                pile_sn=self.device_code,
                status=signal_value,
                duration=duration_hours,
                current=current,
            )
        else:
            signal_value = 1
            signal = ControlSignal(
                pile_sn=self.device_code,
                status=signal_value,
            )
        return await self.client.set_control_data(self.device_code, "90100404", 1, signal_value, signal)
