"""Diagnostics support for HomeLINK."""

from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant

from .helpers.configdata import HLConfigEntry

TO_REDACT = {CONF_ACCESS_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: HLConfigEntry,  # pylint: disable=unused-argument
) -> dict:
    """Return diagnostics for a config entry."""
    return {
        "config_entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "config_entry_options": dict(entry.options),
    }
