"""Test setup process."""

from dataclasses import dataclass
from unittest.mock import Mock

from aiohttp.test_utils import TestClient
import pytest
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from homeassistant.components.webhook import async_generate_url

from .conftest import HomelinkMockConfigEntry


@dataclass
class WebhookSetupData:
    """A collection of data set up by the webhook_setup fixture."""

    hass: any
    client: TestClient
    webhook_url: str
    event_listener: Mock


@pytest.fixture
async def webhook_setup(
    hass,
    setup_webhook_integration,
    webhook_config_entry: HomelinkMockConfigEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> WebhookSetupData:
    """Set up integration, client and webhook url."""

    client = await hass_client_no_auth()
    webhook_id = webhook_config_entry.options["webhook_id"]
    webhook_url = async_generate_url(hass, webhook_id)
    event_listener = Mock()
    # hass.bus.async_listen(MONZO_EVENT, event_listener)

    return WebhookSetupData(hass, client, webhook_url, event_listener)


async def test_webhook_init(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test full HomeLINK initialisation with webhooks."""
    assert webhook_config_entry.runtime_data.webhook
