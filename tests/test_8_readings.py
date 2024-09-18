"""Test readings."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .conftest import HomelinkMockConfigEntry
from .data.state.device_state import CARBONDIOXIDE, HUMIDITY, TEMPERATURE
from .helpers.utils import check_entity_state, ignore_reading_mocks


@pytest.mark.parametrize(
    "setup_base_integration", ["environment_alert_mocks"], indirect=True
)
async def test_environment_entity_alert_states(
    hass: HomeAssistant,
    setup_base_integration: None,
):
    """Test HomeLINK alerts."""

    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_carbon_dioxide",
        "1031",
        CARBONDIOXIDE,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_humidity",
        "84.5",
        HUMIDITY,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_temperature",
        "20.46",
        TEMPERATURE,
    )


async def test_readings_update_throttled(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test readings update is throttled."""
    coordinator = base_config_entry.runtime_data.coordinator

    with patch(
        "custom_components.homelink.helpers.coordinator.HomeLINKDataCoordinator._async_retrieve_readings",
    ) as async_retrieve_readings:
        await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert not async_retrieve_readings.called


@patch(
    "custom_components.homelink.helpers.coordinator.RETRIEVAL_INTERVAL_READINGS",
    timedelta(minutes=0),
)
async def test_readings_update(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test readings update with throttle removed."""
    coordinator = base_config_entry.runtime_data.coordinator

    # This also runs a test through to ensure the invalid reading device code is tested.
    # Not clear how to asset this is true
    aioclient_mock.clear_requests()
    ignore_reading_mocks(aioclient_mock)

    with patch(
        "custom_components.homelink.helpers.coordinator.HomeLINKDataCoordinator._async_retrieve_readings",
    ) as async_retrieve_readings:
        await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert async_retrieve_readings.called


@patch(
    "custom_components.homelink.helpers.coordinator.RETRIEVAL_INTERVAL_READINGS",
    timedelta(minutes=0),
)
async def test_readings_ignored(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test readings update with throttle removed."""
    coordinator = base_config_entry.runtime_data.coordinator

    aioclient_mock.clear_requests()
    ignore_reading_mocks(aioclient_mock)

    with patch(
        "custom_components.homelink.sensor.HomeLINKReadingSensor._update_values",
    ) as update_values:
        await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert not update_values.called
