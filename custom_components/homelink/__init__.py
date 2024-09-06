"""Initialise the HomeLINK integration."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_WEBHOOK_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from pyhomelink.api import HomeLINKApi

from .const import (
    CONF_MQTT_ENABLE,
    CONF_MQTT_HOMELINK,
    CONF_WEBHOOK_ENABLE,
    COORD_PROPERTIES,
)
from .helpers.api import AsyncConfigEntryAuth
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.mqtt import HAMQTT, HomeLINKMQTT
from .helpers.webhook import HomeLINKWebhook

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.EVENT]

HLConfigEntry = ConfigEntry["HLData"]


@dataclass
class HLData:
    """Data previously stored in hass.data."""

    coordinator: HomeLINKDataCoordinator
    mqtt: any
    webhook: HomeLINKWebhook
    options: MappingProxyType[str, Any]


async def async_setup_entry(hass: HomeAssistant, entry: HLConfigEntry) -> bool:
    """Set up HomeLINK from a config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    try:
        await session.async_ensure_token_valid()
    except aiohttp.client_exceptions.ClientResponseError as err:
        if err.status == 401:
            raise ConfigEntryAuthFailed from err
        raise
    except aiohttp.client_exceptions.ClientConnectorError as err:
        raise ConfigEntryNotReady from err

    hl_api = HomeLINKApi(
        AsyncConfigEntryAuth(aiohttp_client.async_get_clientsession(hass), session)
    )

    entry.runtime_data = HLData(None, None, None, None)
    hl_coordinator = HomeLINKDataCoordinator(hass, hl_api, entry)
    await hl_coordinator.async_config_entry_first_refresh()
    entry.runtime_data.coordinator = hl_coordinator

    if entry.options.get(CONF_MQTT_ENABLE):
        hl_mqtt = await _async_start_mqtt(hass, entry)
        entry.runtime_data.mqtt = hl_mqtt

    if entry.options.get(CONF_WEBHOOK_ENABLE):
        hl_webhook = HomeLINKWebhook()
        hl_webhook.register_webhooks(hass, entry.options.get(CONF_WEBHOOK_ID))
        entry.runtime_data.webhook = hl_webhook

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: HLConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        if entry.runtime_data.webhook:
            hl_webhook = entry.runtime_data.webhook
            hl_webhook.unregister_webhooks(hass, entry.options.get(CONF_WEBHOOK_ID))
        if entry.runtime_data.mqtt:
            hl_mqtt = entry.runtime_data.mqtt
            await hl_mqtt.async_stop()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: HLConfigEntry) -> None:
    """Handle options update - only reload if the options have changed."""
    if entry.runtime_data.options != entry.options:
        await hass.config_entries.async_reload(entry.entry_id)


async def _async_start_mqtt(hass: HomeAssistant, entry: HLConfigEntry):
    hl_coordinator = entry.runtime_data.coordinator
    if entry.options.get(CONF_MQTT_HOMELINK):
        hl_mqtt = HomeLINKMQTT(
            hass,
            entry.options,
            hl_coordinator.data[COORD_PROPERTIES],
        )
    else:
        hl_mqtt = HAMQTT(
            hass,
            entry.options,
            hl_coordinator.data[COORD_PROPERTIES],
        )

    try:
        ret = await hl_mqtt.async_start()
        if ret:
            raise ConfigEntryNotReady(
                "HomeLink MQTT credentials/topic are invalid. Please reconfigure"
            )
        return hl_mqtt  # noqa: TRY300

    except ConnectionRefusedError as err:
        raise ConfigEntryNotReady("HomeLink MQTT server not available") from err
