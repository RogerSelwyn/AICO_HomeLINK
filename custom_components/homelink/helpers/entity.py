"""HomeLINK entity."""

from homeassistant.components.event import EventEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    ATTR_ACTIONTIMESTAMP,
    ATTR_ID,
    ATTR_MODEL,
    ATTR_MODELTYPE,
    ATTR_SEVERITY,
    ATTR_SOURCE,
    ATTRIBUTION,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    DOMAIN,
    HOMELINK_MESSAGE_EVENT,
    MQTT_EVENTTYPEID,
    MQTT_SEVERITY,
    MQTT_SOURCEID,
    MQTT_SOURCEMODEL,
    MQTT_SOURCEMODELTYPE,
)
from .coordinator import HomeLINKDataCoordinator
from .utils import (
    build_device_identifiers,
    device_device_info,
    get_message_date,
    property_device_info,
)


class HomeLINKPropertyEntity(CoordinatorEntity[HomeLINKDataCoordinator]):
    """HomeLINK Property Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: HomeLINKDataCoordinator, hl_property_key) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)
        self._key = hl_property_key
        self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
        self._gateway_key = self._property[COORD_GATEWAY_KEY]
        self._update_attributes()

    @property
    def device_info(self):
        """Entity device information."""
        return property_device_info(self._key)

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
        self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        self._gateway_key = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_GATEWAY_KEY
        ]
        self._identifiers = build_device_identifiers(device_key)
        self._update_attributes()

    @property
    def device_info(self):
        """Entity device information."""
        return device_device_info(self._identifiers, self._parent_key, self._device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._update_attributes()
        self.async_write_ha_state()

    def _update_attributes(self):
        """Overloaded in sub entities."""


class HomeLINKEventEntity(EventEntity):
    """Event entity for HomeLINK ."""

    _attr_has_entity_name = True
    _attr_name = "Event"
    _attr_should_poll = False

    def __init__(self, entry, key, eventtypes, mqtt_key) -> None:
        """Property event entity object for HomeLINK sensor."""
        self._key = key
        self._attr_event_types = eventtypes
        self._entry = entry
        self._mqtt_key = mqtt_key
        self._unregister_event_handler = None

    @property
    def unique_id(self) -> str:
        """Return the unique_id of the event entity."""
        return f"{self._key}_event"

    async def async_added_to_hass(self) -> None:
        """Register Event handler."""
        event = HOMELINK_MESSAGE_EVENT.format(domain=DOMAIN, key=self._mqtt_key).lower()

        self._unregister_event_handler = async_dispatcher_connect(
            self.hass, event, self._handle_event
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister Evemt handler."""
        if self._unregister_event_handler:
            self._unregister_event_handler()

    @callback
    def _handle_event(self, event) -> None:
        """Handle status event for this resource."""
        self._trigger_event(
            event[MQTT_EVENTTYPEID],
            {
                ATTR_ACTIONTIMESTAMP: get_message_date(event),
                ATTR_SEVERITY: event[MQTT_SEVERITY],
                ATTR_SOURCE: {
                    ATTR_ID: event[MQTT_SOURCEID],
                    ATTR_MODEL: event[MQTT_SOURCEMODEL],
                    ATTR_MODELTYPE: event[MQTT_SOURCEMODELTYPE],
                },
            },
        )
        self.async_write_ha_state()
