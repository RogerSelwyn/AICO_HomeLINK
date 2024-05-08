"""Config data class."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from homeassistant.config_entries import ConfigEntry

from .coordinator import HomeLINKDataCoordinator
from .webhook import HomeLINKWebhook

HLConfigEntry = ConfigEntry["HLData"]


@dataclass
class HLData:
    """Data previously stored in hass.data."""

    coordinator: HomeLINKDataCoordinator
    mqtt: any
    webhook: HomeLINKWebhook
    options: MappingProxyType[str, Any]
