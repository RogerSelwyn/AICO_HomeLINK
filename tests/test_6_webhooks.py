"""Test setup process."""

from dataclasses import dataclass
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from aiohttp.test_utils import TestClient
import pytest
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from homeassistant.components.webhook import async_generate_url
from homeassistant.core import Event

from .conftest import HomelinkMockConfigEntry
from .helpers.utils import load_json


@dataclass
class WebhookSetupData:
    """A collection of data set up by the webhook_setup fixture."""

    hass: any
    client: TestClient
    webhook_url: str
    event_listener: Mock
    events: any


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

    events = []

    async def event_listener(event: Event) -> None:
        events.append(event)

    hass.bus.async_listen("homelink_alert", event_listener)

    return WebhookSetupData(hass, client, webhook_url, event_listener, events)


async def test_webhook_alert(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook alert receival."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_json("../data/webhook_alert.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_alert"
    assert async_refresh.called
    resp.close()
