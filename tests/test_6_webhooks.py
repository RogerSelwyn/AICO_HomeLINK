"""Test setup process."""

from unittest.mock import patch
from urllib.parse import urlparse

from .conftest import HomelinkMockConfigEntry, WebhookSetupData
from .helpers.utils import check_entity_state, load_webhook_json


async def test_webhook_property_environment_alert(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook alert receipt and no refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("property_environment_alert.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_alert"
    assert async_refresh.called
    resp.close()


async def test_webhook_property_fire_alert(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook alert receipt and no refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("property_fire_alert.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_alert"
    assert async_refresh.called
    resp.close()


async def test_webhook_device_alert(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook alert receipt and refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("device_alert.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_alert"
    assert async_refresh.called
    resp.close()


async def test_webhook_device_reading(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook reading receipt and reading sensor update."""

    resp = await webhook_setup.client.post(
        urlparse(webhook_setup.webhook_url).path,
        json=load_webhook_json("device_reading.json"),
    )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_reading"
    check_entity_state(
        webhook_setup.hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_humidity",
        "57.7",
    )
    resp.close()


async def test_webhook_device_reading_old(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook old alert receipt and ignore."""

    resp = await webhook_setup.client.post(
        urlparse(webhook_setup.webhook_url).path,
        json=load_webhook_json("device_alert_old.json"),
    )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 0

    resp.close()


async def test_webhook_notification(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook notification receipt and ignore."""

    resp = await webhook_setup.client.post(
        urlparse(webhook_setup.webhook_url).path,
        json=load_webhook_json("notification.json"),
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
    """Test webhook property receipt and refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("property_add.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_property"
    assert async_refresh.called
    resp.close()


async def test_webhook_property_add_old(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook old property receipt ignored."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("property_add_old.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 0
    assert not async_refresh.called
    resp.close()


async def test_webhook_device_add(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook device receipt and refresh start."""

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh",
    ) as async_refresh:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("device_add.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 1
    assert webhook_setup.events[0].event_type == "homelink_device"
    assert async_refresh.called
    resp.close()


async def test_webhook_ignored_property(
    webhook_setup: WebhookSetupData,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test webhook device receipt and refresh start."""

    with patch(
        "custom_components.homelink.helpers.webhook.HomeLINKWebhook._async_property_device_update_message",
    ) as update_message:
        resp = await webhook_setup.client.post(
            urlparse(webhook_setup.webhook_url).path,
            json=load_webhook_json("device_add_ignored_property.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert not update_message.called
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
            json=load_webhook_json("unknown_type.json"),
        )
    # Wait for remaining tasks to complete.
    await webhook_setup.hass.async_block_till_done()
    assert resp.ok
    assert len(webhook_setup.events) == 0
    assert not async_refresh.called
    resp.close()
