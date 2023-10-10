"""HomeLINK entity."""

from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_VIA_DEVICE,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_HOMELINK,
    ATTR_PROPERTY,
    ATTRIBUTION,
    COORD_DEVICES,
    COORD_PROPERTIES,
    DASHBOARD_URL,
    DOMAIN,
)
from .coordinator import HomeLINKDataCoordinator
from .helpers.utils import build_device_identifiers


class HomeLINKPropertyEntity(CoordinatorEntity[HomeLINKDataCoordinator]):
    """HomeLINK Property Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: HomeLINKDataCoordinator, hl_property_key) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)
        self._key = hl_property_key
        self._gateway_key = None
        self._property = None
        self._update_attributes()

    @property
    def device_info(self):
        """Entity device information."""
        return {
            ATTR_IDENTIFIERS: {(DOMAIN, ATTR_PROPERTY, self._key)},
            ATTR_NAME: self._key,
            ATTR_MANUFACTURER: ATTR_HOMELINK,
            ATTR_MODEL: ATTR_PROPERTY.capitalize(),
            ATTR_CONFIGURATION_URL: DASHBOARD_URL,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._update_attributes()
        self.async_write_ha_state()

    def _update_attributes(self):
        """Overloaded in sub entities."""


class HomeLINKDeviceEntity(CoordinatorEntity[HomeLINKDataCoordinator]):
    """HomeLINK Device Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: HomeLINKDataCoordinator, hl_property_key, device_key
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        super().__init__(coordinator)
        self._parent_key = hl_property_key
        self._key = device_key
        self._gateway_key = None
        self._device = None
        self._update_attributes()

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
        self._update_attributes()
        self.async_write_ha_state()

    def _update_attributes(self):
        """Overloaded in sub entities."""
