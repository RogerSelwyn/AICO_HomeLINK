"""Initialise the HomeLINK integration."""

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow

from pyhomelink.api import HomeLINKApi

from .api import AsyncConfigEntryAuth
from .const import (
    CONF_MQTT_ENABLE,
    CONF_MQTT_HOMELINK,
    COORD_DATA_MQTT,
    COORD_PROPERTIES,
    DOMAIN,
)
from .coordinator import HomeLINKDataCoordinator
from .helpers.mqtt import HAMQTT, HomeLINKMQTT

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.EVENT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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

    hl_coordinator = HomeLINKDataCoordinator(hass, hl_api, entry)
    await hl_coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hl_coordinator

    if entry.options.get(CONF_MQTT_ENABLE):
        hl_mqtt = await _async_start_mqtt(hass, entry, hl_coordinator)
        hass.data[DOMAIN][entry.entry_id].data[COORD_DATA_MQTT] = hl_mqtt

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        if hass.data[DOMAIN][entry.entry_id].data[COORD_DATA_MQTT]:
            hl_mqtt = hass.data[DOMAIN][entry.entry_id].data[COORD_DATA_MQTT]
            await hl_mqtt.async_stop()
            hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def _async_start_mqtt(hass: HomeAssistant, entry: ConfigEntry, hl_coordinator):
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
        return hl_mqtt

    except ConnectionRefusedError as err:
        raise ConfigEntryNotReady("HomeLink MQTT server not available") from err
