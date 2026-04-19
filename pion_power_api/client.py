"""Async HTTP client for the Pion Power API."""

from __future__ import annotations

import logging
import hashlib
import httpx
import typing as t

from .device import Device
from .device_stats import DeviceStats
from .exceptions import APIError
from .device_data import DeviceData
from .station import Station

JSON = t.Any
Headers = t.Dict[str, str]

_LOGGER = logging.getLogger(__name__)

class PionPowerAPIClient:
    """HTTP REST API client for asynchronous communication with Pion Power."""

    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 10.0,
        headers: Headers | None = None,
        verify: bool = True,
    ) -> None:
        """Initialize the Pion Power API client.

        Args:
            base_url: The base URL of the Pion Power API server.
            username: Optional username for authentication.
            password: Optional password for authentication.
            timeout: Request timeout in seconds. Defaults to 10.0.
            headers: Optional dictionary of additional HTTP headers.
            verify: Whether to verify SSL certificates. Defaults to True.
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token: str | None = None
        self.timeout = timeout
        self.verify = verify

        default_headers: Headers = {
            "Accept": "application/json",
            "User-Agent": "pion_power_api/0.1.0",
            "CompanyCode": "PionPower",
            "TimeZone": "UTC",
        }

        if headers:
            default_headers.update(headers)

        async def log_request(request: httpx.Request):
            _LOGGER.debug(f"Request: {request.method} {request.url} - Waiting for response")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            event_hooks={"request": [log_request]},
            headers=default_headers,
            timeout=self.timeout,
            verify=self.verify,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def login(
        self,
        username: str | None = None,
        password: str | None = None,
    ) -> bool:
        """Authenticate with username and password.

        This method sends the user's credentials to the
        "/ToCWebInterfaceServer/Auth/UserLogin" endpoint. The password is sent
        as an MD5 hash in lowercase hexadecimal form. On success, the returned
        JSON response is parsed and the `Data.Token` value is saved to
        `self.token` and added to the client headers for subsequent requests.

        Args:
            username: Optional username to use for login. If provided, it
                updates the client's stored username.
            password: Optional password to use for login. If provided, it
                updates the client's stored password.

        Returns:
            True when login completes successfully.

        Raises:
            ValueError: When username or password is missing.
            APIError: When the login request fails or the response is invalid.
        """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        if not self.username or not self.password:
            raise ValueError("Username and password are required for login.")

        response = await self.__post(
            "/ToCWebInterfaceServer/Auth/UserLogin",
            json={"UserLoginId": self.username, "PassWord": hashlib.md5(self.password.encode()).hexdigest().lower(), "LoginType": 2},
        )

        if not isinstance(response, dict):
            raise APIError("Login response did not return JSON.")

        token: str | None = None
        data = response.get("Data")
        if isinstance(data, dict):
            token = data.get("Token")

        if not token or not isinstance(token, str):
            raise APIError("Login response did not include Data.Token.")

        self.token = token
        self._client.headers["token"] = token
        return True

    async def get_device(self, device_code: str) -> Device:
        """Fetch a device by its code.

        Args:
            device_code: The code of the device to query.

        Returns:
            A Device object containing device information.

        Raises:
            APIError: When the response is not valid JSON or the request fails.
        """
        response = await self.__post("/AppInterfaceServer/Config/GetDeviceInfo", json={"DeviceCode": device_code})
        if not isinstance(response, dict):
            raise APIError("Response is not valid JSON.")
        if (response["Code"] != 1) or (not isinstance(response["Data"], dict)):
            raise APIError(f"API call failed: {response["Msg"]}")
        return Device.from_dict(response["Data"], self)

    async def get_device_stats(self, device_code: str) -> DeviceStats:
        """Fetch real-time device stats by device code.

        Sends a POST request to "/StatisticsDataServer/Statistics/GetDeviceStatisticData"
        with the device code included in the JSON body. The response body is
        validated as JSON and parsed into DeviceStats objects.

        Args:
            device_code: The code of the device to query.

        Returns:
            A DeviceStats object containing device statistics data.

        Raises:
            APIError: When the response is not valid JSON or the request fails.
        """
        response = await self.__post("/StatisticsDataServer/Statistics/GetDeviceStatisticData", json={"DeviceCode": device_code})
        if not isinstance(response, dict):
            raise APIError("Response is not valid JSON.")
        if (response["Code"] != 1) or (not isinstance(response["Data"], dict)):
            raise APIError(f"API call failed: {response["Msg"]}")
        return DeviceStats.from_dict(response["Data"])

    async def get_realtime_data_by_device_code(self, device_code: str) -> list[DeviceData]:
        """Fetch real-time device data by device code.

        Sends a POST request to "/APPInterfaceServer/RealData/GetRealDataByDeviceCode"
        with the device code included in the JSON body. The response body is
        validated as JSON and parsed into DeviceData objects.

        Args:
            device_code: The code of the device to query.

        Returns:
            A list of DeviceData objects containing real-time signal data.

        Raises:
            APIError: When the response is not valid JSON or the request fails.
        """
        response = await self.__post("/APPInterfaceServer/RealData/GetRealDataByDeviceCode", json={"DeviceCode": device_code})
        if not isinstance(response, dict):
            raise APIError("Response is not valid JSON.")
        if (response["Code"] != 1) or (not isinstance(response["Data"], dict)):
            raise APIError(f"API call failed: {response["Msg"]}")
        return [DeviceData.from_dict(device) for device in response["Data"].values() if isinstance(device, dict)]

    async def get_realtime_station_device_data(self, station_code: str) -> list[Device]:
        """Fetch all devices for a station with their real-time data.

        Sends a POST request to "/ToCWebInterfaceServer/Real/GetStationDeviceReals"
        with the station code to retrieve device information and real-time status.

        Args:
            station_code: The code of the station to query.

        Returns:
            A list of Device objects for the station.

        Raises:
            APIError: When the response is not valid JSON or the request fails.
        """
        response = await self.__post("/ToCWebInterfaceServer/Real/GetStationDeviceReals", json={"StationCode": station_code})
        if not isinstance(response, dict):
            raise APIError("Response is not valid JSON.")
        if (response["Code"] != 1) or (not isinstance(response["Data"]["DeviceReals"], list)):
            raise APIError(f"API call failed: {response["Msg"]}")
        return [Device.from_dict(device, self) for device in response["Data"]["DeviceReals"] if isinstance(device, dict)]

    async def get_station_list(self) -> list[Station]:
        """Fetch the list of all stations.

        Sends a POST request to "/AppInterfaceServer/Config/GetStationList"
        to retrieve all stations the authenticated user has access to.

        Returns:
            A list of Station objects.

        Raises:
            APIError: When the response is not valid JSON or the request fails.
        """
        response = await self.__post("/AppInterfaceServer/Config/GetStationList", json={})
        if not isinstance(response, dict):
            raise APIError("Response is not valid JSON.")
        if (response["Code"] != 1) or (not isinstance(response["Data"], list)):
            raise APIError(f"API call failed: {response["Msg"]}")
        return [Station.from_dict(station, self) for station in response["Data"] if isinstance(station, dict)]

    async def __get(
        self,
        path: str,
        params: t.Dict[str, t.Any] | None = None,
        headers: Headers | None = None,
        timeout: float | None = None,
    ) -> JSON | str:
        return await self.__request("GET", path, params=params, headers=headers, timeout=timeout)

    async def __post(
        self,
        path: str,
        json: JSON | None = None,
        params: t.Dict[str, t.Any] | None = None,
        headers: Headers | None = None,
        timeout: float | None = None,
    ) -> JSON | str:
        return await self.__request("POST", path, params=params, json=json, headers=headers, timeout=timeout)

    async def __request(
        self,
        method: str,
        path: str,
        params: t.Dict[str, t.Any] | None = None,
        json: JSON | None = None,
        headers: Headers | None = None,
        timeout: float | None = None,
    ) -> JSON | str:
        """Send an asynchronous HTTP request to the API."""
        request_headers = self._client.headers.copy()
        if headers:
            request_headers.update(headers)

        if not path.startswith("/"):
            path = f"/{path}"

        try:
            response = await self._client.request(
                method,
                path,
                params=params,
                json=json,
                headers=request_headers,
                timeout=timeout or self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise APIError(
                f"API request failed with status {exc.response.status_code}: {exc.response.text}",
                status_code=exc.response.status_code,
                response=exc.response,
            ) from exc
        except httpx.RequestError as exc:
            raise APIError(str(exc)) from exc

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()

        return response.text

    async def __aenter__(self) -> "PionPowerAPIClient":
        return self

    async def __aexit__(
        self,
        exc_type: t.Type[BaseException] | None,
        exc: BaseException | None,
        traceback: t.Any | None,
    ) -> None:
        await self.close()
