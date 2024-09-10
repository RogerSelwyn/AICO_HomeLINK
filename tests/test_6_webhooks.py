"""Test setup process."""

from dataclasses import dataclass
from unittest.mock import Mock, patch
from urllib.parse import urlparse

from aiohttp.test_utils import TestClient
import pytest
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from homeassistant.components.webhook import async_generate_url
from homeassistant.core import Event, HomeAssistant

from .conftest import HomelinkMockConfigEntry
from .helpers.utils import check_entity_state, load_json


@dataclass
class WebhookSetupData:
    """A collection of data set up by the webhook_setup fixture."""

    hass: HomeAssistant
    client: TestClient
    webhook_url: str
    event_listener: Mock
    events: any


@pytest.fixture
async def webhook_setup(
    hass: HomeAssistant,
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
    hass.bus.async_listen("homelink_device", event_listener)
    hass.bus.async_listen("homelink_notification", event_listener)
    hass.bus.async_listen("homelink_property", event_listener)
    hass.bus.async_listen("homelink_reading", event_listener)
    hass.bus.async_listen("homelink_unknown", event_listener)

    return WebhookSetupData(hass, client, webhook_url, event_listener, events)


async def test_webhook_property_alert(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook alert receival and no refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_json("../data/webhook_property_alert.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 0
    assert not async_refresh.called
    resp.close()


async def test_webhook_device_alert(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook alert receival and refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_json("../data/webhook_device_alert.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_alert"
    assert async_refresh.called
    resp.close()


async def test_webhook_device_reading(
    hass: HomeAssistant,
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook reading receival and reading sensor update."""

    resp = await webhook_setup.client.post(
        urlparse(webhook_setup.webhook_url).path,
        json=load_json("../data/webhook_device_reading.json"),
    )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_reading"
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_humidity",
        "57.7",
    )
    resp.close()


async def test_webhook_notification(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook notification receival and ignore."""

    resp = await webhook_setup.client.post(
        urlparse(webhook_setup.webhook_url).path,
        json=load_json("../data/webhook_notification.json"),
    )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 0

    resp.close()


async def test_webhook_property_add(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook property receival and refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_json("../data/webhook_property_add.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_property"
    assert async_refresh.called
    resp.close()


async def test_webhook_device_add(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook device receival and refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_json("../data/webhook_device_add.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_device"
    assert async_refresh.called
    resp.close()


async def test_webhook_unknown_message(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook unknown message handling."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_json("../data/webhook_unknown_type.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 0
    assert not async_refresh.called
    resp.close()
