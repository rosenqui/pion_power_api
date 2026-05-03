"""DeviceStats data model for Pion Power API."""

from __future__ import annotations

import typing as t


class DeviceStatValue:
    """Represents a single numeric statistic value with metadata."""

    def __init__(
        self,
        value: float | None,
        percent: float | None,
        unit: str | None,
    ) -> None:
        """Initialize the DeviceStatValue instance."""
        self.value: float | None = value
        self.percent: float | None = percent
        self.unit: str | None = unit

    def __repr__(self) -> str:
        """Return a string representation of the DeviceStatValue instance."""
        return f"DeviceStatValue(value={self.value!r}, percent={self.percent!r}, unit={self.unit!r})"

    def __eq__(self, other: object) -> bool:
        """Compare two DeviceStatValue instances for equality."""
        if self is other:
            return True
        if not isinstance(other, DeviceStatValue):
            return False
        return self.value == other.value and self.percent == other.percent and self.unit == other.unit

    def __hash__(self) -> int:
        """Return a hash based on the device stat value."""
        return hash((self.value, self.percent, self.unit))

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> DeviceStatValue:
        """
        Create a DeviceStatValue instance from a dictionary.

        Args:
            data: Dictionary containing device stat
        Returns:
            A DeviceStatValue instance.

        """
        return cls(
            value=float(data.get("Value", 0.0)) if data is not None else None,
            percent=float(data.get("Percent", 0.0)) if data is not None else None,
            unit=str(data.get("Unit")) if data is not None else None,
        )

    def to_dict(self) -> dict[str, t.Any]:
        """
        Convert the DeviceStatValue instance to a dictionary.

        Returns:
            Dictionary representation of the device stat.

        """
        return {
            "Value": self.value,
            "Percent": self.percent,
            "Unit": self.unit,
        }


class DevicePeriodStats:
    """Represents a period stat block in DeviceStats."""

    def __init__(  # noqa: PLR0913
        self,
        charge: DeviceStatValue,
        discharge: DeviceStatValue,
        move_charge: DeviceStatValue,
        move_discharge: DeviceStatValue,
        pv_discharge: DeviceStatValue,
        station_use: DeviceStatValue,
        grid_use: DeviceStatValue,
        grid_out: DeviceStatValue,
        ev_charge: DeviceStatValue,
        ev_order_number: int,
        ev_charge_hours: DeviceStatValue,
        profit: DeviceStatValue,
        es_profit: DeviceStatValue,
        pv_profit: DeviceStatValue,
    ) -> None:
        """Initialize the DevicePeriodStats instance."""
        self.charge = charge
        self.discharge = discharge
        self.move_charge = move_charge
        self.move_discharge = move_discharge
        self.pv_discharge = pv_discharge
        self.station_use = station_use
        self.grid_use = grid_use
        self.grid_out = grid_out
        self.ev_charge = ev_charge
        self.ev_order_number = ev_order_number
        self.ev_charge_hours = ev_charge_hours
        self.profit = profit
        self.es_profit = es_profit
        self.pv_profit = pv_profit

    def __repr__(self) -> str:
        """Return a string representation of the DevicePeriodStats instance."""
        return (
            f"DevicePeriodStats(charge={self.charge!r}, discharge={self.discharge!r}, "
            f"move_charge={self.move_charge!r}, move_discharge={self.move_discharge!r}, "
            f"pv_discharge={self.pv_discharge!r}, station_use={self.station_use!r}, "
            f"grid_use={self.grid_use!r}, grid_out={self.grid_out!r}, "
            f"ev_charge={self.ev_charge!r}, ev_order_number={self.ev_order_number!r}, "
            f"ev_charge_hours={self.ev_charge_hours!r}, profit={self.profit!r}, "
            f"es_profit={self.es_profit!r}, pv_profit={self.pv_profit!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two DevicePeriodStats instances for equality."""
        if self is other:
            return True
        if not isinstance(other, DevicePeriodStats):
            return False
        return (
            self.charge == other.charge
            and self.discharge == other.discharge
            and self.move_charge == other.move_charge
            and self.move_discharge == other.move_discharge
            and self.pv_discharge == other.pv_discharge
            and self.station_use == other.station_use
            and self.grid_use == other.grid_use
            and self.grid_out == other.grid_out
            and self.ev_charge == other.ev_charge
            and self.ev_order_number == other.ev_order_number
            and self.ev_charge_hours == other.ev_charge_hours
            and self.profit == other.profit
            and self.es_profit == other.es_profit
            and self.pv_profit == other.pv_profit
        )

    def __hash__(self) -> int:
        """Return a hash based on the period stats."""
        return hash(
            (
                self.charge,
                self.discharge,
                self.move_charge,
                self.move_discharge,
                self.pv_discharge,
                self.station_use,
                self.grid_use,
                self.grid_out,
                self.ev_charge,
                self.ev_order_number,
                self.ev_charge_hours,
                self.profit,
                self.es_profit,
                self.pv_profit,
            )
        )

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> DevicePeriodStats:
        """Create a DevicePeriodStats instance from a dictionary."""
        return cls(
            charge=DeviceStatValue.from_dict(data.get("Charge", {})),
            discharge=DeviceStatValue.from_dict(data.get("Discharge", {})),
            move_charge=DeviceStatValue.from_dict(data.get("MoveCharge", {})),
            move_discharge=DeviceStatValue.from_dict(data.get("MoveDischarge", {})),
            pv_discharge=DeviceStatValue.from_dict(data.get("PVDischarge", {})),
            station_use=DeviceStatValue.from_dict(data.get("StationUse", {})),
            grid_use=DeviceStatValue.from_dict(data.get("GridUse", {})),
            grid_out=DeviceStatValue.from_dict(data.get("GridOut", {})),
            ev_charge=DeviceStatValue.from_dict(data.get("EVCharge", {})),
            ev_order_number=int(data.get("EVOrderNumber", 0)),
            ev_charge_hours=DeviceStatValue.from_dict(data.get("EVChargeHours", {})),
            profit=DeviceStatValue.from_dict(data.get("Profit", {})),
            es_profit=DeviceStatValue.from_dict(data.get("ESProfit", {})),
            pv_profit=DeviceStatValue.from_dict(data.get("PVProfit", {})),
        )

    def to_dict(self) -> dict[str, t.Any]:
        """Convert the DevicePeriodStats instance to a dictionary."""
        return {
            "Charge": self.charge.to_dict(),
            "Discharge": self.discharge.to_dict(),
            "MoveCharge": self.move_charge.to_dict(),
            "MoveDischarge": self.move_discharge.to_dict(),
            "PVDischarge": self.pv_discharge.to_dict(),
            "StationUse": self.station_use.to_dict(),
            "GridUse": self.grid_use.to_dict(),
            "GridOut": self.grid_out.to_dict(),
            "EVCharge": self.ev_charge.to_dict(),
            "EVOrderNumber": self.ev_order_number,
            "EVChargeHours": self.ev_charge_hours.to_dict(),
            "Profit": self.profit.to_dict(),
            "ESProfit": self.es_profit.to_dict(),
            "PVProfit": self.pv_profit.to_dict(),
        }


class DeviceStats:
    """Represents device statistics across multiple reporting periods."""

    def __init__(
        self,
        day_stat: DevicePeriodStats,
        month_stat: DevicePeriodStats,
        year_stat: DevicePeriodStats,
        total_stat: DevicePeriodStats,
    ) -> None:
        """Initialize the DeviceStats instance."""
        self.day_stat = day_stat
        self.month_stat = month_stat
        self.year_stat = year_stat
        self.total_stat = total_stat

    def __repr__(self) -> str:
        """Return a string representation of the DeviceStats instance."""
        return (
            f"DeviceStats(day_stat={self.day_stat!r}, month_stat={self.month_stat!r}, "
            f"year_stat={self.year_stat!r}, total_stat={self.total_stat!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two DeviceStats instances for equality."""
        if self is other:
            return True
        if not isinstance(other, DeviceStats):
            return False
        return (
            self.day_stat == other.day_stat
            and self.month_stat == other.month_stat
            and self.year_stat == other.year_stat
            and self.total_stat == other.total_stat
        )

    def __hash__(self) -> int:
        """Return a hash based on the device stats."""
        return hash((self.day_stat, self.month_stat, self.year_stat, self.total_stat))

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> DeviceStats:
        """Create a DeviceStats instance from a dictionary."""
        return cls(
            day_stat=DevicePeriodStats.from_dict(data.get("DayStat", {})),
            month_stat=DevicePeriodStats.from_dict(data.get("MonthStat", {})),
            year_stat=DevicePeriodStats.from_dict(data.get("YearStat", {})),
            total_stat=DevicePeriodStats.from_dict(data.get("TotalStat", {})),
        )

    def to_dict(self) -> dict[str, t.Any]:
        """Convert the DeviceStats instance to a dictionary."""
        return {
            "DayStat": self.day_stat.to_dict(),
            "MonthStat": self.month_stat.to_dict(),
            "YearStat": self.year_stat.to_dict(),
            "TotalStat": self.total_stat.to_dict(),
        }
