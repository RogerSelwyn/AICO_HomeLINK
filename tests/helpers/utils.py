"""Utilities for HomeLINK testing."""

import pathlib

from .const import BASE_API_URL


def check_entity_state(hass, entity_name, entity_state, entity_attributes=None):
    """Check entity state."""
    state = hass.states.get(entity_name)
    # print("***************************")
    # print(state)
    # print(state.attributes)
    assert state.state == entity_state
    if entity_attributes:
        assert state.attributes == entity_attributes


def create_mock(aioclient_mock, url, filename):
    """Create a mock."""
    aioclient_mock.get(
        f"{BASE_API_URL}{url}",
        text=_load_json(f"../data/{filename}"),
    )


def _load_json(filename):
    """Load a json file."""
    return pathlib.Path(__file__).parent.joinpath(filename).read_text(encoding="utf8")


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
