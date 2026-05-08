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
    async with PionPowerAPIClient("https://api.example.com/v1", username="user", password="pass") as client:
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

### `close()`

Close the underlying HTTP client.

### `login()`

Authenticate with the username and password supplied as constructor arguments or updated on the instance.

On success, the returned JSON response is parsed and the returned token value is saved and added to the
HTTP client headers for subsequent requests.

**Returns:**
- True when login completes successfully.

**Raises:**
- `ValueError`: When username or password is missing.
- `PionInvalidJsonError`: When the response is not valid JSON.
- `PionLoginError`: When login fails due to invalid credentials.
- `PionApiError`: When the HTTP request fails or the response does not contain the expected token.

### `get_device(device_code)`

Fetch a device by its code.

**Args:**
- `device_code`: The code of the device to query.

**Returns:**
- A Device object containing device information.

**Raises:**
- `PionInvalidJsonError`: When the response is not valid JSON.
- `PionAuthError`: When authentication has expired.
- `PionUnexpectedResponseError`: When the response format is unexpected
- `PionApiError`: When the HTTP request fails

### `get_device_list(station_code)`

Fetch the list of devices for a given station code.

**Args:**
- `station_code`: The code of the station to query.

**Returns:**
- A list of Device objects containing device information.

**Raises:**
- `PionInvalidJsonError`: When the response is not valid JSON.
- `PionAuthError`: When authentication has expired.
- `PionApiError`: When the HTTP request fails.
- `PionUnexpectedResponseError`: When the response format is unexpected.

### `get_device_stats(device_code)`

Fetch real-time device stats by device code.

Sends a POST request to "/StatisticsDataServer/Statistics/GetDeviceStatisticData"
with the device code included in the JSON body. The response body is
validated as JSON and parsed into DeviceStats objects.

**Args:**
- `device_code`: The code of the device to query.

**Returns:**
- A DeviceStats object containing device statistics data.

**Raises:**
- `PionInvalidJsonError`: When the response is not valid JSON.
- `PionAuthError`: When authentication has expired.
- `PionUnexpectedResponseErHTTP request fails
- `PionApiError`: When the response is not valid JSON or the request fails.

### `get_realtime_data_by_device_code(device_code)`

Fetch real-time device data by device code.

**Args:**
- `device_code`: The code of the device to query.

**Returns:**
- A dictionary mapping signal IDs to DeviceData objects containing real-time signal data.

**Raises:**
- `PionInvalidJsonError`: When the response is not valid JSON.
- `PionAuthError`: When authentication has expired.
- `PionUnexpectedResponseError`: When the response format is unexpected
- `PionApiError`: When the HTTP request fails

### `get_station_list()`

Fetch the list of all stations.

Sends a POST request to "/AppInterfaceServer/Config/GetStationList"
to retrieve all stations the authenticated user has access to.

**Returns:**
- A list of Station objects.

**Raises:**
- `PionInvalidJsonError`: When the response is not valid JSON.
- `PionAuthError`: When authentication has expired.
- `PionUnexpectedResponseError`: When the response format is unexpected
- `PionApiError`: When the response is not valid JSON or the request fails.

## Features

- Async HTTP methods: `get`, `post`
- Automatic authentication with username/password
- JSON request and response handling
- Custom error handling with exceptions based on `PionApiError`
- Context manager support for automatic cleanup
