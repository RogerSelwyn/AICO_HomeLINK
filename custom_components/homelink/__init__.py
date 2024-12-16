"""Initialise the HomeLINK integration."""

import logging

import aiohttp
from homeassistant.const import CONF_WEBHOOK_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import (
    aiohttp_client,
    config_entry_oauth2_flow,
    device_registry,
)

from pyhomelink.api import HomeLINKApi

from .const import (
    CONF_MQTT_ENABLE,
    CONF_MQTT_HOMELINK,
    CONF_WEBHOOK_ENABLE,
    COORD_PROPERTIES,
    DOMAIN,
)
from .helpers.api import AsyncConfigEntryAuth
from .helpers.config_data import HLConfigEntry, HLData
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.mqtt import HAMQTT, HomeLINKMQTT
from .helpers.webhook import HomeLINKWebhook

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.EVENT]


async def async_setup_entry(hass: HomeAssistant, entry: HLConfigEntry) -> bool:
    """Set up HomeLINK from a config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    # Retrieve OAUTH sesion and make sure token is valid.
    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    try:
        await session.async_ensure_token_valid()
    except aiohttp.client_exceptions.ClientResponseError as err:
        if err.status == 401:
            raise ConfigEntryAuthFailed from err
        raise
    except aiohttp.client_exceptions.ClientConnectorError as err:
        raise ConfigEntryNotReady from err

    # Initiate api connection
    hl_api = HomeLINKApi(
        AsyncConfigEntryAuth(aiohttp_client.async_get_clientsession(hass), session)
    )

    # Initiate co-ordinator
    hl_coordinator = HomeLINKDataCoordinator(hass, hl_api, entry)
    await hl_coordinator.async_config_entry_first_refresh()
    entry.runtime_data = HLData(hl_coordinator, entry.options, None, None)

    # Setup MQTT if required
    if entry.options.get(CONF_MQTT_ENABLE):
        hl_mqtt = await _async_start_mqtt(hass, entry)
        entry.runtime_data.mqtt = hl_mqtt

    #  Setup webhooks if required
    if entry.options.get(CONF_WEBHOOK_ENABLE):
        hl_webhook = HomeLINKWebhook(entry)
        hl_webhook.register_webhooks(hass, entry.options.get(CONF_WEBHOOK_ID))
        entry.runtime_data.webhook = hl_webhook

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: HLConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Unregister webhooks if one was set up
        if entry.runtime_data.webhook:
            hl_webhook = entry.runtime_data.webhook
            hl_webhook.unregister_webhooks(hass, entry.options.get(CONF_WEBHOOK_ID))

        # Disconenct MQTT if one was setup
        if entry.runtime_data.mqtt:
            hl_mqtt = entry.runtime_data.mqtt
            await hl_mqtt.async_stop()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: HLConfigEntry) -> None:
    """Handle options update - only reload if the options have changed."""
    if entry.runtime_data.options != entry.options:
        await hass.config_entries.async_reload(entry.entry_id)


async def _async_start_mqtt(
    hass: HomeAssistant, entry: HLConfigEntry
) -> HAMQTT | HomeLINKMQTT:
    hl_coordinator = entry.runtime_data.coordinator

    # Initiate connection to HomeLINK MQTT or HA MQTT as required
    hl_mqtt: HAMQTT | HomeLINKMQTT | None = None
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
        # Start the connection - both connections operate the same methods
        ret = await hl_mqtt.async_start()
        if ret:
            raise ConfigEntryNotReady(
                translation_domain=DOMAIN, translation_key="homelink_mqtt_invalid"
            )
        return hl_mqtt  # noqa: TRY300

    except ConnectionRefusedError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="homelink_mqtt_unavailable"
        ) from err


async def async_migrate_entry(hass: HomeAssistant, config_entry: HLConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version > 2:
        # This shouldn't happen since we are at v2
        return False

    if config_entry.version == 1:
        # Modify the incorrectly created device identifiers from v1
        new_data = {**config_entry.data}

        await _migrate_devices_identifiers(hass, config_entry)

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=0, version=2
        )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )

    return True


async def _migrate_devices_identifiers(
    hass: HomeAssistant, config_entry: HLConfigEntry
) -> None:
    # Original device identifiers were created with an extra (second) item in the tuple.
    # This removes it
    dev_reg = device_registry.async_get(hass)
    devices = device_registry.async_entries_for_config_entry(
        dev_reg, config_entry.entry_id
    )
    for device in devices:
        if len(list(device.identifiers)[0]) < 3:
            continue
        new_identifiers = {(DOMAIN, list(device.identifiers)[0][-1])}
        dev_reg.async_update_device(device.id, new_identifiers=new_identifiers)
