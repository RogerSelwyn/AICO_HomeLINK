"""Support for HomeLINK sensors."""

import json
import logging

from dateutil import parser
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    ATTR_IDENTIFIERS,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt

from .const import (
    ALARMS_NONE,
    ATTR_ADDRESS,
    ATTR_ALARMED_DEVICES,
    ATTR_ALERTID,
    ATTR_ALERTS,
    ATTR_ALERTSTATUS,
    ATTR_CATEGORY,
    ATTR_CONNECTIVITYTYPE,
    ATTR_DATACOLLECTIONSTATUS,
    ATTR_DESCRIPTION,
    ATTR_DEVICE,
    ATTR_EVENTTYPE,
    ATTR_HOMELINK,
    ATTR_INSTALLATIONDATE,
    ATTR_INSTALLEDBY,
    ATTR_LASTSEENDATE,
    ATTR_LASTTESTDATE,
    ATTR_PROPERTY,
    ATTR_RAISEDDATE,
    ATTR_REFERENCE,
    ATTR_REPLACEDATE,
    ATTR_SERIALNUMBER,
    ATTR_SEVERITY,
    ATTR_SIGNALSTRENGTH,
    ATTR_TAGS,
    ATTR_TYPE,
    ATTRIBUTION,
    CONF_MQTT_ENABLE,
    CONF_MQTT_TOPIC,
    COORD_ALERTS,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    COORD_PROPERTY,
    DASHBOARD_URL,
    DOMAIN,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    HOMELINK_MQTT_MESSAGE,
    MODELTYPE_COALARM,
    MODELTYPE_FIREALARM,
    MODELTYPE_FIRECOALARM,
    MODELTYPE_GATEWAY,
    MODELTYPE_PROBLEMS,
    MQTT_ACTIONTIMESTAMP,
    MQTT_CLASSIFIER_ACTIVE,
    MQTT_DEVICESERIALNUMBER,
    MQTT_EVENTID,
    MQTT_EVENTTYPEID,
    STATUS_GOOD,
    STATUS_NOT_GOOD,
    UNKNOWN,
    HomeLINKMessageType,
)
from .coordinator import HomeLINKDataCoordinator
from .entity import HomeLINKEntity
from .helpers.events import raise_device_event, raise_property_event
from .helpers.utils import build_device_identifiers

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_property(hl_property):
        async_add_entities([HomeLINKProperty(hass, entry, hl_coordinator, hl_property)])
        for device in hl_coordinator.data[COORD_PROPERTIES][hl_property][COORD_DEVICES]:
            async_add_device(hl_property, device)

    @callback
    def async_add_device(hl_property, device):
        async_add_entities(
            [HomeLINKDevice(hass, entry, hl_coordinator, hl_property, device)]
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


class HomeLINKProperty(CoordinatorEntity[HomeLINKDataCoordinator], BinarySensorEntity):
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
        hl_property,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)

        self._key = hl_property
        self._gateway_key = None
        self._attr_unique_id = f"{self._key}"
        self._dev_reg = device_registry.async_get(hass)
        self._property = None
        self._alarms = []
        self._status = None
        self._alerts = None
        self._alert_status = {}
        self._update_attributes()
        self._startup = dt.utcnow()
        self._root_topic = entry.options.get(CONF_MQTT_TOPIC).removesuffix("#")
        if entry.options.get(CONF_MQTT_ENABLE):
            self._register_mqtt_handler(hass, entry)

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
        attributes = {
            ATTR_REFERENCE: hl_property.reference,
            ATTR_ADDRESS: hl_property.address,
            ATTR_LATITUDE: hl_property.latitude,
            ATTR_LONGITUDE: hl_property.longitude,
            ATTR_TAGS: hl_property.tags,
            ATTR_ALARMED_DEVICES: self._alarms,
        }
        if self._alerts:
            attributes[ATTR_ALERTS] = self._alerts

        return attributes

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
        if self._key in self.coordinator.data[COORD_PROPERTIES]:
            self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
            self._gateway_key = self._property[COORD_GATEWAY_KEY]
            self._alerts = self._set_alerts()
            self._status, self._alarms = self._set_status()

    def _set_status(self) -> bool:
        status = STATUS_GOOD
        if self._alerts:
            status = STATUS_NOT_GOOD
        alarms = []
        for devicekey in self._property[COORD_DEVICES]:
            device = self._property[COORD_DEVICES][devicekey]
            if device.status.operationalstatus != STATUS_GOOD:
                status = device.status.operationalstatus
                if devicereg := self._dev_reg.async_get_device(
                    build_device_identifiers(device.serialnumber)
                ):
                    alarms.append(devicereg.name_by_user or devicereg.name)
        return status != STATUS_GOOD, alarms or ALARMS_NONE

    def _set_alerts(self):
        return [
            {
                ATTR_ALERTID: alert.alertid,
                ATTR_ALERTSTATUS: self._alert_status.get(alert.alertid, UNKNOWN),
                ATTR_EVENTTYPE: alert.eventtype,
                ATTR_SEVERITY: alert.severity,
                ATTR_RAISEDDATE: alert.raiseddate,
                ATTR_CATEGORY: alert.category,
                ATTR_TYPE: alert.hl_type,
                ATTR_DESCRIPTION: alert.description,
            }
            for alert in self._get_alerts()
        ]

    def _get_alerts(self):
        return [
            alert
            for alert in self.coordinator.data[COORD_PROPERTIES][self._key][
                COORD_ALERTS
            ]
            if not hasattr(alert.rel, ATTR_DEVICE)
        ]

    def _register_mqtt_handler(self, hass, entry):
        event = HOMELINK_MQTT_MESSAGE.format(domain=DOMAIN, key=self._key).lower()
        entry.async_on_unload(
            async_dispatcher_connect(hass, event, self._async_message_received)
        )

    @callback
    async def _async_message_received(self, msg):
        payload = json.loads(msg.payload)
        msgdate = _get_message_date(payload)
        if msgdate < self._startup:
            return

        messagetype = _extract_message_type(self._root_topic, msg.topic)

        if self._gateway_key.lower() in msg.topic:
            serialnumber = payload[MQTT_DEVICESERIALNUMBER]
            event = HOMELINK_MQTT_MESSAGE.format(
                domain=DOMAIN, key=serialnumber
            ).lower()
            dispatcher_send(self.hass, event, msg, messagetype)
            return

        raise_property_event(self.hass, messagetype, msg.topic, payload)
        if messagetype in [
            HomeLINKMessageType.MESSAGE_DEVICE,
            HomeLINKMessageType.MESSAGE_PROPERTY,
        ]:
            await self.coordinator.async_refresh()
            return

        if messagetype in [
            HomeLINKMessageType.MESSAGE_ALERT,
        ]:
            self._process_alert(msg, payload)
            await self.coordinator.async_refresh()

        return

    def _process_alert(self, msg, payload):
        classifier = _extract_classifier(self._root_topic, msg.topic)
        eventid = payload[MQTT_EVENTID]
        if classifier == MQTT_CLASSIFIER_ACTIVE:
            self._alert_status[eventid] = payload[MQTT_EVENTTYPEID]
        else:
            self._alert_status.pop(eventid)


class HomeLINKDevice(HomeLINKEntity, BinarySensorEntity):
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
        hass: HomeAssistant,
        entry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        self._alert_status = {}
        self._alerts = None
        super().__init__(coordinator, hl_property_key, device_key)

        self._attr_unique_id = f"{self._parent_key}_{self._key}".rstrip()
        self._startup = dt.utcnow()
        self._root_topic = entry.options.get(CONF_MQTT_TOPIC)
        if entry.options.get(CONF_MQTT_ENABLE):
            self._register_mqtt_handler(hass, entry)

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
        modeltype = self._device.modeltype
        if modeltype in [MODELTYPE_FIRECOALARM, MODELTYPE_FIREALARM]:
            return BinarySensorDeviceClass.SMOKE
        if modeltype == MODELTYPE_COALARM:
            return BinarySensorDeviceClass.CO
        if modeltype in MODELTYPE_PROBLEMS:
            return BinarySensorDeviceClass.PROBLEM
        return None

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attributes = {
            ATTR_SERIALNUMBER: self._device.serialnumber,
            ATTR_INSTALLATIONDATE: self._device.installationdate,
            ATTR_INSTALLEDBY: self._device.installedby,
            ATTR_REPLACEDATE: self._device.replacedate,
            ATTR_SIGNALSTRENGTH: self._device.metadata.signalstrength,
            ATTR_LASTSEENDATE: self._device.metadata.lastseendate,
            ATTR_CONNECTIVITYTYPE: self._device.metadata.connectivitytype,
            ATTR_LASTTESTDATE: self._device.status.lasttesteddate,
            ATTR_DATACOLLECTIONSTATUS: self._device.status.datacollectionstatus,
        }
        if self._alerts:
            attributes[ATTR_ALERTS] = self._alerts

        return attributes

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
            self._alerts = self._set_alerts()
            self._status = self._set_status()

    def _set_status(self) -> bool:
        if self._device.status.operationalstatus == STATUS_GOOD:
            return False

        return bool(self._get_alerts())

    def _set_alerts(self):
        alerts = self._get_alerts()
        return [
            {
                ATTR_ALERTID: alert.alertid,
                ATTR_ALERTSTATUS: self._alert_status.get(alert.alertid, UNKNOWN),
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
                hasattr(alert.rel, ATTR_DEVICE)
                and self._device.rel.self == alert.rel.device
            )
        ]

    def _register_mqtt_handler(self, hass, entry):
        if self._device.modeltype == MODELTYPE_GATEWAY:
            key = self._key
        else:
            key = f"{self._gateway_key}-{self._key}"

        event = HOMELINK_MQTT_MESSAGE.format(domain=DOMAIN, key=key).lower()
        entry.async_on_unload(
            async_dispatcher_connect(hass, event, self._async_mqtt_handle)
        )

    @callback
    async def _async_mqtt_handle(self, msg, messagetype):
        payload = json.loads(msg.payload)

        raise_device_event(self.hass, self.device_info, messagetype, msg.topic, payload)
        if messagetype in [
            HomeLINKMessageType.MESSAGE_ALERT,
        ]:
            self._process_alert(msg, payload)
            await self.coordinator.async_refresh()

    def _process_alert(self, msg, payload):
        classifier = _extract_classifier(self._root_topic, msg.topic)
        eventid = payload[MQTT_EVENTID]
        if classifier == MQTT_CLASSIFIER_ACTIVE:
            self._alert_status[eventid] = payload[MQTT_EVENTTYPEID]
        else:
            self._alert_status.pop(eventid)


def _extract_message_type(root_topic, topic):
    messagetype = topic.removeprefix(f"{root_topic}/").split("/")[0]
    messagetypes = [item.value for item in HomeLINKMessageType]
    if messagetype in messagetypes:
        return messagetype

    return HomeLINKMessageType.MESSAGE_UNKNOWN


def _extract_classifier(root_topic, topic):
    return topic.removeprefix(f"{root_topic}/").split("/")[1]


def _get_message_date(payload):
    return parser.parse(payload[MQTT_ACTIONTIMESTAMP])
