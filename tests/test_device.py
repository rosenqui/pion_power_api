from unittest.mock import AsyncMock, MagicMock

import pytest

from pion_power_api.device import Device


def make_device(client=None) -> Device:
    if client is None:
        client = MagicMock()
    return Device(
        station_code="STN001",
        device_code="DEV001",
        device_name="Test Device",
        device_type="TypeA",
        parent_code="PARENT001",
        master_or_slave="Master",
        device_share_status="Shared",
        product_id="PID001",
        product_code="PCODE001",
        product_name="Product Name",
        hardware_version="HW1.0",
        software_version="SW2.0",
        upgrade_version="UV3.0",
        upgrade_progress="50%",
        client=client,
    )


def test_device_from_dict_and_to_dict_roundtrip():
    payload = {
        "StationCode": "STN001",
        "DeviceCode": "DEV001",
        "DeviceName": "Test Device",
        "DeviceType": "TypeA",
        "ParentCode": "PARENT001",
        "MasterOrSlave": "Master",
        "DeviceShareStatus": "Shared",
        "ProductId": "PID001",
        "ProductCode": "PCODE001",
        "ProductName": "Product Name",
        "HardwareVersion": "HW1.0",
        "SoftwareVersion": "SW2.0",
        "UpgradeVersion": "UV3.0",
        "UpgradeProgress": "50%",
    }

    client = MagicMock()
    device = Device.from_dict(payload, client=client)

    assert device.station_code == "STN001"
    assert device.device_code == "DEV001"
    assert device.software_version == "SW2.0"
    assert device.to_dict() == payload
    assert device.client is client


def test_device_from_dict_uses_soft_version_fallback():
    payload = {
        "StationCode": "STN001",
        "DeviceCode": "DEV001",
        "DeviceName": "Test Device",
        "DeviceType": "TypeA",
        "ParentCode": "PARENT001",
        "MasterOrSlave": "Master",
        "DeviceShareStatus": "Shared",
        "ProductId": "PID001",
        "ProductCode": "PCODE001",
        "ProductName": "Product Name",
        "HardwareVersion": "HW1.0",
        "SoftVersion": "SW-FALLBACK",
        "UpgradeVersion": "UV3.0",
        "UpgradeProgress": "50%",
    }

    device = Device.from_dict(payload, client=MagicMock())

    assert device.software_version == "SW-FALLBACK"


def test_device_equality_and_hash():
    payload = {
        "StationCode": "STN001",
        "DeviceCode": "DEV001",
        "DeviceName": "Test Device",
        "DeviceType": "TypeA",
        "ParentCode": "PARENT001",
        "MasterOrSlave": "Master",
        "DeviceShareStatus": "Shared",
        "ProductId": "PID001",
        "ProductCode": "PCODE001",
        "ProductName": "Product Name",
        "HardwareVersion": "HW1.0",
        "SoftwareVersion": "SW2.0",
        "UpgradeVersion": "UV3.0",
        "UpgradeProgress": "50%",
    }

    device_a = Device.from_dict(payload, client=MagicMock())
    device_b = Device.from_dict(payload, client=MagicMock())
    device_c = Device.from_dict(
        {**payload, "DeviceName": "Other Device"}, client=MagicMock()
    )

    assert device_a == device_b
    assert hash(device_a) == hash(device_b)
    assert device_a != device_c
    assert device_a != "not a device"


def test_device_repr_contains_device_code_and_station_code():
    device = make_device()
    repr_text = repr(device)

    assert "Device(" in repr_text
    assert "station_code='STN001'" in repr_text
    assert "device_code='DEV001'" in repr_text
    assert repr_text.endswith(")")


@pytest.mark.asyncio
async def test_get_realtime_data_delegates_to_client():
    client = MagicMock()
    client.get_realtime_data_by_device_code = AsyncMock(
        return_value={"signal1": "value1"}
    )
    device = make_device(client=client)

    result = await device.get_realtime_data()

    assert result == {"signal1": "value1"}
    client.get_realtime_data_by_device_code.assert_awaited_once_with("DEV001")


@pytest.mark.asyncio
async def test_get_stats_delegates_to_client():
    client = MagicMock()
    client.get_device_stats = AsyncMock(return_value="stats")
    device = make_device(client=client)

    result = await device.get_stats()

    assert result == "stats"
    client.get_device_stats.assert_awaited_once_with("DEV001")


@pytest.mark.asyncio
async def test_start_charging_sends_control_data():
    mock_set_control = AsyncMock(return_value=True)
    client = MagicMock()
    client.set_control_data = mock_set_control
    device = make_device(client=client)

    result = await device.start_charging(current=16, duration_hours=4)

    assert result is True
    mock_set_control.assert_awaited_once()
    args = mock_set_control.call_args.args
    assert args[0] == "DEV001"
    assert args[1] == "90100404"
    assert args[2] == 1
    assert args[3] == 0

    signal = args[4]
    assert signal.pile_sn == "DEV001"
    assert signal.status == 0
    assert signal.current == 16
    assert signal.duration == 4
    assert signal.start_time is None
    assert signal.power is None


@pytest.mark.asyncio
async def test_stop_charging_sends_stop_control_data():
    mock_set_control = AsyncMock(return_value=True)
    client = MagicMock()
    client.set_control_data = mock_set_control
    device = make_device(client=client)

    result = await device.stop_charging()

    assert result is True
    mock_set_control.assert_awaited_once()
    args = mock_set_control.call_args.args
    assert args[0] == "DEV001"
    assert args[1] == "90100404"
    assert args[2] == 1
    assert args[3] == 1

    signal = args[4]
    assert signal.pile_sn == "DEV001"
    assert signal.status == 1
    assert signal.power is None
    assert signal.current is None
    assert signal.duration is None
    assert signal.start_time is None
