"""Test alertss."""

import pytest

from homeassistant.core import HomeAssistant

from .conftest import HomelinkMockConfigEntry
from .data.state.core_state import ALARM_BAD, ENVIRONMENT_BAD
from .data.state.device_state import HALLWAY1_ENVCO2SENSOR_BAD, LIVINGROOM_FIREALARM_BAD
from .helpers.utils import async_check_sensor, check_entity_state


@pytest.mark.parametrize(
    "setup_base_integration",
    [{"method_name": "environment_alert_mocks", "enabled": True}],
    indirect=True,
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


@pytest.mark.parametrize(
    "setup_base_integration",
    [{"method_name": "alarm_alert_mocks", "enabled": True}],
    indirect=True,
)
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
