"""Utilities for HomeLINK testing."""

from datetime import date
import json
import pathlib

from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from .const import BASE_API_URL, TOKEN_URL


def check_entity_state(
    hass,
    entity_name,
    entity_state,
    entity_attributes=None,
):
    """Check entity state."""
    state = hass.states.get(entity_name)
    # print("*************************** State")
    # print(state.state)
    assert state.state == entity_state
    if entity_attributes:
        # print("*************************** State Attributes")
        # print(state.attributes)
        assert state.attributes == entity_attributes


def create_mock(aioclient_mock, url, filename):
    """Create a mock."""
    aioclient_mock.get(
        f"{BASE_API_URL}{url}",
        text=load_json_txt(f"../data/{filename}"),
    )


def load_json_txt(filename):
    """Load a json file as string."""
    return pathlib.Path(__file__).parent.joinpath(filename).read_text(encoding="utf8")


def load_json(filename):
    """Load a json file."""
    return json.load(
        open(pathlib.Path(__file__).parent.joinpath(filename), encoding="utf8")
    )


async def async_check_sensor(
    hass,
    device_name,
    entity_state,
    entity_attributes,
    last_tested_date,
    replace_by_date,
):
    """Check the entity state."""
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


# async def fire_mqtt(hass, topic, payload):
#     """Fire and MQTT trigger."""
#     with patch(
#         "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
#     ) as async_refresh:
#         await hass.async_add_executor_job(
#             async_fire_mqtt_message,
#             hass,
#             topic,
#             load_json_txt(f"../data/mqtt/{payload}"),
#         )

#     await hass.async_block_till_done()
#     return async_refresh


def mock_token_call(aioclient_mock, token, post=False):
    """Mock the call url."""
    if not post:
        aioclient_mock.get(
            TOKEN_URL,
            json={"accessToken": token},
        )
    else:
        aioclient_mock.post(
            TOKEN_URL,
            json={"access_token": token},
        )


def add_property_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Specific add property mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "base/lookup.json")
    create_mock(aioclient_mock, "/property", "base/propertyx2.json")
    create_mock(aioclient_mock, "/device", "base/devicex2.json")
    create_mock(
        aioclient_mock, "/property/DUMMY_USER_My_House/alerts", "base/alerts.json"
    )
    create_mock(
        aioclient_mock, "/property/DUMMY_USER_My_New_House/alerts", "base/alerts.json"
    )
    create_mock(
        aioclient_mock,
        f"/property/DUMMY_USER_My_House/readings?date={date.today()}",
        "base/readings.json",
    )
    create_mock(
        aioclient_mock,
        f"/property/DUMMY_USER_My_New_House/readings?date={date.today()}",
        "base/readingsx2.json",
    )
    create_mock(aioclient_mock, "/insight", "base/insight.json")


def add_device_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Specific add property mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "base/lookup.json")
    create_mock(aioclient_mock, "/property", "base/property.json")
    create_mock(aioclient_mock, "/device", "base/devicex3.json")
    create_mock(
        aioclient_mock, "/property/DUMMY_USER_My_House/alerts", "base/alerts.json"
    )
    create_mock(
        aioclient_mock,
        f"/property/DUMMY_USER_My_House/readings?date={date.today()}",
        "base/readings.json",
    )
    create_mock(aioclient_mock, "/insight", "base/insight.json")


def ignore_reading_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Specific add property mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "base/lookup.json")
    create_mock(aioclient_mock, "/property", "base/property.json")
    create_mock(aioclient_mock, "/device", "base/device.json")
    create_mock(
        aioclient_mock, "/property/DUMMY_USER_My_House/alerts", "base/alerts.json"
    )
    create_mock(
        aioclient_mock,
        f"/property/DUMMY_USER_My_House/readings?date={date.today()}",
        "base/readings_ignore.json",
    )
    create_mock(aioclient_mock, "/insight", "base/insight.json")
