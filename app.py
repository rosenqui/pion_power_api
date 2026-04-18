#!/usr/bin/env python3
"""Standalone application to demonstrate pion_power_api usage."""

import asyncio
import argparse
import logging
import pprint
import sys

from pion_power_api import PionPowerAPIClient, APIError


async def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch real-time data from Pion Power API"
    )
    parser.add_argument(
        "base_url",
        help="Base URL of the Pion Power API (e.g., https://api.example.com)"
    )
    parser.add_argument("username", help="Username for authentication")
    parser.add_argument("password", help="Password for authentication")
    parser.add_argument("device_code", help="Device code to fetch real-time data for")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async with PionPowerAPIClient(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
    ) as client:
        try:
            print("Attempting to login...")
            if await client.login():
                print("Login successful!")
            else:
                print("Login failed.")
                sys.exit(1)

            print(f"Fetching real-time data for device: {args.device_code}")
            data = await client.get_realtime_data_by_device_code(args.device_code)
            if not isinstance(data, dict):
                print("Received unexpected data format.")
                sys.exit(1)
            if (data["Code"] != 1) or (not isinstance(data["Data"], dict)):
                print(f"API returned error: {data["Msg"]}")
                sys.exit(1)
            print("Real-time data retrieved successfully:")
            pprint.pprint(data["Data"])

        except APIError as e:
            print(f"API Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())