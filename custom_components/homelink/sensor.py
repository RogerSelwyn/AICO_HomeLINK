"""Support for HomeLINK sensors."""
from datetime import datetime

from dateutil import parser
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HomeLINKDataCoordinator
from .entity import HomeLINKEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Electric Kiwi Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    hl_entities = []
    for hl_property in hl_coordinator.data["properties"]:
        hl_entities.extend(
            HomeLINKLastTestSensorEntity(hl_coordinator, hl_property, device)
            for device in hl_coordinator.data["properties"][hl_property]["devices"]
            if (
                hl_coordinator.data["properties"][hl_property]["devices"][
                    device
                ].modeltype
                != "GATEWAY"
            )
        )
    async_add_entities(hl_entities)


class HomeLINKLastTestSensorEntity(HomeLINKEntity, SensorEntity):
    """Device entity object for HomeLINK sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: HomeLINKDataCoordinator, hl_property_key, device_key
    ) -> None:
        """Device entity object for HomeLINKi sensor."""
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} lasttesteddate"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Last Tested Date"

    @property
    def native_value(self) -> datetime:
        lasttesteddate = self._device.status.lasttesteddate

        return parser.parse(lasttesteddate) if lasttesteddate else None

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device_class."""
        return SensorDeviceClass.TIMESTAMP
