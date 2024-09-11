"""Test setup process."""

# from unittest import mock
# from unittest.mock import ANY, call

# import pytest
# from pytest_homeassistant_custom_component.typing import MqttMockHAClient

# from .conftest import HomelinkMockConfigEntry, MQTTSetupData
# from .helpers.utils import check_entity_state

# @pytest.mark.parametrize("expected_lingering_timers", [True])
# async def test_mqtt_ha_init(
#     mqtt_ha_setup: MQTTSetupData,
#     mqtt_mock: MqttMockHAClient,
#     mqtt_ha_config_entry: HomelinkMockConfigEntry,
# ) -> None:
#     """Test full HomeLINK initialisation with mqtt."""

#     assert mqtt_ha_config_entry.runtime_data.mqtt
#     check_entity_state(mqtt_ha_setup.hass, "event.dummy_user_my_house_event", "unknown")
#     check_entity_state(
#         mqtt_ha_setup.hass,
#         "event.dummy_user_my_house_livingroom_firealarm_event",
#         "unknown",
#     )
#     mqtt_call = call("dummy_user/#", mock.ANY, 2, "utf-8", ANY)
#     assert mqtt_call in mqtt_mock.async_subscribe.call_args_list


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# async def test_mqtt_hl_init(
#     mqtt_hl_setup: MQTTSetupData,
#     mqtt_mock: MqttMockHAClient,
#     mqtt_hl_config_entry: HomelinkMockConfigEntry,
# ) -> None:
#     """Test full HomeLINK initialisation with mqtt."""

#     assert mqtt_hl_config_entry.runtime_data.mqtt
