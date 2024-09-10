"""Test setup process."""

# import pytest

# from .conftest import MQTTSetupData
# from .helpers.utils import fire_mqtt

# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_notification(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt notification receipt."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/notification/sms/02597ad6-de64-43ce-8f4d-133b3d970636",
#         "notification.json",
#     )

#     assert len(mqtt_setup.events) == 0
#     assert not async_refresh.called


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_property_add(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt property receipt and refresh start."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/property/dummy_user_my_house/add",
#         "property_add.json",
#     )

#     assert len(mqtt_setup.events) == 1
#     assert mqtt_setup.events[0].event_type == "homelink_property"
#     assert async_refresh.called


# @pytest.mark.parametrize("expected_lingering_timers", [True])
# @pytest.mark.timeout(30)
# async def test_mqtt_device_add(
#     mqtt_setup: MQTTSetupData,
# ) -> None:
#     """Test mqtt device receipt and refresh start."""

#     async_refresh = await fire_mqtt(
#         mqtt_setup.hass,
#         "dummy_user/device/dummy_user_my_house/add",
#         "device_add.json",
#     )

#     assert len(mqtt_setup.events) == 1
#     assert mqtt_setup.events[0].event_type == "homelink_device"
#     assert async_refresh.called
