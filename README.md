# pion_power_api

A Python library for communicating with the Pion Power HTTP REST API using asynchronous requests.

## Installation

```bash
pip install pion_power_api
```

Or for development:

```bash
git clone https://github.com/rosenqui/pion_power_api.git
cd pion_power_api
pip install -e .[test]
```

## Usage

### As a Library

```python
import asyncio
from pion_power_api import PionPowerAPIClient

async def main():
    async with PionPowerAPIClient("https://api.pionpower.local/v1", username="user", password="pass") as client:
        token = await client.login()
        data = await client.get_realtime_data_by_device_code("DEVICE123")
        print(data)

asyncio.run(main())
```

### Standalone Application

A standalone application is provided for command-line usage:

```bash
python app.py https://api.example.com user pass DEVICE123
```

Arguments:
- `base_url`: The base URL of the API
- `username`: Username for authentication
- `password`: Password for authentication
- `device_code`: Device code to fetch data for

## Client Methods

### `login()`

Authenticates against `/ToCWebInterfaceServer/Auth/UserLogin` using the configured username and password.
- The password is sent as an MD5 hash in lowercase hexadecimal form.
- On success, the client extracts `Data.Token` from the JSON response.
- The token is stored in the client and used for subsequent requests.

### `get_realtime_data_by_device_code(device_code)`

Fetches real-time data for a device from `/APPInterfaceServer/RealData/GetRealDataByDeviceCode`.
- Sends the device code in the request JSON body as `DeviceCode`.
- Validates that the response is valid JSON and returns it as a Python dictionary.

## Features

- Async HTTP methods: `get`, `post`, `put`, `patch`, `delete`
- Automatic authentication with username/password
- JSON request and response handling
- Custom error handling with `APIError`
- Context manager support for automatic cleanup
