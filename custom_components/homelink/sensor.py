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
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    ATTR_LASTTESTDATE,
    ATTR_REPLACEDATE,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    DOMAIN,
    ENTITY_NAME_LASTTESTDATE,
    ENTITY_NAME_REPLACEDATE,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    MODELTYPE_GATEWAY,
)
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


@dataclass
class HomeLINKEntityDescription(
    SensorEntityDescription, HomeLINKEntityDescriptionMixin
):
    """Describes HomeLINK sensor entity."""


SENSOR_TYPES: tuple[HomeLINKEntityDescription, ...] = (
    HomeLINKEntityDescription(
        key=ATTR_REPLACEDATE,
        name=ENTITY_NAME_REPLACEDATE,
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_date(data.replacedate),
    ),
    HomeLINKEntityDescription(
        key=ATTR_LASTTESTDATE,
        name=ENTITY_NAME_LASTTESTDATE,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: _parse_timestamp(data.status.lasttesteddate),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_sensor_property(hl_property):
        for device in hl_coordinator.data[COORD_PROPERTIES][hl_property][COORD_DEVICES]:
            async_add_sensor_device(hl_property, device)

    @callback
    def async_add_sensor_device(hl_property, device):
        if (
            hl_coordinator.data[COORD_PROPERTIES][hl_property][COORD_DEVICES][
                device
            ].modeltype
            != MODELTYPE_GATEWAY
        ):
            async_add_entities(
                [
                    HomeLINKSensor(hl_coordinator, hl_property, device, description)
                    for description in SENSOR_TYPES
                ]
            )
        else:
            async_add_entities(
                [HomeLINKSensor(hl_coordinator, hl_property, device, SENSOR_TYPES[0])]
            )

    for hl_property in hl_coordinator.data[COORD_PROPERTIES]:
        async_add_sensor_property(hl_property)

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_PROPERTY, async_add_sensor_property)
    )

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_DEVICE, async_add_sensor_device)
    )


class HomeLINKSensor(HomeLINKEntity, SensorEntity):
    """Sensor entity object for HomeLINK sensor."""

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
        self._update_properties()

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._update_properties()
        self.async_write_ha_state()

    def _update_properties(self):
        self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        self._gateway_key = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_GATEWAY_KEY
        ]
