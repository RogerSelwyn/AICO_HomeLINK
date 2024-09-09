"""Test setup process."""

from unittest.mock import Mock, patch

from aiohttp import ClientConnectorError, ClientResponseError
import pytest

from custom_components.homelink import async_setup_entry
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .conftest import HomelinkMockConfigEntry
from .helpers.utils import check_entity_state


async def test_setup_errors(
    hass,
    setup_credentials: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test for setup errors."""
    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientResponseError(
                None,
                None,
                status=401,
            ),
        ),
        pytest.raises(ConfigEntryAuthFailed),
    ):
        await async_setup_entry(hass, base_config_entry)

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientResponseError(None, None, status=500),
        ),
        pytest.raises(ClientResponseError),
    ):
        await async_setup_entry(hass, base_config_entry)

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientConnectorError(Mock(), OSError()),
        ),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(hass, base_config_entry)


async def test_full_init(
    hass,
    setup_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test full HomeLINK initialisation."""

    assert hasattr(base_config_entry.runtime_data, "options")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house", "off")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house_alarm", "off")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house_environment", "off")
    assert (
        hass.states.get("sensor.dummy_user_my_house_hallway1_envco2sensor_abandonment")
        is None
    )
