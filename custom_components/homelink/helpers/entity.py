"""HomeLINK entity."""

from abc import abstractmethod
from collections.abc import Callable

from homeassistant.components.event import EventEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from ..const import (
    ATTR_ACTIONTIMESTAMP,
    ATTR_CATEGORY,
    ATTR_ID,
    ATTR_MODEL,
    ATTR_MODELTYPE,
    ATTR_SEVERITY,
    ATTR_SOURCE,
    ATTR_STATUSID,
    ATTRIBUTION,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    DOMAIN,
    HOMELINK_MESSAGE_EVENT,
    MQTT_CATEGORY,
    MQTT_EVENTTYPEID,
    MQTT_SEVERITY,
    MQTT_SOURCEID,
    MQTT_SOURCEMODEL,
    MQTT_SOURCEMODELTYPE,
    MQTT_STATUSID,
)
from .config_data import HLConfigEntry
from .coordinator import HomeLINKDataCoordinator
from .utils import (
    alarm_device_info,
    build_device_identifiers,
    device_device_info,
    get_message_date,
)


# Supports binary_sensor and sensor for Alarm type entity
class HomeLINKAlarmEntity(CoordinatorEntity[HomeLINKDataCoordinator]):
    """HomeLINK Property Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        alarm_type: str,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)
        self._key = hl_property_key
        self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
        self._gateway_key = self._property[COORD_GATEWAY_KEY]
        self._alarm_type = alarm_type
        self._update_attributes()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._is_data_in_coordinator()

    @property
    def device_info(self) -> DeviceInfo:
        """Entity device information."""
        return alarm_device_info(self._key, self._alarm_type)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._update_attributes()
        self.async_write_ha_state()

    @abstractmethod
    def _update_attributes(self) -> None:
        """Overloaded in sub entities."""

    @abstractmethod
    def _is_data_in_coordinator(self) -> bool:
        """Overloaded in sub entities."""


# Supports binary_sensor and sensor for Device type entity
class HomeLINKDeviceEntity(CoordinatorEntity[HomeLINKDataCoordinator]):
    """HomeLINK Device Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        device_key: str,
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
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._is_data_in_coordinator()

    @property
    def device_info(self) -> DeviceInfo:
        """Entity device information."""
        return device_device_info(self._identifiers, self._parent_key, self._device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._update_attributes()
        self.async_write_ha_state()

    @abstractmethod
    def _update_attributes(self) -> None:
        """Overloaded in sub entities."""

    @abstractmethod
    def _is_data_in_coordinator(self) -> bool:
        """Overloaded in sub entities."""


# Supports event for Property and Device type entity
class HomeLINKEventEntity(EventEntity):
    """Event entity for HomeLINK ."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self, entry: HLConfigEntry, key: str, eventtypes: list[str], mqtt_key: str
    ) -> None:
        """Property event entity object for HomeLINK sensor."""
        self._key = key
        self._attr_event_types = eventtypes
        self._entry = entry
        self._mqtt_key = mqtt_key
        self._unregister_event_handler: Callable[[], None] | None = None
        self._lastdate = dt_util.utcnow()

    @property
    def name(self) -> None:
        """Return the name of the sensor as device name."""
        return None

    @property
    def unique_id(self) -> str:
        """Return the unique_id of the event entity."""
        return f"{self._key}"

    async def async_added_to_hass(self) -> None:
        """Register Event handler."""
        event = HOMELINK_MESSAGE_EVENT.format(domain=DOMAIN, key=self._mqtt_key).lower()

        self._unregister_event_handler = async_dispatcher_connect(
            self.hass, event, self._handle_event
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister Event handler."""
        if self._unregister_event_handler:
            self._unregister_event_handler()

    @callback
    def _handle_event(self, event: dict) -> None:
        """Handle status event for this resource."""
        msgdate = get_message_date(event)
        if msgdate < self._lastdate:
            return
        self._lastdate = msgdate

        self._trigger_event(
            event[MQTT_EVENTTYPEID],
            {
                ATTR_ACTIONTIMESTAMP: msgdate,
                ATTR_STATUSID: event[MQTT_STATUSID],
                ATTR_CATEGORY: event[MQTT_CATEGORY],
                ATTR_SEVERITY: event[MQTT_SEVERITY],
                ATTR_SOURCE: {
                    ATTR_ID: event[MQTT_SOURCEID],
                    ATTR_MODEL: event[MQTT_SOURCEMODEL],
                    ATTR_MODELTYPE: event[MQTT_SOURCEMODELTYPE],
                },
            },
        )
        self.async_write_ha_state()
