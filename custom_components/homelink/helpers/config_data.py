"""Initialise the HomeLINK integration."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .coordinator import HomeLINKDataCoordinator
from .mqtt import HAMQTT, HomeLINKMQTT
from .webhook import HomeLINKWebhook

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.EVENT]

HLConfigEntry = ConfigEntry["HLData"]


@dataclass
class HLData:
    """Data previously stored in hass.data."""

    coordinator: HomeLINKDataCoordinator
    options: MappingProxyType[str, Any]
    mqtt: HAMQTT | HomeLINKMQTT | None
    webhook: HomeLINKWebhook | None
