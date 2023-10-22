"""Support for HomeLINK events."""


from homeassistant.components.event import DOMAIN as EVENT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_EVENT_ENABLE,
    CONF_MQTT_ENABLE,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_LOOKUP_EVENTTYPE,
    COORD_PROPERTIES,
    DOMAIN,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
)
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import HomeLINKEventEntity
from .helpers.utils import (
    build_device_identifiers,
    build_mqtt_device_key,
    device_device_info,
    property_device_info,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    if entry.options.get(CONF_MQTT_ENABLE) and entry.options.get(CONF_EVENT_ENABLE):
        await _async_create_entities(hass, entry, async_add_entities)
    else:
        await _async_delete_entities(hass, entry)


async def _async_create_entities(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    eventtypes = hl_coordinator.data[COORD_LOOKUP_EVENTTYPE]

    @callback
    def async_add_property(hl_property):
        async_add_entities([HomeLINKPropertyEvent(entry, hl_property, eventtypes)])
        gateway_key = hl_coordinator.data[COORD_PROPERTIES][hl_property][
            COORD_GATEWAY_KEY
        ]

        for device_key, device in hl_coordinator.data[COORD_PROPERTIES][hl_property][
            COORD_DEVICES
        ].items():
            async_add_device(hl_property, device_key, device, gateway_key, eventtypes)

    @callback
    def async_add_device(hl_property, device_key, device, gateway_key, eventtypes):
        async_add_entities(
            [
                HomeLINKDeviceEvent(
                    entry, hl_property, device_key, device, gateway_key, eventtypes
                )
            ]
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


async def _async_delete_entities(hass, entry):
    ent_reg = entity_registry.async_get(hass)
    entities = entity_registry.async_entries_for_config_entry(ent_reg, entry.entry_id)
    for entity in entities:
        if entity.domain == EVENT_DOMAIN:
            ent_reg.async_remove(entity.entity_id)


class HomeLINKPropertyEvent(HomeLINKEventEntity):
    """Event entity for HomeLINK Property."""

    def __init__(self, entry, hl_property_key, eventtypes) -> None:
        """Property event entity object for HomeLINK sensor."""
        super().__init__(entry, hl_property_key, eventtypes, hl_property_key)

    @property
    def device_info(self):
        """Entity device information."""
        return property_device_info(self._key)


class HomeLINKDeviceEvent(HomeLINKEventEntity):
    """Event entity for HomeLINK Device."""

    def __init__(
        self, entry, hl_property_key, device_key, device, gateway_key, eventtypes
    ) -> None:
        """Device event entity object for HomeLINK sensor."""
        mqtt_key = build_mqtt_device_key(device, device_key, gateway_key)
        super().__init__(entry, device_key, eventtypes, mqtt_key)
        self._parent_key = hl_property_key
        self._device = device
        self._identifiers = build_device_identifiers(device_key)

    @property
    def device_info(self):
        """Entity device information."""
        return device_device_info(self._identifiers, self._parent_key, self._device)
