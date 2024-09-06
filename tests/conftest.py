# pylint: disable=protected-access,redefined-outer-name
"""Global fixtures for integration."""

import time
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.application_credentials import (
    ClientCredential, async_import_client_credential)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.homelink import HLData
from custom_components.homelink.const import DOMAIN

CLIENT_ID = "1234"
CLIENT_SECRET = "5678"
# REDIRECT_URI = "https://example.com/auth/external/callback"
BASE_AUTH_URL = "https://auth.live.homelync.io"
TOKEN = "longtoken"
TITLE ="mock"

pytest_plugins = "pytest_homeassistant_custom_component"  # pylint: disable=invalid-name

class HomelinkMockConfigEntry(MockConfigEntry):
    """Mock config entry with Homelink runtime_data."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialise HomelinkMockConfigEntry."""
        self.runtime_data: HLData = None
        super().__init__(*args, **kwargs)

# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations): # pylint: disable=unused-argument
    """Automatically enable loading custom integrations in all tests."""
    return

@pytest.fixture(autouse=True)
async def request_setup(current_request_with_host: None) -> None:
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
def polling_config_entry(expires_at: int) ->HomelinkMockConfigEntry:
    """Create Monzo entry in Home Assistant."""
    entry = HomelinkMockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        unique_id=DOMAIN,
        data={
            "auth_implementation": DOMAIN,
            "token": {
                "access_token": TOKEN,
                "refresh_token": None,
                "scope": "standard",
                "token_type": "bearer",
                "expires_in": 72000,
                "expires_at": expires_at,
            }
        },
    )
    entry.runtime_data = None
    return entry
