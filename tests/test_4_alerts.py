"""Test alertss."""

import pytest

from homeassistant.core import HomeAssistant

from .conftest import HomelinkMockConfigEntry
from .helpers.utils import async_check_sensor, check_entity_state
from .state.core_state import ALARM_BAD, ENVIRONMENT_BAD
from .state.device_state import (
    CARBONDIOXIDE,
    HALLWAY1_ENVCO2SENSOR_BAD,
    HUMIDITY,
    LIVINGROOM_FIREALARM_BAD,
    TEMPERATURE,
)


@pytest.mark.parametrize(
    "setup_base_integration", ["environment_alert_mocks"], indirect=True
)
async def test_environment_entity_alert_states(
    hass: HomeAssistant,
    setup_base_integration: None,
):
    """Test HomeLINK alerts."""

    check_entity_state(
        hass, "binary_sensor.dummy_user_my_house_environment", "on", ENVIRONMENT_BAD
    )

    await async_check_sensor(
        hass,
        "hallway1_envco2sensor",
        "on",
        HALLWAY1_ENVCO2SENSOR_BAD,
        "unknown",
        "2033-08-15",
    )
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


@pytest.mark.parametrize("setup_base_integration", ["alarm_alert_mocks"], indirect=True)
async def test_alarm_alert_state(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test HomeLINK alerts."""
    coordinator = base_config_entry.runtime_data.coordinator
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    check_entity_state(hass, "binary_sensor.dummy_user_my_house_alarm", "on", ALARM_BAD)

    await async_check_sensor(
        hass,
        "livingroom_firealarm",
        "on",
        LIVINGROOM_FIREALARM_BAD,
        "2024-09-06T09:05:16+00:00",
        "2034-06-26",
    )
