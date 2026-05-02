#!/usr/bin/env python3
"""Standalone application to demonstrate pion_power_api usage."""

import argparse
import asyncio
import sys

from pion_power_api import PionApiError, PionPowerAPIClient
from pion_power_api.device import Device


async def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch real-time data from Pion Power API"
    )
    parser.add_argument(
        "base_url",
        help="Base URL of the Pion Power API (e.g., https://api.example.com)",
    )
    parser.add_argument("username", help="Username for authentication")
    parser.add_argument("password", help="Password for authentication")
    parser.add_argument(
        "--device-code",
        dest="device_code",
        help="Device code to fetch real-time data for",
        default=None,
    )

    args = parser.parse_args()

    # logging.basicConfig(level=logging.INFO)

    async with PionPowerAPIClient(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
    ) as client:
        try:
            print("Attempting to login...")
            if await client.login():
                print("Login successful!")
                print("Company code:", client.company_code)
                print("Company type:", client.company_type)
            else:
                print("Login failed.")
                sys.exit(1)

            if args.device_code:
                print(f"Fetching data for device: {args.device_code}")
                device = await client.get_device(args.device_code)
                await ShowDevice(device)
                return

            stations = await client.get_station_list()
            if not isinstance(stations, list):
                print("Received unexpected data format.")
                sys.exit(1)
            print(
                f"Available stations: {[station.station_name for station in stations if hasattr(station, 'station_name')]}"
            )

            for station in stations:
                devices = await station.get_devices()
                if not isinstance(devices, list):
                    print("Received unexpected data format.")
                    sys.exit(1)
                print(f"Devices for station {station.station_name}:")
                for device in devices:
                    await ShowDevice(device)

        except PionApiError as e:
            print(f"API Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


async def ShowDevice(device: Device) -> None:
    """Print device information and real-time data."""
    print(f"Device: {device.device_name} (Code: {device.device_code})")
    print(f"  Model: {device.product_name}")
    print("  Real-time data:")
    data = await device.get_realtime_data()
    for _, signal in data.items():
        print(
            f"    - {signal.signal_name}: {signal.signal_value} {signal.signal_unit} ({signal.signal_meaning})"
        )
    stats = await device.get_stats()
    print(f"    * Total stats: {stats.total_stat}")


if __name__ == "__main__":
    asyncio.run(main())
