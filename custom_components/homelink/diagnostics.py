"""Diagnostics support for HomeLINK."""
from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant

TO_REDACT = {CONF_ACCESS_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry  # pylint: disable=unused-argument
) -> dict:
    """Return diagnostics for a config entry."""
    return {
        "config_entry_data": async_redact_data(dict(config_entry.data), TO_REDACT),
        "config_entry_options": dict(config_entry.options),
    }
