"""Async HTTP client for the Pion Power API."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import typing as t

import httpx

import pion_power_api

from .device import Device
from .device_data import DeviceData
from .device_stats import DeviceStats
from .exceptions import (
    PionApiError,
    PionAuthError,
    PionConnectionError,
    PionInvalidJsonError,
    PionLoginError,
    PionUnexpectedResponseError,
)
from .station import Station

if t.TYPE_CHECKING:
    from types import TracebackType

JSON = t.Any
Headers = dict[str, str]

_LOGGER = logging.getLogger(__name__)


class PionPowerAPIClient:
    """HTTP REST API client for asynchronous communication with Pion Power."""

    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
        headers: Headers | None = None,
    ) -> None:
        """
        Initialize the Pion Power API client.

        Args:
            base_url: The base URL of the Pion Power API server.
            username: Optional username for authentication.
            password: Optional password for authentication.
            httpx_client: Optional custom httpx.AsyncClient instance. If not provided, a default client will be created.
            timeout: Request timeout in seconds. Defaults to 30.0.
            headers: Optional dictionary of additional HTTP headers.

        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token: str | None = None
        self.timeout = timeout

        self.is_logged_in = False
        self.company_code = "PionPower"
        self.company_type = 0
        self.language = "en-us"

        default_headers: Headers = {
            "Accept": "application/json",
            "User-Agent": f"pion_power_api/{pion_power_api.__version__}",
            "CompanyCode": "PionPower",
            "TimeZone": "UTC",
        }

        if headers:
            default_headers.update(headers)

        async def log_request(request: httpx.Request) -> None:
            _LOGGER.debug("Request: %s %s", request.method, request.url)

        if httpx_client is None:
            httpx_client = httpx.AsyncClient(
                base_url=self.base_url,
                event_hooks={"request": [log_request]},
                headers=default_headers,
                timeout=self.timeout,
            )
        else:
            httpx_client.base_url = self.base_url
            httpx_client.headers.update(default_headers)
            httpx_client.timeout = self.timeout

        self._client = httpx_client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def login(
        self,
        username: str | None = None,
        password: str | None = None,
    ) -> bool:
        """
        Authenticate with username and password.

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
            PionApiError: When the login request fails or the response is invalid.

        """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        if not self.username or not self.password:
            msg = "Username and password are required for login."
            raise ValueError(msg)

        response = await self.__post(
            "/ToCWebInterfaceServer/Auth/UserLogin",
            json={
                "UserLoginId": self.username,
                "PassWord": hashlib.md5(self.password.encode()).hexdigest().lower(),  # noqa: S324
                "LoginType": 2,
            },
        )

        if not isinstance(response, dict):
            raise PionInvalidJsonError(response=response)

        if response["Code"] != 1:
            raise PionLoginError(response=response)

        token: str | None = None
        data = response.get("Data")
        if isinstance(data, dict):
            token = data.get("Token")

        if not token or not isinstance(token, str):
            msg_0 = "Login response did not include Data.Token."
            raise PionApiError(msg_0, response=response)

        self.token = token
        self._client.headers["token"] = token
        self.is_logged_in = True
        self.company_code = (
            response.get("CompanyCode", "PionPower") if isinstance(response.get("CompanyCode"), str) else "PionPower"
        )
        self.company_type = response.get("CompanyType", 0) if isinstance(response.get("CompanyType"), int) else 0
        self.language = response.get("Language", "en-us") if isinstance(response.get("Language"), str) else "en-us"
        return True

    async def get_device(self, device_code: str) -> Device:
        """
        Fetch a device by its code.

        Args:
            device_code: The code of the device to query.

        Returns:
            A Device object containing device information.

        Raises:
            PionApiError: When the response is not valid JSON or the request fails.

        """
        response = await self.__post("/AppInterfaceServer/Config/GetDeviceInfo", json={"DeviceCode": device_code})
        data = self.__raise_on_error(response, dict)
        return Device.from_dict(data, self)

    async def get_device_list(self, station_code: str) -> list[Device]:
        """
        Fetch the list of devices for a given station code.

        Args:
            station_code: The code of the station to query.

        Returns:
            A list of DeviceData objects containing device information.

        Raises:
            PionApiError: When the response is not valid JSON or the request fails.

        """
        response = await self.__post("/AppInterfaceServer/Config/GetDeviceList", json={"StationCode": station_code})
        data = self.__raise_on_error(response, list)
        return [Device.from_dict(device, self) for device in data if isinstance(device, dict)]

    async def get_device_stats(self, device_code: str) -> DeviceStats:
        """
        Fetch real-time device stats by device code.

        Sends a POST request to "/StatisticsDataServer/Statistics/GetDeviceStatisticData"
        with the device code included in the JSON body. The response body is
        validated as JSON and parsed into DeviceStats objects.

        Args:
            device_code: The code of the device to query.

        Returns:
            A DeviceStats object containing device statistics data.

        Raises:
            PionApiError: When the response is not valid JSON or the request fails.

        """
        response = await self.__post(
            "/StatisticsDataServer/Statistics/GetDeviceStatisticData",
            json={"DeviceCode": device_code},
        )
        data = self.__raise_on_error(response, dict)
        return DeviceStats.from_dict(data)

    async def get_realtime_data_by_device_code(self, device_code: str) -> dict[str, DeviceData]:
        """
        Fetch real-time device data by device code.

        Args:
            device_code: The code of the device to query.

        Returns:
            A dictionary mapping signal IDs to DeviceData objects containing real-time signal data.

        Raises:
            PionApiError: When the response is not valid JSON or the request fails.

        """
        response = await self.__post(
            "/APPInterfaceServer/RealData/GetRealDataByDeviceCode",
            json={"DeviceCode": device_code},
        )
        data = self.__raise_on_error(response, dict)
        return {k: DeviceData.from_dict(device) for k, v in data.items() if (device := v) and isinstance(device, dict)}

    async def get_station_list(self) -> list[Station]:
        """
        Fetch the list of all stations.

        Sends a POST request to "/AppInterfaceServer/Config/GetStationList"
        to retrieve all stations the authenticated user has access to.

        Returns:
            A list of Station objects.

        Raises:
            PionApiError: When the response is not valid JSON or the request fails.

        """
        response = await self.__post("/AppInterfaceServer/Config/GetStationList", json={})
        data = self.__raise_on_error(response, list)
        return [Station.from_dict(station, self) for station in data if isinstance(station, dict)]

    async def __get(
        self,
        path: str,
        params: dict[str, t.Any] | None = None,
        headers: Headers | None = None,
    ) -> JSON | str:
        return await self.__request("GET", path, params=params, headers=headers)

    async def __post(
        self,
        path: str,
        json: JSON | None = None,
        params: dict[str, t.Any] | None = None,
        headers: Headers | None = None,
    ) -> JSON | str:
        return await self.__request("POST", path, params=params, json=json, headers=headers)

    def __raise_on_error(self, response: t.Any | str, data_type: type) -> t.Any:
        if not isinstance(response, dict):
            self.is_logged_in = False
            raise PionInvalidJsonError(response=response)
        if response["Code"] == -1 and response["Msg"] == "<<<Token已过期>>>":
            self.is_logged_in = False
            raise PionAuthError(response=response)
        if response["Code"] != 1 or not isinstance(response["Data"], data_type):
            self.is_logged_in = False
            raise PionUnexpectedResponseError(response=response)
        return response["Data"]

    async def __request(
        self,
        method: str,
        path: str,
        params: dict[str, t.Any] | None = None,
        json: JSON | None = None,
        headers: Headers | None = None,
    ) -> JSON | str:
        """Send an asynchronous HTTP request to the API."""
        request_headers = self._client.headers.copy()
        if headers:
            request_headers.update(headers)

        if not path.startswith("/"):
            path = f"/{path}"

        try:
            async with asyncio.timeout(self.timeout):
                response = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    headers=request_headers,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            err_msg = f"API request failed with status {exc.response.status_code}: {exc.response.text}"
            raise PionApiError(
                err_msg,
                status_code=exc.response.status_code,
                response=exc.response,
            ) from exc
        except httpx.ConnectError as exc:
            raise PionConnectionError from exc
        except httpx.RequestError as exc:
            raise PionApiError(str(exc)) from exc

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()

        return response.text

    async def __aenter__(self) -> PionPowerAPIClient:  # noqa: PYI034
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the HTTP client."""
        await self.close()
