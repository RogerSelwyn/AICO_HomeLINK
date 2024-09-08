"""Test setup process."""

from .conftest import HomelinkMockConfigEntry
from .helpers.utils import check_entity_state


async def test_init(
    hass,
    setup_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test HomeLINK initialization."""

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
