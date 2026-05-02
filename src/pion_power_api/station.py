"""Station data model for Pion Power API."""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from .client import PionPowerAPIClient
    from .device import Device


class Station:
    """Represents a Pion Power station with location and type information."""

    def __init__(  # noqa: PLR0913
        self,
        station_code: str,
        station_name: str,
        station_type: str,
        country: str,
        province: str,
        city: str,
        area: str,
        client: PionPowerAPIClient,
    ) -> None:
        """Initialize the Station instance."""
        self.station_code = station_code
        self.station_name = station_name
        self.station_type = station_type
        self.country = country
        self.province = province
        self.city = city
        self.area = area
        self.client = client

    def __repr__(self) -> str:
        """
        Return a string representation of the Station instance.

        Returns:
            String representation of the Station instance.

        """
        return (
            f"Station(station_code={self.station_code!r}, "
            f"station_name={self.station_name!r}, "
            f"station_type={self.station_type!r}, "
            f"country={self.country!r}, "
            f"province={self.province!r}, "
            f"city={self.city!r}, "
            f"area={self.area!r})"
        )

    @classmethod
    def from_dict(cls, data: dict[str, t.Any], client: PionPowerAPIClient) -> Station:
        """
        Create a Station instance from a dictionary.

        Args:
            data: Dictionary containing station data.
            client: The API client instance.

        Returns:
            A Station instance populated with data from the dictionary.

        """
        return cls(
            station_code=str(data.get("StationCode")),
            station_name=str(data.get("StationName")),
            station_type=str(data.get("StationType")),
            country=str(data.get("Country")),
            province=str(data.get("Province")),
            city=str(data.get("City")),
            area=str(data.get("Area")),
            client=client,
        )

    def to_dict(self) -> dict[str, t.Any]:
        """
        Convert the Station instance to a dictionary.

        Returns:
            Dictionary representation of the station.

        """
        return {
            "StationCode": self.station_code,
            "StationName": self.station_name,
            "StationType": self.station_type,
            "Country": self.country,
            "Province": self.province,
            "City": self.city,
            "Area": self.area,
        }

    async def get_devices(self) -> list[Device]:
        """
        Fetch devices associated with this station.

        Returns:
            A list of Device objects associated with this station.

        """
        return await self.client.get_device_list(self.station_code)
