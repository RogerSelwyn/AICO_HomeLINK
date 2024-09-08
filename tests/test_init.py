"""Test setup process."""

from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from . import check_entity_state, setup_integration
from .conftest import HomelinkMockConfigEntry


async def test_init(
    hass,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test HomeLINK initialization."""

    await setup_integration(hass, aioclient_mock, base_config_entry)
    assert hasattr(base_config_entry.runtime_data, "options")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house", "off")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house_alarm", "off")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house_environment", "off")
    assert (
        hass.states.get(
            "binary_sensor.dummy_user_my_house_hallway1_envco2sensor_abandonment"
        )
        is None
    )
