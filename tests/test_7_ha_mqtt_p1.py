"""Test setup process."""

# import pytest

# from .conftest import MQTTSetupData
# from .helpers.utils import check_entity_state, fire_mqtt

# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_property_alert(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test full HomeLINK initialisation with mqtt."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/alert/active/dummy_user_my_house/airquality/airquality-medium",
#         "property_alert.json",
#     )

#     assert len(mqtt_setup.events) == 1
#     assert mqtt_setup.events[0].event_type == "homelink_alert"
#     assert async_refresh.called


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_device_alert(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt device alert receipt and refresh start."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/alert/active/dummy_user_my_house/c3cec7fb-d6fcd4f0/head-removed",
#         "device_alert.json",
#     )

#     assert len(mqtt_setup.events) == 1
#     assert mqtt_setup.events[0].event_type == "homelink_alert"
#     assert async_refresh.called


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_device_reading(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt reading receipt and reading sensor update."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/reading/dummy_user_my_housen/c3cec7fb-001fd75f/environment-humidity-indoor",
#         "device_reading.json",
#     )

#     assert len(mqtt_setup.events) == 1
#     assert mqtt_setup.events[0].event_type == "homelink_reading"
#     check_entity_state(
#         mqtt_setup.hass,
#         "sensor.dummy_user_my_house_hallway1_envco2sensor_humidity",
#         "81.6",
#     )
#     assert not async_refresh.called
