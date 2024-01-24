"""Support for HomeLINK sensors."""

import json
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from .const import (
    ALARMS_NONE,
    ALARMTYPE_ALARM,
    ALARMTYPE_ENVIRONMENT,
    ATTR_ADDRESS,
    ATTR_ALARMED_DEVICES,
    ATTR_ALARMED_ROOMS,
    ATTR_ALERTID,
    ATTR_ALERTS,
    ATTR_CATEGORY,
    ATTR_CONNECTIVITYTYPE,
    ATTR_DATACOLLECTIONSTATUS,
    ATTR_DESCRIPTION,
    ATTR_DEVICE,
    ATTR_EVENTTYPE,
    ATTR_INSTALLATIONDATE,
    ATTR_INSTALLEDBY,
    ATTR_LASTSEENDATE,
    ATTR_LASTTESTDATE,
    ATTR_METADATA,
    ATTR_OPERATIONALSTATUS,
    ATTR_RAISEDDATE,
    ATTR_REFERENCE,
    ATTR_REPLACEDATE,
    ATTR_SERIALNUMBER,
    ATTR_SEVERITY,
    ATTR_SIGNALSTRENGTH,
    ATTR_STATUS,
    ATTR_TAGS,
    ATTR_TYPE,
    ATTRIBUTION,
    CATEGORY_INSIGHT,
    CONF_MQTT_ENABLE,
    CONF_MQTT_TOPIC,
    COORD_ALERTS,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    COORD_PROPERTY,
    DOMAIN,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    HOMELINK_MESSAGE_MQTT,
    MODELLIST_ALARMS,
    MODELLIST_ENVIRONMENT,
    MODELLIST_PROBLEMS,
    MODELTYPE_COALARM,
    STATUS_GOOD,
    STATUS_NOT_GOOD,
    HomeLINKMessageType,
)
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import (
    HomeLINKAlarmEntity,
    HomeLINKDeviceEntity,
    HomeLINKPropertyEntity,
)
from .helpers.events import raise_device_event, raise_property_event
from .helpers.utils import (
    build_device_identifiers,
    build_mqtt_device_key,
    get_message_date,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_property(hl_property):
        async_add_entities([HomeLINKProperty(hass, entry, hl_coordinator, hl_property)])
        async_add_entities(
            [HomeLINKAlarm(hass, entry, hl_coordinator, hl_property, ALARMTYPE_ALARM)]
        )
        environment = False
        for device_key, device in hl_coordinator.data[COORD_PROPERTIES][hl_property][
            COORD_DEVICES
        ].items():
            async_add_device(hl_property, device_key, None, None)
            if device.modeltype in MODELLIST_ENVIRONMENT:
                environment = True

        if environment:
            async_add_entities(
                [
                    HomeLINKAlarm(
                        hass, entry, hl_coordinator, hl_property, ALARMTYPE_ENVIRONMENT
                    )
                ]
            )

    @callback
    def async_add_device(hl_property, device_key, device, gateway_key):  # pylint: disable=unused-argument
        async_add_entities(
            [HomeLINKDevice(entry, hl_coordinator, hl_property, device_key)]
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


class HomeLINKProperty(HomeLINKPropertyEntity, BinarySensorEntity):
    """Property entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _unrecorded_attributes = frozenset(
        (ATTR_REFERENCE, ATTR_ADDRESS, ATTR_LATITUDE, ATTR_LONGITUDE)
    )

    def __init__(
        self,
        hass: HomeAssistant,
        entry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
    ) -> None:
        """Property entity object for HomeLINK sensor."""

        self._status = None
        self._alarms = []
        self._dev_reg = device_registry.async_get(hass)
        super().__init__(coordinator, hl_property_key)
        self._entry = entry
        self._attr_unique_id = f"{self._key}"
        self._unregister_mqtt_handler = None
        if entry.options.get(CONF_MQTT_ENABLE):
            self._root_topic = entry.options.get(CONF_MQTT_TOPIC).removesuffix("#")

    @property
    def name(self) -> str:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        return self._status

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        return BinarySensorDeviceClass.SAFETY

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        hl_property = self._property[COORD_PROPERTY]
        return {
            ATTR_REFERENCE: hl_property.reference,
            ATTR_ADDRESS: hl_property.address,
            ATTR_LATITUDE: hl_property.latitude,
            ATTR_LONGITUDE: hl_property.longitude,
            ATTR_TAGS: hl_property.tags,
            ATTR_ALARMED_DEVICES: self._alarms,
        }

    def _update_attributes(self):
        if self._key in self.coordinator.data[COORD_PROPERTIES]:
            self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
            self._gateway_key = self._property[COORD_GATEWAY_KEY]
            self._status, self._alarms = self._set_status()

    def _set_status(self) -> bool:
        status = STATUS_GOOD
        alarms = []
        for alert in self.coordinator.data[COORD_PROPERTIES][self._key][COORD_ALERTS]:
            if alert.rel.hl_property == f"property/{self._key}" and hasattr(
                alert.rel, ATTR_DEVICE
            ):
                status = STATUS_NOT_GOOD
                if devicereg := self._dev_reg.async_get_device(
                    build_device_identifiers(alert.serialnumber)
                ):
                    alarms.append(devicereg.name_by_user or devicereg.name)

        return status != STATUS_GOOD, alarms or ALARMS_NONE


class HomeLINKAlarm(HomeLINKAlarmEntity, BinarySensorEntity):
    """Property entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _unrecorded_attributes = frozenset(
        (ATTR_REFERENCE, ATTR_ADDRESS, ATTR_LATITUDE, ATTR_LONGITUDE)
    )

    def __init__(
        self,
        hass: HomeAssistant,
        entry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        alarm_type,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        self._alerts = None
        self._status = None
        self._alarms_devices = []
        self._alarms_rooms = []
        self._dev_reg = device_registry.async_get(hass)
        super().__init__(coordinator, hl_property_key, alarm_type)
        self._entry = entry
        self._attr_unique_id = f"{self._key}_{alarm_type}"
        self._lastdate = dt.utcnow()
        self._unregister_mqtt_handler = None
        if entry.options.get(CONF_MQTT_ENABLE):
            self._root_topic = entry.options.get(CONF_MQTT_TOPIC).removesuffix("#")

    @property
    def name(self) -> str:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        return self._status

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        return BinarySensorDeviceClass.SAFETY

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attributes = {ATTR_ALARMED_DEVICES: self._alarms_devices}
        if self._alarm_type == ALARMTYPE_ENVIRONMENT:
            attributes[ATTR_ALARMED_ROOMS] = self._alarms_rooms
        if self._alerts:
            attributes[ATTR_ALERTS] = self._alerts

        return attributes

    async def async_added_to_hass(self) -> None:
        """Register MQTT handler."""
        await super().async_added_to_hass()
        if self._entry.options.get(CONF_MQTT_ENABLE):
            event = HOMELINK_MESSAGE_MQTT.format(
                domain=DOMAIN, key=f"{self._key}_{self._alarm_type}"
            ).lower()

            self._unregister_mqtt_handler = async_dispatcher_connect(
                self.hass, event, self._async_mqtt_handle
            )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister MQTT handler."""
        if self._unregister_mqtt_handler:
            self._unregister_mqtt_handler()

    def _update_attributes(self):
        if self._key in self.coordinator.data[COORD_PROPERTIES]:
            self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
            self._gateway_key = self._property[COORD_GATEWAY_KEY]
            self._alerts = self._set_alerts()
            self._status, self._alarms_devices, self._alarms_rooms = self._set_status()

    def _set_status(self) -> bool:
        status = STATUS_GOOD
        if self._alerts:
            status = STATUS_NOT_GOOD
        alarms_devices = []
        alarms_rooms = []
        for alert in self._get_alerts():
            status = STATUS_NOT_GOOD
            if not alert.serialnumber and not alert.location:
                continue
            if alert.serialnumber:
                if devicereg := self._dev_reg.async_get_device(
                    build_device_identifiers(alert.serialnumber)
                ):
                    device = devicereg.name_by_user or devicereg.name
                    if device not in alarms_devices:
                        alarms_devices.append(device)
            else:
                location = alert.locationnickname or alert.location
                if location not in alarms_rooms:
                    alarms_rooms.append(location)

        return (
            status != STATUS_GOOD,
            alarms_devices or ALARMS_NONE,
            alarms_rooms or ALARMS_NONE,
        )

    def _set_alerts(self):
        return [
            {
                ATTR_ALERTID: alert.alertid,
                ATTR_STATUS: alert.status,
                ATTR_EVENTTYPE: alert.eventtype,
                ATTR_SEVERITY: alert.severity,
                ATTR_RAISEDDATE: alert.raiseddate,
                ATTR_CATEGORY: alert.category,
                ATTR_TYPE: alert.hl_type,
                ATTR_DESCRIPTION: alert.description,
            }
            for alert in self._get_alerts()
            if not alert.location
        ]

    def _get_alerts(self):
        return [
            alert
            for alert in self.coordinator.data[COORD_PROPERTIES][self._key][
                COORD_ALERTS
            ]
            if (
                alert.category == CATEGORY_INSIGHT
                and self._alarm_type == ALARMTYPE_ENVIRONMENT
            )
            or (
                alert.category != CATEGORY_INSIGHT
                and alert.modeltype not in MODELLIST_ENVIRONMENT
                and self._alarm_type == ALARMTYPE_ALARM
            )
            or (
                alert.category != CATEGORY_INSIGHT
                and alert.modeltype in MODELLIST_ENVIRONMENT
                and self._alarm_type == ALARMTYPE_ENVIRONMENT
            )
        ]

    @callback
    async def _async_mqtt_handle(self, topic, payload, messagetype):
        msgdate = get_message_date(payload)
        if msgdate < self._lastdate:
            return
        self._lastdate = msgdate

        raise_property_event(self.hass, messagetype, topic, payload)

        if messagetype in [
            HomeLINKMessageType.MESSAGE_DEVICE,
            HomeLINKMessageType.MESSAGE_PROPERTY,
        ]:
            await self.coordinator.async_refresh()
            return

        if messagetype in [
            HomeLINKMessageType.MESSAGE_ALERT,
        ]:
            await self.coordinator.async_refresh()


class HomeLINKDevice(HomeLINKDeviceEntity, BinarySensorEntity):
    """Device entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _unrecorded_attributes = frozenset(
        (
            ATTR_INSTALLATIONDATE,
            ATTR_INSTALLEDBY,
            ATTR_REPLACEDATE,
            ATTR_CONNECTIVITYTYPE,
        )
    )

    def __init__(
        self,
        entry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        self._alerts = None
        super().__init__(coordinator, hl_property_key, device_key)
        self._entry = entry

        self._attr_unique_id = f"{self._parent_key}_{self._key}".rstrip()
        self._lastdate = dt.utcnow()
        self._unregister_mqtt_handler = None
        self._device_class = self._build_device_class()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        return self._status

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        return self._device_class

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attributes = {
            ATTR_SERIALNUMBER: self._device.serialnumber,
            ATTR_INSTALLATIONDATE: self._device.installationdate,
            ATTR_INSTALLEDBY: self._device.installedby,
            ATTR_REPLACEDATE: self._device.replacedate,
            ATTR_METADATA: {
                ATTR_SIGNALSTRENGTH: self._device.metadata.signalstrength,
                ATTR_LASTSEENDATE: self._device.metadata.lastseendate,
                ATTR_CONNECTIVITYTYPE: self._device.metadata.connectivitytype,
            },
            ATTR_STATUS: {
                ATTR_OPERATIONALSTATUS: self._device.status.operationalstatus,
                ATTR_LASTTESTDATE: self._device.status.lasttesteddate,
                ATTR_DATACOLLECTIONSTATUS: self._device.status.datacollectionstatus,
            },
        }
        if self._alerts:
            attributes[ATTR_ALERTS] = self._alerts

        return attributes

    async def async_added_to_hass(self) -> None:
        """Register MQTT handler."""
        await super().async_added_to_hass()
        if self._entry.options.get(CONF_MQTT_ENABLE):
            key = build_mqtt_device_key(self._device, self._key, self._gateway_key)

            event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=key).lower()
            self._unregister_mqtt_handler = async_dispatcher_connect(
                self.hass, event, self._async_mqtt_handle
            )
            if self._device.modeltype in MODELLIST_ENVIRONMENT:
                event = HOMELINK_MESSAGE_MQTT.format(
                    domain=DOMAIN, key=self._device.location
                ).lower()
                self._unregister_mqtt_handler = async_dispatcher_connect(
                    self.hass, event, self._async_mqtt_handle
                )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister MQTT handler."""
        if self._unregister_mqtt_handler:
            self._unregister_mqtt_handler()

    def _build_device_class(self):
        modeltype = self._device.modeltype
        if modeltype in MODELLIST_ALARMS:
            return BinarySensorDeviceClass.SMOKE
        if modeltype == MODELTYPE_COALARM:
            return BinarySensorDeviceClass.CO
        if modeltype in MODELLIST_PROBLEMS or modeltype in MODELLIST_ENVIRONMENT:
            return BinarySensorDeviceClass.PROBLEM
        return None

    def _update_attributes(self):
        if (
            self._parent_key not in self.coordinator.data[COORD_PROPERTIES]
            or self._key
            not in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_DEVICES
            ]
        ):
            return

        self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        self._gateway_key = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_GATEWAY_KEY
        ]
        self._alerts = self._set_alerts()
        self._status = self._set_status()

    def _set_status(self) -> bool:
        return bool(self._get_alerts())

    def _set_alerts(self):
        alerts = self._get_alerts()
        return [
            {
                ATTR_ALERTID: alert.alertid,
                ATTR_STATUS: alert.status,
                ATTR_EVENTTYPE: alert.eventtype,
                ATTR_SEVERITY: alert.severity,
                ATTR_RAISEDDATE: alert.raiseddate,
                ATTR_CATEGORY: alert.category,
                ATTR_TYPE: alert.hl_type,
                ATTR_DESCRIPTION: alert.description,
            }
            for alert in alerts
        ]

    def _get_alerts(self):
        return [
            alert
            for alert in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_ALERTS
            ]
            if (
                (
                    hasattr(alert.rel, ATTR_DEVICE)
                    and self._device.rel.self == alert.rel.device
                )
                or (
                    alert.location == self._device.location
                    and self._device.modeltype in MODELLIST_ENVIRONMENT
                    and not alert.serialnumber
                )
            )
        ]

    @callback
    async def _async_mqtt_handle(self, msg, topic, messagetype):
        payload = json.loads(msg.payload)
        msgdate = get_message_date(payload)
        if msgdate < self._lastdate and messagetype not in [
            HomeLINKMessageType.MESSAGE_READING,
        ]:
            return
        self._lastdate = msgdate

        raise_device_event(self.hass, self.device_info, messagetype, topic, payload)
        if messagetype in [
            HomeLINKMessageType.MESSAGE_READING,
        ]:
            self._process_reading(msg, topic, messagetype)
            return

        if messagetype in [
            HomeLINKMessageType.MESSAGE_ALERT,
        ]:
            await self.coordinator.async_refresh()

    def _process_reading(self, msg, topic, messagetype):
        readingtype = _extract_classifier(topic, 3)

        key = build_mqtt_device_key(
            self._device, f"{self._key}-{readingtype}", self._gateway_key
        )

        event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=key).lower()
        dispatcher_send(self.hass, event, msg, topic, messagetype, readingtype)


def _extract_classifier(topic, item):
    return topic.split("/")[item]
