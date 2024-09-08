# pylint: disable=protected-access,redefined-outer-name
"""Global fixtures for integration."""

from collections.abc import Generator
from datetime import date
import sys
import time
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.homelink import HLData
from custom_components.homelink.const import DOMAIN
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.config import async_process_ha_core_config
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from .helpers.const import BASE_CONFIG_ENTRY, CLIENT_ID, CLIENT_SECRET, TITLE
from .helpers.utils import create_mock

pytest_plugins = "pytest_homeassistant_custom_component"  # pylint: disable=invalid-name
THIS_MODULE = sys.modules[__name__]


class HomelinkMockConfigEntry(MockConfigEntry):
    """Mock config entry with Homelink runtime_data."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialise HomelinkMockConfigEntry."""
        self.runtime_data: HLData = None
        super().__init__(*args, **kwargs)


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # pylint: disable=unused-argument
    """Automatically enable loading custom integrations in all tests."""
    return


@pytest.fixture(autouse=True)
async def request_setup(current_request_with_host: None) -> None:  # pylint: disable=unused-argument
    """Request setup."""


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Mock setting up a config entry."""
    with patch(
        "custom_components.homelink.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
async def setup_credentials(hass: HomeAssistant) -> None:
    """Fixture to setup application credentials component."""
    await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(CLIENT_ID, CLIENT_SECRET),
    )


@pytest.fixture
def expires_at() -> int:
    """Fixture to set the oauth token expiration time."""
    return time.time() + (20 * 60 * 60)


@pytest.fixture
def base_config_entry(hass: HomeAssistant, expires_at: int) -> HomelinkMockConfigEntry:
    """Create HomeLINK entry in Home Assistant."""
    data = BASE_CONFIG_ENTRY
    data["expires_at"] = expires_at
    entry = HomelinkMockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        unique_id=DOMAIN,
        data=data,
    )
    entry.runtime_data = None
    return entry


@pytest.fixture
async def setup_integration(
    request,
    hass,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
    base_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Fixture for setting up the component."""
    if hasattr(request, "param"):
        method_name = request.param
    else:
        method_name = "standard_mocks"

    mock_method = getattr(THIS_MODULE, method_name)
    mock_method(aioclient_mock)

    base_config_entry.add_to_hass(hass)

    await async_process_ha_core_config(
        hass,
        {"external_url": "https://example.com"},
    )

    await hass.config_entries.async_setup(base_config_entry.entry_id)


def standard_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Specific standard mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "lookup.json")
    create_mock(aioclient_mock, "/property", "property.json")
    create_mock(aioclient_mock, "/device", "device.json")
    create_mock(aioclient_mock, "/property/DUMMY_USER_My_House/alerts", "alerts.json")
    url = f"/property/DUMMY_USER_My_House/readings?date={date.today()}"
    create_mock(aioclient_mock, url, "readings.json")


def environment_alert_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Alert mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "lookup.json")
    create_mock(aioclient_mock, "/property", "property.json")
    create_mock(aioclient_mock, "/device", "device.json")
    create_mock(
        aioclient_mock,
        "/property/DUMMY_USER_My_House/alerts",
        "alerts_environment.json",
    )
    url = f"/property/DUMMY_USER_My_House/readings?date={date.today()}"
    create_mock(aioclient_mock, url, "readings.json")


def alarm_alert_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Alert mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "lookup.json")
    create_mock(aioclient_mock, "/property", "property.json")
    create_mock(aioclient_mock, "/device", "device.json")
    create_mock(
        aioclient_mock,
        "/property/DUMMY_USER_My_House/alerts",
        "alerts_alarm.json",
    )
    url = f"/property/DUMMY_USER_My_House/readings?date={date.today()}"
    create_mock(aioclient_mock, url, "readings.json")
