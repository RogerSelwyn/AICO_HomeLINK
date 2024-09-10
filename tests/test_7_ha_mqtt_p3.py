"""Test setup process."""

# import pytest

# from .conftest import MQTTSetupData
# from .helpers.utils import fire_mqtt

# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_property_event(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt property event handling."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/event/dummy_user_my_house/abandonment/abandonment-risk-low",
#         "property_event.json",
#     )

#     assert not async_refresh.called
#     assert (
#         mqtt_setup.hass.states.get("event.dummy_user_my_house_event").attributes[
#             "event_type"
#         ]
#         == "ABANDONMENT_RISK_LOW"
#     )
#     assert (
#         mqtt_setup.hass.states.get("event.dummy_user_my_house_event").attributes[
#             "statusid"
#         ]
#         == "ACTIVE"
#     )


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_device_event(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt device event handling."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/event/dummy_user_my_house/c3cec7fb/gateway-check-in",
#         "device_event.json",
#     )

#     assert not async_refresh.called
#     assert (
#         mqtt_setup.hass.states.get(
#             "event.dummy_user_my_house_kitchen_gateway_event"
#         ).attributes["event_type"]
#         == "GATEWAY_CHECK_IN"
#     )
#     assert (
#         mqtt_setup.hass.states.get(
#             "event.dummy_user_my_house_kitchen_gateway_event"
#         ).attributes["statusid"]
#         == "ACTIVE"
#     )


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_unknown_message(
#     mqtt_setup: MQTTSetupData,
#     caplog: pytest.LogCaptureFixture,
# ) -> None:
#     """Test mqtt unknown message handling."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/unknown/dummy_user_my_house/add",
#         "unknown_type.json",
#     )

#     assert not async_refresh.called
#     assert "Unknown MQTT message type: unknown" in caplog.text
