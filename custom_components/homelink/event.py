"""Support for HomeLINK events."""


from homeassistant.components.event import (
    EventEntity,
)  # EventDeviceClass,; EventEntityDescription,
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MQTT_ENABLE,
    COORD_DEVICES,
    COORD_LOOKUP_EVENTTYPE,
    COORD_PROPERTIES,
    DOMAIN,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    HOMELINK_MESSAGE_EVENT,
    MODELTYPE_GATEWAY,
)
from .coordinator import HomeLINKDataCoordinator
from .entity import HomeLINKDeviceEntity, HomeLINKPropertyEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    if entry.options.get(CONF_MQTT_ENABLE):
        hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]

        @callback
        def async_add_property(hl_property):
            async_add_entities(
                [HomeLINKPropertyEvent(entry, hl_coordinator, hl_property)]
            )
            for device in hl_coordinator.data[COORD_PROPERTIES][hl_property][
                COORD_DEVICES
            ]:
                async_add_device(hl_property, device)

        @callback
        def async_add_device(hl_property, device):
            async_add_entities(
                [HomeLINKDeviceEvent(entry, hl_coordinator, hl_property, device)]
            )

        for hl_property in hl_coordinator.data[COORD_PROPERTIES]:
            async_add_property(hl_property)

        entry.async_on_unload(
            async_dispatcher_connect(hass, HOMELINK_ADD_PROPERTY, async_add_property)
        )
        entry.async_on_unload(
            async_dispatcher_connect(
                hass,
                HOMELINK_ADD_DEVICE,
                async_add_device,
            )
        )


class HomeLINKPropertyEvent(HomeLINKPropertyEntity, EventEntity):
    """Event entity for HomeLINK Property."""

    _attr_has_entity_name = True
    _attr_name = "event"
    _attr_should_poll = False

    def __init__(
        self,
        entry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
    ) -> None:
        """Property event entity object for HomeLINK sensor."""
        super().__init__(coordinator, hl_property_key)
        self._attr_event_types = coordinator.data[COORD_LOOKUP_EVENTTYPE]
        self._entry = entry
        self._unregister_event_handler = None

    @property
    def unique_id(self) -> str:
        """Return the unique_id of the event entity."""
        return f"{self._key}_event"

    async def async_added_to_hass(self) -> None:
        """Register Event handler."""
        event = HOMELINK_MESSAGE_EVENT.format(domain=DOMAIN, key=self._key).lower()

        self._unregister_event_handler = async_dispatcher_connect(
            self.hass, event, self._handle_event
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister Evemt handler."""
        if self._unregister_event_handler:
            self._unregister_event_handler()

    @callback
    def _handle_event(self, event) -> None:
        """Handle status event for this resource (or it's parent)."""
        self._trigger_event(event["eventTypeId"])
        self.async_write_ha_state()


class HomeLINKDeviceEvent(HomeLINKDeviceEntity, EventEntity):
    """Event entity for HomeLINK Device."""

    _attr_has_entity_name = True
    _attr_name = "event"
    _attr_should_poll = False

    def __init__(
        self, entry, coordinator: HomeLINKDataCoordinator, hl_property_key, device_key
    ) -> None:
        """Device event entity object for HomeLINK sensor."""
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_event_types = coordinator.data[COORD_LOOKUP_EVENTTYPE]
        self._entry = entry
        self._unregister_event_handler = None
        self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]

    @property
    def unique_id(self) -> str:
        """Return the unique_id of the event entity."""
        return f"{self._key}_event"

    async def async_added_to_hass(self) -> None:
        """Register Event handler."""
        if self._device.modeltype == MODELTYPE_GATEWAY:
            key = self._key
        else:
            key = f"{self._gateway_key}-{self._key}"

        event = HOMELINK_MESSAGE_EVENT.format(domain=DOMAIN, key=key).lower()
        self._unregister_event_handler = async_dispatcher_connect(
            self.hass, event, self._handle_event
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister Event handler."""
        if self._unregister_event_handler:
            self._unregister_event_handler()

    @callback
    def _handle_event(self, event) -> None:
        """Handle status event for this resource (or it's parent)."""
        self._trigger_event(event["eventTypeId"])
        self.async_write_ha_state()
