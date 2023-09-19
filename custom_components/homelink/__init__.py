"""Initialise the HomeLINK integration."""
import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow

from pyhomelink.api import HomeLINKApi

from .api import AsyncConfigEntryAuth
from .const import DOMAIN
from .coordinator import HomeLINKDataCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


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

    hl_coordinator = HomeLINKDataCoordinator(hass, hl_api)
    await hl_coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hl_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
