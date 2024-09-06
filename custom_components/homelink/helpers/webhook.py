"""Webhook management for HomeLINK."""

import logging

import aiohttp
from aiohttp.hdrs import METH_POST
from homeassistant.components import webhook
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import dispatcher_send

from ..const import (
    ALARMTYPE_ALARM,
    DOMAIN,
    HOMELINK_MESSAGE_MQTT,
    WEBHOOK_ACTION,
    WEBHOOK_DEVICECOUNT,
    WEBHOOK_DEVICESERIALNUMBER,
    WEBHOOK_NAME,
    WEBHOOK_NOTIFICATIONID,
    WEBHOOK_PROPERTY_REFERENCE,
    WEBHOOK_READINGTYPEID,
    WEBHOOK_REPLACEBYDATE,
    WEBHOOK_STATUSID,
    HomeLINKMessageType,
)

_LOGGER = logging.getLogger(__name__)
ALLOWED_METHODS = [METH_POST]


class HomeLINKWebhook:
    """HomeLINK Webhooks."""

    def __init__(self):
        """Initialise the webhooks."""

    def register_webhooks(self, hass, webhook_id):
        """Register the required webhooks with Home Assistant."""

        webhook.async_register(
            hass,
            DOMAIN,
            WEBHOOK_NAME,
            webhook_id,
            self._async_handle_webhook,
            allowed_methods=ALLOWED_METHODS,
        )
        _LOGGER.debug("HomeLINK Webhook registered")

    def unregister_webhooks(self, hass, webhook_id):
        """Unregister the required webhooks with Home Assistant."""
        webhook.async_unregister(hass, webhook_id)
        _LOGGER.debug("HomeLINK Webhook unregistered")

    async def _async_handle_webhook(
        self,
        hass: HomeAssistant,
        webhook_id: str,  # pylint: disable=unused-argument
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        """Handle webhook callback."""
        message = await request.json()
        messagetype, actiontype = self._identify_message(message)

        # Ignore Notifications. No Insights or InsightComponents via Webhooks
        if messagetype in [
            HomeLINKMessageType.MESSAGE_INSIGHT,
            HomeLINKMessageType.MESSAGE_INSIGHTCOMPONENT,
            HomeLINKMessageType.MESSAGE_NOTIFICATION,
        ]:
            return

        _LOGGER.debug("Webhook message: %s - %s - %s", actiontype, messagetype, message)

        key = message[WEBHOOK_PROPERTY_REFERENCE]

        # Property/Device added or deleted, so route to property binary sensor to trigger refresh
        if messagetype in [
            HomeLINKMessageType.MESSAGE_DEVICE,
            HomeLINKMessageType.MESSAGE_PROPERTY,
        ]:
            await self._async_property_device_update_message(
                hass, key, actiontype, message, messagetype
            )
            return

        # No Event messages via Webhook

        # Device alert or reading so route to device binary sensor for onward handling
        if (
            messagetype
            in [HomeLINKMessageType.MESSAGE_ALERT, HomeLINKMessageType.MESSAGE_READING]
            and WEBHOOK_DEVICESERIALNUMBER in message
            and message[WEBHOOK_DEVICESERIALNUMBER]
        ):
            await self._async_device_message(hass, actiontype, message, messagetype)
            return

        return

    def _identify_message(self, message):
        actiontype = message[WEBHOOK_ACTION]
        if WEBHOOK_DEVICECOUNT in message:
            messagetype = HomeLINKMessageType.MESSAGE_PROPERTY
        elif WEBHOOK_REPLACEBYDATE in message:
            messagetype = HomeLINKMessageType.MESSAGE_DEVICE
        elif WEBHOOK_STATUSID in message:
            messagetype = HomeLINKMessageType.MESSAGE_ALERT
        elif WEBHOOK_READINGTYPEID in message:
            messagetype = HomeLINKMessageType.MESSAGE_READING
        elif WEBHOOK_NOTIFICATIONID in message:
            messagetype = HomeLINKMessageType.MESSAGE_NOTIFICATION
        else:
            messagetype = HomeLINKMessageType.MESSAGE_UNKNOWN
        return messagetype, actiontype

    async def _async_property_device_update_message(
        self, hass, key, topic, message, messagetype
    ):
        event = HOMELINK_MESSAGE_MQTT.format(
            domain=DOMAIN, key=f"{key}_{ALARMTYPE_ALARM}"
        ).lower()
        dispatcher_send(hass, event, topic, message, messagetype)

    async def _async_device_message(self, hass, topic, message, messagetype):
        serialnumber = message[WEBHOOK_DEVICESERIALNUMBER]
        event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=serialnumber).lower()
        dispatcher_send(hass, event, message, topic, messagetype)
