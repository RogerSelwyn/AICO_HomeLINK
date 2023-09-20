"""Support for HomeLINK sensors."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from dateutil import parser
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import HomeLINKDataCoordinator
from .entity import HomeLINKEntity


def _parse_timestamp(passeddate):
    return parser.parse(passeddate) if passeddate else None


def _parse_date(passeddate):
    return _parse_timestamp(passeddate).date() if passeddate else None


@dataclass
class HomeLINKEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], StateType]
    # extra_state_attributes_fn: Callable[[Any], dict[str, str]] | None


@dataclass
class HomeLINKEntityDescription(
    SensorEntityDescription, HomeLINKEntityDescriptionMixin
):
    """Describes HomeLINK sensor entity."""


SENSOR_TYPES: tuple[HomeLINKEntityDescription, ...] = (
    HomeLINKEntityDescription(
        key="lasttesteddate",
        name="Last Tested Date",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: _parse_timestamp(data.status.lasttesteddate),
    ),
    HomeLINKEntityDescription(
        key="replacedate",
        name="Replace By Date",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_date(data.replacedate),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    hl_entities = []
    for hl_property in hl_coordinator.data["properties"]:
        for device in hl_coordinator.data["properties"][hl_property]["devices"]:
            if (
                hl_coordinator.data["properties"][hl_property]["devices"][
                    device
                ].modeltype
                != "GATEWAY"
            ):
                hl_entities.extend(
                    HomeLINKSensor(hl_coordinator, hl_property, device, description)
                    for description in SENSOR_TYPES
                )

    async_add_entities(hl_entities, False)


class HomeLINKSensor(HomeLINKEntity, SensorEntity):
    """Device entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    entity_description: HomeLINKEntityDescription

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
        description: HomeLINKEntityDescription,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} {description.key}"
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._device)
