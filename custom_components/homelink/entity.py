"""HomeLINK entity."""

from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_VIA_DEVICE,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DEVICE,
    ATTR_PROPERTY,
    ATTRIBUTION,
    COORD_DEVICES,
    COORD_PROPERTIES,
    DOMAIN,
)
from .coordinator import HomeLINKDataCoordinator


class HomeLINKEntity(CoordinatorEntity[HomeLINKDataCoordinator]):
    """HomeLINK Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: HomeLINKDataCoordinator, hl_property_key, device_key
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        super().__init__(coordinator)
        self._parent_key = hl_property_key
        self._key = device_key
        self._device = coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]

    @property
    def device_info(self):
        """Entity device information."""
        device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        return {
            ATTR_IDENTIFIERS: build_device_identifiers(self._key),
            ATTR_NAME: f"{self._parent_key} {self._device.location} {self._device.modeltype}",
            ATTR_VIA_DEVICE: (DOMAIN, ATTR_PROPERTY, self._parent_key),
            ATTR_MANUFACTURER: device.manufacturer,
            ATTR_MODEL: f"{device.model} ({device.modeltype})",
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        self.async_write_ha_state()


def build_device_identifiers(device_id):
    """Build device identifiers"""
    return {(DOMAIN, ATTR_DEVICE, device_id.upper())}
