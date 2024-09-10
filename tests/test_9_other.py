"""Test odds and sods."""

from unittest.mock import patch

from pyhomelink.exceptions import ApiException, AuthException
import pytest

from custom_components.homelink.const import DOMAIN
from custom_components.homelink.diagnostics import async_get_config_entry_diagnostics
from homeassistant.core import HomeAssistant

from .conftest import HomelinkMockConfigEntry


async def test_diagnostics(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test Diagnostics."""
    result = await async_get_config_entry_diagnostics(hass, base_config_entry)

    assert "config_entry_data" in result
    assert "auth_implementation" in result["config_entry_data"]
    assert result["config_entry_data"]["auth_implementation"] == DOMAIN
    assert "token" in result["config_entry_data"]
    assert result["config_entry_data"]["token"]["access_token"] == "**REDACTED**"
    assert result["config_entry_data"]["token"]["refresh_token"] is None


async def test_coordinator_auth_error(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    caplog: pytest.LogCaptureFixture,
):
    """Test for coordinator auth error."""
    coordinator = base_config_entry.runtime_data.coordinator
    with (
        patch(
            "custom_components.homelink.helpers.coordinator.HomeLINKDataCoordinator._async_get_core_data",
            side_effect=AuthException(),
        ),
    ):
        await coordinator.async_refresh()

    assert "Error authenticating with HL API" in caplog.text


async def test_coordinator_api_error(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    caplog: pytest.LogCaptureFixture,
):
    """Test for coordinator api error."""
    coordinator = base_config_entry.runtime_data.coordinator

    with (
        patch(
            "custom_components.homelink.helpers.coordinator.HomeLINKDataCoordinator._async_get_core_data",
            side_effect=ApiException(),
        ),
    ):
        await coordinator.async_refresh()

    assert "Error communicating with HL API" in caplog.text
