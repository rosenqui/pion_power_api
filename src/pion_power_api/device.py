"""Device data model for Pion Power API."""

from __future__ import annotations

import typing as t

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
        device_now_time: str,
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
        self.device_now_time = device_now_time
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
            f"upgrade_progress={self.upgrade_progress!r}, "
            f"device_now_time={self.device_now_time!r})"
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
            software_version=str(data.get("SoftwareVersion")) or str(data.get("SoftVersion")),
            upgrade_version=str(data.get("UpgradeVersion")),
            upgrade_progress=str(data.get("UpgradeProgress")),
            device_now_time=str(data.get("DeviceNowTime")),
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
            "DeviceNowTime": self.device_now_time,
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
