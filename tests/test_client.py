import httpx
import pytest
import respx

from pion_power_api import APIError, PionPowerAPIClient


@respx.mock
@pytest.mark.asyncio
async def test_get_returns_json():
    route = respx.get("https://api.example.com/v1/status").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )

    async with PionPowerAPIClient("https://api.example.com/v1") as client:
        result = await client._PionPowerAPIClient__get("/status")

    assert result == {"ok": True}
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_login_sets_authorization_header_and_token():
    login_route = respx.post(
        "https://api.example.com/v1/ToCWebInterfaceServer/Auth/UserLogin"
    ).mock(
        return_value=httpx.Response(200, json={"Data": {"Token": "abc123"}})
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
    assert login_route.called


@respx.mock
@pytest.mark.asyncio
async def test_request_raises_api_error_for_bad_status():
    respx.get("https://api.example.com/v1/status").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )

    async with PionPowerAPIClient("https://api.example.com/v1") as client:
        with pytest.raises(APIError) as exc_info:
            await client._PionPowerAPIClient__get("/status")

    assert exc_info.value.status_code == 404
    assert "Not found" in str(exc_info.value)


@respx.mock
@pytest.mark.asyncio
async def test_get_realtime_data_by_device_code():
    route = respx.post(
        "https://api.example.com/v1/APPInterfaceServer/RealData/GetRealDataByDeviceCode"
    ).mock(
        return_value=httpx.Response(200, json={"data": "realtime"})
    )

    async with PionPowerAPIClient("https://api.example.com/v1") as client:
        result = await client.get_realtime_data_by_device_code("DEV123")

    assert result == {"data": "realtime"}
    assert route.called
