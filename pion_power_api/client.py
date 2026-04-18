"""Async HTTP client for the Pion Power API."""

from __future__ import annotations

import logging
import hashlib
import httpx
import typing as t

from .exceptions import APIError

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

    async def get_realtime_data_by_device_code(self, device_code: str) -> JSON:
        """Fetch real-time device data by device code.

        Sends a POST request to "/APPInterfaceServer/RealData/GetRealDataByDeviceCode"
        with the device code included in the JSON body. The response body is
        validated as JSON and returned as a Python dictionary.

        Args:
            device_code: The code of the device to query.

        Returns:
            The parsed JSON response as a Python dictionary.

        Raises:
            APIError: When the response is not valid JSON or the request fails.
        """
        response = await self.__post(
            "/APPInterfaceServer/RealData/GetRealDataByDeviceCode",
            json={"DeviceCode": device_code}
        )
        if not isinstance(response, dict):
            raise APIError("Response is not valid JSON.")
        return response

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

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
