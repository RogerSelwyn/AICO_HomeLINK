"""Support for HomeLINK sensors."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from pyhomelink import HomeLINKReadingType

from .const import (
    ATTR_LASTTESTDATE,
    ATTR_READINGDATE,
    ATTR_READINGS,
    ATTR_REPLACEDATE,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    COORD_READINGS,
    DOMAIN,
    ENTITY_NAME_LASTTESTDATE,
    ENTITY_NAME_REPLACEDATE,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
)
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import HomeLINKDeviceEntity


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
        value_fn=lambda data: data.replacedate.date() or None,
    ),
    HomeLINKEntityDescription(
        key=ATTR_LASTTESTDATE,
        name=ENTITY_NAME_LASTTESTDATE,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.status.lasttesteddate,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_sensor_property(hl_property):
        for device_key, device in hl_coordinator.data[COORD_PROPERTIES][hl_property][
            COORD_DEVICES
        ].items():
            async_add_sensor_device(hl_property, device_key, device, None)

    @callback
    def async_add_sensor_device(
        hl_property, device_key, device, gateway_key
    ):  # pylint: disable=unused-argument
        async_add_entities(
            [
                HomeLINKSensor(hl_coordinator, hl_property, device_key, description)
                for description in SENSOR_TYPES
            ]
        )
        if hasattr(device.rel, ATTR_READINGS):
            for reading in hl_coordinator.data[COORD_PROPERTIES][hl_property][
                COORD_READINGS
            ]:
                for readingdevice in reading.devices:
                    if readingdevice.serialnumber == device_key:
                        _add_sensor_reading(reading, device_key)

    def _add_sensor_reading(reading, device_key):
        async_add_entities(
            [
                HomeLINKReadingSensor(
                    hl_coordinator, hl_property, device_key, reading.type
                )
            ]
        )

    for hl_property in hl_coordinator.data[COORD_PROPERTIES]:
        async_add_sensor_property(hl_property)

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_PROPERTY, async_add_sensor_property)
    )

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_DEVICE, async_add_sensor_device)
    )


class HomeLINKSensor(HomeLINKDeviceEntity, SensorEntity):
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

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._device)

    def _update_attributes(self):
        if (
            self._parent_key in self.coordinator.data[COORD_PROPERTIES]
            and self._key
            in self.coordinator.data[COORD_PROPERTIES][self._parent_key][COORD_DEVICES]
        ):
            self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_DEVICES
            ][self._key]
            self._gateway_key = self.coordinator.data[COORD_PROPERTIES][
                self._parent_key
            ][COORD_GATEWAY_KEY]


class HomeLINKReadingSensor(HomeLINKDeviceEntity, SensorEntity):
    """Reading sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_state_class = STATE_CLASS_MEASUREMENT

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
        readingtype,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        self._readingtype = readingtype
        self._state = None
        self._readingdate = None
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} {readingtype}"
        if readingtype == HomeLINKReadingType.CO2:
            self._attr_device_class = SensorDeviceClass.CO2
            self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
        elif readingtype == HomeLINKReadingType.HUMIDITY:
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif readingtype == HomeLINKReadingType.TEMPERATURE:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> Any:
        return self._state

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {ATTR_READINGDATE: self._readingdate}

    def _update_attributes(self):
        if (
            self._parent_key in self.coordinator.data[COORD_PROPERTIES]
            and self._key
            in self.coordinator.data[COORD_PROPERTIES][self._parent_key][COORD_DEVICES]
        ):
            for reading in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_READINGS
            ]:
                if reading.type != self._readingtype:
                    continue
                for device in reading.devices:
                    if device.serialnumber != self._key:
                        continue
                    self._state = device.values[len(device.values) - 1].value
                    self._readingdate = device.values[
                        len(device.values) - 1
                    ].readingdate
                    break
