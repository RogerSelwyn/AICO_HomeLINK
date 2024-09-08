"""Test sensors."""

from homeassistant.helpers import device_registry as dr

from . import check_entity_state
from .conftest import HomelinkMockConfigEntry
from .state.core_state import ALARM_GOOD, ENVIRONMENT_GOOD, HOME_GOOD
from .state.device_state import (
    HALLWAY1_EIACCESSORY_GOOD,
    HALLWAY1_ENVCO2SENSOR_GOOD,
    KITCHEN_FIREALARM_GOOD,
    KITCHEN_GATEWAY_GOOD,
    LIVINGROOM_FIREALARM_GOOD,
    UTILITY_FIRECOALARM_GOOD,
)


async def test_device_count(
    setup_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
):
    """Test HomeLINK devices."""
    devices = device_registry.devices.get_devices_for_config_entry_id(
        base_config_entry.entry_id
    )

    assert len(devices) == 9


async def test_core_entities(
    hass,
    setup_integration: None,
):
    """Test HomeLINK core entities."""

    check_entity_state(hass, "binary_sensor.dummy_user_my_house", "off", HOME_GOOD)
    check_entity_state(
        hass, "binary_sensor.dummy_user_my_house_alarm", "off", ALARM_GOOD
    )
    check_entity_state(
        hass, "binary_sensor.dummy_user_my_house_environment", "off", ENVIRONMENT_GOOD
    )


async def test_ei3016(
    hass,
    setup_integration: None,
):
    """Test HomeLINK ei3016."""

    await _async_check_sensor(
        hass,
        "livingroom_firealarm",
        "off",
        LIVINGROOM_FIREALARM_GOOD,
        "2024-09-06T09:05:16+00:00",
        "2034-06-26",
    )


async def test_ei450(
    hass,
    setup_integration: None,
):
    """Test HomeLINK ei450."""

    await _async_check_sensor(
        hass,
        "hallway1_eiaccessory",
        "off",
        HALLWAY1_EIACCESSORY_GOOD,
        "2024-09-06T09:05:16+00:00",
        "2034-07-03",
    )


async def test_ei1000g(
    hass,
    setup_integration: None,
):
    """Test HomeLINK ei1000g."""

    await _async_check_sensor(
        hass,
        "kitchen_gateway",
        "off",
        KITCHEN_GATEWAY_GOOD,
        "unknown",
        "2034-04-24",
    )


async def test_ei1025(
    hass,
    setup_integration: None,
):
    """Test HomeLINK ei1025."""

    await _async_check_sensor(
        hass,
        "hallway1_envco2sensor",
        "off",
        HALLWAY1_ENVCO2SENSOR_GOOD,
        "unknown",
        "2033-08-15",
    )


async def test_ei3014(
    hass,
    setup_integration: None,
):
    """Test HomeLINK ei3014."""

    await _async_check_sensor(
        hass,
        "kitchen_firealarm",
        "off",
        KITCHEN_FIREALARM_GOOD,
        "2024-09-06T09:05:16+00:00",
        "2034-05-08",
    )


async def test_ei3028(
    hass,
    setup_integration: None,
):
    """Test HomeLINK ei3028."""

    await _async_check_sensor(
        hass,
        "utility_firecoalarm",
        "off",
        UTILITY_FIRECOALARM_GOOD,
        "2024-09-06T09:05:16+00:00",
        "2034-05-29",
    )


async def _async_check_sensor(
    hass,
    device_name,
    entity_state,
    entity_attributes,
    last_tested_date,
    replace_by_date,
):
    check_entity_state(
        hass,
        f"binary_sensor.dummy_user_my_house_{device_name}",
        entity_state,
        entity_attributes,
    )
    check_entity_state(
        hass,
        f"sensor.dummy_user_my_house_{device_name}_last_tested_date",
        last_tested_date,
    )
    check_entity_state(
        hass,
        f"sensor.dummy_user_my_house_{device_name}_replace_by_date",
        replace_by_date,
    )
