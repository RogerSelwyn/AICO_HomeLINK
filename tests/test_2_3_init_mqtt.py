"""Test setup process."""

import pytest
from pytest_homeassistant_custom_component.typing import MqttMockHAClient

from homeassistant.core import HomeAssistant

from .conftest import HomelinkMockConfigEntry
from .helpers.utils import check_entity_state


@pytest.mark.parametrize("expected_lingering_timers", [True])
async def test_mqtt_init(
    hass: HomeAssistant,
    setup_mqtt_integration,
    mqtt_mock: MqttMockHAClient,
    mqtt_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test full HomeLINK initialisation with mqtt."""

    assert mqtt_config_entry.runtime_data.mqtt
    check_entity_state(hass, "event.dummy_user_my_house_event", "unknown")
    check_entity_state(
        hass, "event.dummy_user_my_house_livingroom_firealarm_event", "unknown"
    )
