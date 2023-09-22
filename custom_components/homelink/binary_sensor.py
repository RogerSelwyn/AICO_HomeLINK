"""Support for HomeLINK sensors."""
import json
import logging

from dateutil import parser
from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.setup import async_when_setup
from homeassistant.util import dt

from .const import (
    ATTR_ADDRESS,
    ATTR_CATEGORY,
    ATTR_CONNECTIVITYTYPE,
    ATTR_DATACOLLECTIONSTATUS,
    ATTR_DESCRIPTION,
    ATTR_DEVICE,
    ATTR_DEVICE_INFO,
    ATTR_EVENTTYPE,
    ATTR_HOMELINK,
    ATTR_INSTALLATIONDATE,
    ATTR_INSTALLEDBY,
    ATTR_LASTSEENDATE,
    ATTR_LASTTESTDATE,
    ATTR_PAYLOAD,
    ATTR_PROPERTY,
    ATTR_RAISEDDATE,
    ATTR_REFERENCE,
    ATTR_REPLACEDATE,
    ATTR_SEVERITY,
    ATTR_SIGNALSTRENGTH,
    ATTR_SUB_TYPE,
    ATTR_TAGS,
    ATTR_TYPE,
    ATTRIBUTION,
    CONF_MQTT_ENABLE,
    CONF_MQTT_TOPIC,
    COORD_ALERTS,
    COORD_DEVICES,
    COORD_PROPERTIES,
    COORD_PROPERTY,
    DASHBOARD_URL,
    DOMAIN,
    EVENTTYPE_CO_ALARM,
    EVENTTYPE_FIRE_ALARM,
    EVENTTYPE_FIRECO_ALARMS,
    MODELTYPE_COALARM,
    MODELTYPE_FIREALARM,
    MODELTYPE_FIRECOALARM,
    MODELTYPE_PROBLEMS,
    STATUS_GOOD,
    SUBSCRIBE_DEVICE_EVENT_TOPIC,
    SUBSCRIBE_DEVICE_FULL_TOPIC,
    SUBSCRIBE_DEVICE_OTHER_TOPIC,
    SUBSCRIBE_PROPERTY_DEVICE_TOPIC,
    SUBSCRIBE_PROPERTY_FULL_TOPIC,
    SUBSCRIBE_PROPERTY_PROPERTY_TOPIC,
    HomeLINKMessageType,
)
from .coordinator import HomeLINKDataCoordinator
from .entity import HomeLINKEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    hl_entities = []
    for hl_property in hl_coordinator.data[COORD_PROPERTIES]:
        hl_entities.append(
            HomeLINKProperty(hass, entry.options, hl_coordinator, hl_property)
        )
        for device in hl_coordinator.data[COORD_PROPERTIES][hl_property][COORD_DEVICES]:
            if (
                hl_coordinator.data[COORD_PROPERTIES][hl_property][COORD_DEVICES][
                    device
                ].modeltype
                == MODELTYPE_FIRECOALARM
            ):
                hl_entities.extend(
                    (
                        HomeLINKDevice(
                            hass,
                            entry.options,
                            hl_coordinator,
                            hl_property,
                            device,
                            MODELTYPE_FIREALARM,
                        ),
                        HomeLINKDevice(
                            hass,
                            entry.options,
                            hl_coordinator,
                            hl_property,
                            device,
                            MODELTYPE_COALARM,
                        ),
                    )
                )
            else:
                hl_entities.append(
                    HomeLINKDevice(
                        hass, entry.options, hl_coordinator, hl_property, device
                    )
                )
    async_add_entities(hl_entities)


class HomeLINKProperty(CoordinatorEntity[HomeLINKDataCoordinator], BinarySensorEntity):
    """Property entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        hass: HomeAssistant,
        config_options,
        coordinator: HomeLINKDataCoordinator,
        hl_property,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)

        self._key = hl_property
        self._attr_unique_id = f"{self._key}"
        self._property = coordinator.data[COORD_PROPERTIES][self._key]
        self._startup = dt.utcnow()
        self._config_options = config_options
        self._root_topic = _set_root_topic(config_options)
        if self._config_options.get(CONF_MQTT_ENABLE):
            async_when_setup(hass, MQTT_DOMAIN, self._async_subscribe)

    @property
    def name(self) -> str:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        status = STATUS_GOOD
        for devicekey in self._property[COORD_DEVICES]:
            device = self._property[COORD_DEVICES][devicekey]
            if device.status.operationalstatus != STATUS_GOOD:
                status = device.status.operationalstatus
        return status != STATUS_GOOD

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
        }

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
        self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
        self.async_write_ha_state()

    async def _async_subscribe(
        self, hass: HomeAssistant, component  # pylint: disable=unused-argument
    ):
        await self._async_subscribe_topic(hass, SUBSCRIBE_PROPERTY_PROPERTY_TOPIC)
        await self._async_subscribe_topic(hass, SUBSCRIBE_PROPERTY_DEVICE_TOPIC)

    async def _async_subscribe_topic(self, hass, topic):
        sub_topic = SUBSCRIBE_PROPERTY_FULL_TOPIC.format(
            root_topic=self._root_topic, topic=topic, key=self._key.lower()
        )
        await mqtt.async_subscribe(hass, sub_topic, self._async_message_received)

    @callback
    async def _async_message_received(self, msg):
        payload = json.loads(msg.payload)
        msgdate = parser.parse(payload[ATTR_RAISEDDATE])
        if msgdate >= self._startup:
            payload = json.loads(msg.payload)
            eventtype = _extract_event_type(self._root_topic, msg.topic)
            self._raise_event(eventtype, payload)

    def _raise_event(self, event_type, payload):
        self.hass.bus.fire(
            f"{DOMAIN}_{event_type}",
            {ATTR_SUB_TYPE: ATTR_PROPERTY, ATTR_PAYLOAD: payload},
        )
        _LOGGER.debug("%s_%s - %s", DOMAIN, event_type, payload)


class HomeLINKDevice(HomeLINKEntity, BinarySensorEntity):
    """Device entity object for HomeLINK sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        config_options,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
        sub_type=None,
    ) -> None:
        """Device entity object for HomeLINKi sensor."""
        super().__init__(coordinator, hl_property_key, device_key)

        self._attr_unique_id = f"{self._parent_key}_{self._key} {sub_type}".rstrip()
        self._sub_type = sub_type
        self._config_options = config_options
        self._startup = dt.utcnow()
        self._root_topic = _set_root_topic(config_options)
        if self._config_options.get(CONF_MQTT_ENABLE):
            async_when_setup(hass, MQTT_DOMAIN, self._async_subscribe)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._sub_type}" if self._sub_type else None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        if self._device.status.operationalstatus == STATUS_GOOD:
            return False

        return bool(self._get_alerts())

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        modeltype = self._sub_type or self._device.modeltype
        if modeltype == MODELTYPE_FIREALARM:
            return BinarySensorDeviceClass.SMOKE
        elif modeltype == MODELTYPE_COALARM:
            return BinarySensorDeviceClass.CO
        elif modeltype in MODELTYPE_PROBLEMS:
            return BinarySensorDeviceClass.PROBLEM
        return None

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attributes = {
            ATTR_INSTALLATIONDATE: self._device.installationdate,
            ATTR_INSTALLEDBY: self._device.installedby,
            ATTR_REPLACEDATE: self._device.replacedate,
            ATTR_SIGNALSTRENGTH: self._device.metadata.signalstrength,
            ATTR_LASTSEENDATE: self._device.metadata.lastseendate,
            ATTR_CONNECTIVITYTYPE: self._device.metadata.connectivitytype,
            ATTR_LASTTESTDATE: self._device.status.lasttesteddate,
            ATTR_DATACOLLECTIONSTATUS: self._device.status.datacollectionstatus,
        }
        if alerts := self._get_alerts():
            alert_attribute = [
                {
                    ATTR_EVENTTYPE: alert.eventtype,
                    ATTR_SEVERITY: alert.severity,
                    ATTR_CATEGORY: alert.category,
                    ATTR_TYPE: alert.hl_type,
                    ATTR_DESCRIPTION: alert.description,
                }
                for alert in alerts
            ]
            attributes[COORD_ALERTS] = alert_attribute

        return attributes

    def _get_alerts(self):
        alerts = []
        for alert in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_ALERTS
        ]:
            if self._device.rel.self == alert.rel.device:
                if not self._sub_type:
                    alerts.append(alert)
                    continue

                if (
                    (
                        self._sub_type == MODELTYPE_FIRECOALARM
                        and alert.eventtype == EVENTTYPE_FIRE_ALARM
                    )
                    or (
                        self._sub_type == MODELTYPE_COALARM
                        and alert.eventtype == EVENTTYPE_CO_ALARM
                    )
                    or alert.eventtype not in EVENTTYPE_FIRECO_ALARMS
                ):
                    alerts.append(alert)

        return alerts

    async def _async_subscribe(
        self, hass: HomeAssistant, component  # pylint: disable=unused-argument
    ):
        await self._async_subscribe_topic(hass, SUBSCRIBE_DEVICE_EVENT_TOPIC)
        await self._async_subscribe_topic(hass, SUBSCRIBE_DEVICE_OTHER_TOPIC)

    async def _async_subscribe_topic(self, hass, topic):
        sub_topic = SUBSCRIBE_DEVICE_FULL_TOPIC.format(
            root_topic=self._root_topic,
            topic=topic,
            parent_key=self._parent_key.lower(),
            key=self._key.lower(),
        )

        await mqtt.async_subscribe(hass, sub_topic, self._async_message_received)

    @callback
    async def _async_message_received(self, msg):
        payload = json.loads(msg.payload)
        msgdate = parser.parse(payload[ATTR_RAISEDDATE])
        if msgdate >= self._startup:
            payload = json.loads(msg.payload)
            eventtype = _extract_event_type(self._root_topic, msg.topic)
            self._raise_event(eventtype, payload)

    def _raise_event(self, event_type, payload):
        self.hass.bus.fire(
            f"{DOMAIN}_{event_type}",
            {
                ATTR_SUB_TYPE: ATTR_DEVICE,
                ATTR_DEVICE_INFO: self.device_info,
                ATTR_PAYLOAD: payload,
            },
        )
        _LOGGER.debug("%s_%s - %s - %s", DOMAIN, event_type, self.device_info, payload)


def _set_root_topic(config_options):
    root_topic = None
    if CONF_MQTT_TOPIC in config_options:
        root_topic = config_options.get(CONF_MQTT_TOPIC)
        if not root_topic.endswith("/"):
            root_topic = f"{root_topic}/"

    return root_topic


def _extract_event_type(root_topic, topic):
    messagetype = topic.removeprefix(root_topic).split("/")[1]
    messagetypes = [item.value for item in HomeLINKMessageType]
    if messagetype in messagetypes:
        return messagetype

    return HomeLINKMessageType.EVENT_UNKNOWN
