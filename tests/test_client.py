import json

import httpx
import pytest
import respx

from pion_power_api import (
    PionApiError,
    PionAuthError,
    PionInvalidJsonError,
    PionLoginError,
    PionPowerAPIClient,
    PionUnexpectedResponseError,
)
from pion_power_api.control_signal import ControlSignal


@respx.mock
@pytest.mark.asyncio
async def test_close():
    """Test that close() properly closes the HTTP client."""
    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        assert not client._client.is_closed

    # After exiting context manager, client should be closed
    assert client._client.is_closed


@respx.mock
@pytest.mark.asyncio
async def test_context_manager():
    """Test that PionPowerAPIClient works as an async context manager."""
    client = PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    )
    async with client as ctx_client:
        assert ctx_client is client
        assert not client._client.is_closed

    assert client._client.is_closed


@respx.mock
@pytest.mark.asyncio
async def test_get_returns_json():
    route = respx.get("https://api.example.com/v1/status").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        result = await client._PionPowerAPIClient__get("/status")

    assert result == {"ok": True}
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_login_success():
    """Test successful login."""
    login_route = respx.post(
        "https://api.example.com/v1/ToCWebInterfaceServer/Auth/UserLogin"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "Code": 1,
                "Data": {"Token": "abc123"},
                "CompanyCode": "TestCorp",
                "CompanyType": 1,
                "Language": "en-us",
            },
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1",
        username="user",
        password="secret",
    ) as client:
        success = await client.login()

    assert success is True
    assert client.token == "abc123"
    assert client._client.headers["token"] == "abc123"
    assert client.is_logged_in is True
    assert client.company_code == "TestCorp"
    assert client.company_type == 1
    assert login_route.called


@respx.mock
@pytest.mark.asyncio
async def test_login_without_credentials():
    """Test login raises ValueError when credentials are missing."""
    async with PionPowerAPIClient(
        "https://api.example.com/v1", username="", password=""
    ) as client:
        with pytest.raises(ValueError, match="Username and password are required"):
            await client.login()


@respx.mock
@pytest.mark.asyncio
async def test_login_invalid_response_not_dict():
    """Test login raises PionInvalidJsonError when response is not a dict."""
    respx.post("https://api.example.com/v1/ToCWebInterfaceServer/Auth/UserLogin").mock(
        return_value=httpx.Response(200, json=["not", "a", "dict"])
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", username="user", password="secret"
    ) as client:
        with pytest.raises(PionInvalidJsonError):
            await client.login()


@respx.mock
@pytest.mark.asyncio
async def test_login_failure():
    """Test login raises PionLoginError when response Code is not 1."""
    respx.post("https://api.example.com/v1/ToCWebInterfaceServer/Auth/UserLogin").mock(
        return_value=httpx.Response(200, json={"Code": 0, "Msg": "Invalid credentials"})
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", username="user", password="secret"
    ) as client:
        with pytest.raises(PionLoginError):
            await client.login()


@respx.mock
@pytest.mark.asyncio
async def test_login_missing_token():
    """Test login raises PionApiError when token is missing from response."""
    respx.post("https://api.example.com/v1/ToCWebInterfaceServer/Auth/UserLogin").mock(
        return_value=httpx.Response(200, json={"Code": 1, "Data": {}})
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", username="user", password="secret"
    ) as client:
        with pytest.raises(PionApiError, match="did not include Data.Token"):
            await client.login()


@respx.mock
@pytest.mark.asyncio
async def test_request_raises_api_error_for_bad_status():
    respx.get("https://api.example.com/v1/status").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionApiError) as exc_info:
            await client._PionPowerAPIClient__get("/status")

    assert exc_info.value.status_code == 404


@respx.mock
@pytest.mark.asyncio
async def test_get_device_success():
    """Test get_device returns a Device object."""
    route = respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceInfo"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "Code": 1,
                "Data": {
                    "DeviceCode": "DEV001",
                    "DeviceName": "Device 1",
                    "ProductName": "Product A",
                    "ProductModel": "ModelA",
                    "HardwareVersion": "1.0",
                    "SoftwareVersion": "2.0",
                    "UpgradeVersion": "3.0",
                },
            },
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        device = await client.get_device("DEV001")

    assert device.device_code == "DEV001"
    assert device.device_name == "Device 1"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_device_invalid_response():
    """Test get_device raises PionInvalidJsonError when response is not a dict."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceInfo"
    ).mock(return_value=httpx.Response(200, json="not a dict"))

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionInvalidJsonError):
            await client.get_device("DEV001")


@respx.mock
@pytest.mark.asyncio
async def test_get_device_invalid_code():
    """Test get_device raises PionUnexpectedResponseError when Code is not 1."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceInfo"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 0, "Msg": "Invalid device", "Data": {}}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionUnexpectedResponseError):
            await client.get_device("DEV001")


@respx.mock
@pytest.mark.asyncio
async def test_get_device_auth_expired():
    """Test get_device raises PionAuthError when token has expired."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceInfo"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": -1, "Msg": "<<<Token已过期>>>", "Data": {}}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionAuthError):
            await client.get_device("DEV001")
        assert client.is_logged_in is False


@respx.mock
@pytest.mark.asyncio
async def test_get_device_list_success():
    """Test get_device_list returns a list of Device objects."""
    route = respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceList"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "Code": 1,
                "Data": [
                    {
                        "DeviceCode": "DEV001",
                        "DeviceName": "Device 1",
                        "ProductName": "Product A",
                        "ProductModel": "ModelA",
                        "HardwareVersion": "1.0",
                        "SoftwareVersion": "2.0",
                        "UpgradeVersion": "3.0",
                    },
                    {
                        "DeviceCode": "DEV002",
                        "DeviceName": "Device 2",
                        "ProductName": "Product B",
                        "ProductModel": "ModelB",
                        "HardwareVersion": "1.1",
                        "SoftwareVersion": "2.1",
                        "UpgradeVersion": "3.1",
                    },
                ],
            },
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        devices = await client.get_device_list("STATION001")

    assert len(devices) == 2
    assert devices[0].device_code == "DEV001"
    assert devices[1].device_code == "DEV002"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_device_list_empty():
    """Test get_device_list returns empty list when no devices."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceList"
    ).mock(return_value=httpx.Response(200, json={"Code": 1, "Data": []}))

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        devices = await client.get_device_list("STATION001")

    assert len(devices) == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_device_list_not_a_list():
    """Test get_device_list raises PionUnexpectedResponseError when data is not a list."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetDeviceList"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "", "Data": "not a list"}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionUnexpectedResponseError):
            await client.get_device_list("STATION001")


@respx.mock
@pytest.mark.asyncio
async def test_get_device_stats_success():
    """Test get_device_stats returns a DeviceStats object."""
    route = respx.post(
        "https://api.example.com/v1/StatisticsDataServer/Statistics/GetDeviceStatisticData"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "Code": 1,
                "Data": {
                    "TotalStat": {
                        "Charge": {},
                        "Discharge": {},
                        "MoveCharge": {},
                        "MoveDischarge": {},
                        "PVDischarge": {},
                        "StationUse": {},
                        "GridUse": {},
                        "GridOut": {},
                        "EVCharge": {},
                        "EVOrderNumber": 0,
                        "EVChargeHours": {},
                        "Profit": {},
                        "ESProfit": {},
                        "PVProfit": {},
                    },
                    "DayStatValue": [],
                    "MonthStatValue": [],
                },
            },
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        stats = await client.get_device_stats("DEV001")

    assert stats.total_stat is not None
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_device_stats_not_a_dict():
    """Test get_device_stats raises PionUnexpectedResponseError when data is not a dict."""
    respx.post(
        "https://api.example.com/v1/StatisticsDataServer/Statistics/GetDeviceStatisticData"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "", "Data": "not a dict"}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionUnexpectedResponseError):
            await client.get_device_stats("DEV001")


@respx.mock
@pytest.mark.asyncio
async def test_get_realtime_data_by_device_code():
    route = respx.post(
        "https://api.example.com/v1/APPInterfaceServer/RealData/GetRealDataByDeviceCode"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "Code": 1,
                "Data": {
                    "signal1": {
                        "SignalId": "1",
                        "SignalName": "Power",
                        "SignalValue": "100",
                        "SignalMeaning": "Active Power",
                        "SignalUnit": "W",
                        "BlockType": "Block1",
                        "UpdateTime": "2024-01-01 12:00:00",
                    }
                },
            },
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        result = await client.get_realtime_data_by_device_code("DEV123")

    assert isinstance(result, dict)
    assert len(result) == 1
    assert result["signal1"].signal_id == "1"
    assert result["signal1"].signal_name == "Power"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_realtime_data_by_device_code_empty():
    """Test get_realtime_data_by_device_code with no signals."""
    respx.post(
        "https://api.example.com/v1/APPInterfaceServer/RealData/GetRealDataByDeviceCode"
    ).mock(return_value=httpx.Response(200, json={"Code": 1, "Data": {}}))

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        result = await client.get_realtime_data_by_device_code("DEV123")

    assert len(result) == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_realtime_data_not_a_dict():
    """Test get_realtime_data_by_device_code raises PionUnexpectedResponseError when data is not a dict."""
    respx.post(
        "https://api.example.com/v1/APPInterfaceServer/RealData/GetRealDataByDeviceCode"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "", "Data": "not a dict"}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionUnexpectedResponseError):
            await client.get_realtime_data_by_device_code("DEV123")


@respx.mock
@pytest.mark.asyncio
async def test_get_station_list_success():
    """Test get_station_list returns a list of Station objects."""
    route = respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetStationList"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "Code": 1,
                "Data": [
                    {
                        "StationCode": "STATION001",
                        "StationName": "Station 1",
                    },
                    {
                        "StationCode": "STATION002",
                        "StationName": "Station 2",
                    },
                ],
            },
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        stations = await client.get_station_list()

    assert len(stations) == 2
    assert stations[0].station_code == "STATION001"
    assert stations[1].station_code == "STATION002"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_station_list_empty():
    """Test get_station_list returns empty list when no stations."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetStationList"
    ).mock(return_value=httpx.Response(200, json={"Code": 1, "Data": []}))

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        stations = await client.get_station_list()

    assert len(stations) == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_station_list_not_a_list():
    """Test get_station_list raises PionUnexpectedResponseError when data is not a list."""
    respx.post(
        "https://api.example.com/v1/AppInterfaceServer/Config/GetStationList"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "", "Data": "not a list"}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionUnexpectedResponseError):
            await client.get_station_list()


@respx.mock
@pytest.mark.asyncio
async def test_set_control_data_success():
    """Test successful set_control_data call."""
    route = respx.post(
        "https://api.example.com/v1/ControlDataServer/ControlData/SetControlData"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "Success", "Data": True}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        result = await client.set_control_data("DEV123", "90100205", 1, 16)

    assert result is True
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_set_control_data_with_signal():
    """Test set_control_data with optional signal dictionary."""
    route = respx.post(
        "https://api.example.com/v1/ControlDataServer/ControlData/SetControlData"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "Success", "Data": True}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        result = await client.set_control_data(
            "DEV123", "90100205", 1, 16, signal={"SignalName": "Set current"}
        )

    assert result is True
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_set_control_data_with_control_signal():
    """Test set_control_data with a ControlSignal object."""
    route = respx.post(
        "https://api.example.com/v1/ControlDataServer/ControlData/SetControlData"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 1, "Msg": "Success", "Data": True}
        )
    )

    signal = ControlSignal(
        pile_sn="DEV123",
        start_time="2026-07-06 12:34:56",
        duration=2,
        current=16.0,
        power=2500.0,
        status=0,
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        result = await client.set_control_data(
            "DEV123", "90100205", 1, 16, signal=signal
        )

    assert result is True
    assert route.called

    request = route.calls[0].request
    payload = json.loads(request.content.decode())
    assert payload["signalString"] == json.dumps(signal.to_dict())


@respx.mock
@pytest.mark.asyncio
async def test_set_control_data_api_error():
    """Test set_control_data when API returns an error code."""
    respx.post(
        "https://api.example.com/v1/ControlDataServer/ControlData/SetControlData"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": 0, "Msg": "Operation failed", "Data": {}}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(
            PionUnexpectedResponseError,
            match="Unexpected response received: Operation failed",
        ):
            await client.set_control_data("DEV123", "90100205", 1, 16)


@respx.mock
@pytest.mark.asyncio
async def test_set_control_data_auth_expired():
    """Test set_control_data when authentication has expired."""
    respx.post(
        "https://api.example.com/v1/ControlDataServer/ControlData/SetControlData"
    ).mock(
        return_value=httpx.Response(
            200, json={"Code": -1, "Msg": "<<<Token已过期>>>", "Data": {}}
        )
    )

    async with PionPowerAPIClient(
        "https://api.example.com/v1", "user@example.com", "password"
    ) as client:
        with pytest.raises(PionAuthError):
            await client.set_control_data("DEV123", "90100205", 1, 16)


@pytest.mark.asyncio
async def test_set_control_data_test_mode():
    """Test set_control_data using internal test mode data."""
    # Username 'one_device@example.com' triggers test mode using 'one_device' data set in test_data.py
    async with PionPowerAPIClient(
        "https://api.example.com/v1", "one_device@example.com", "password"
    ) as client:
        result = await client.set_control_data("anything", "anything", 0, 0)

    assert result is True
