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
    ATTRIBUTION,
    CONF_MQTT_ENABLE,
    CONF_MQTT_TOPIC,
    DOMAIN,
    EVENT_ALERT,
    EVENT_EVENT,
    EVENT_UNKNOWN,
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
    for hl_property in hl_coordinator.data["properties"]:
        hl_entities.append(
            HomeLINKProperty(hass, entry.options, hl_coordinator, hl_property)
        )
        for device in hl_coordinator.data["properties"][hl_property]["devices"]:
            if (
                hl_coordinator.data["properties"][hl_property]["devices"][
                    device
                ].modeltype
                == "FIRECOALARM"
            ):
                hl_entities.extend(
                    (
                        HomeLINKDevice(
                            hl_coordinator, hl_property, device, "FIREALARM"
                        ),
                        HomeLINKDevice(hl_coordinator, hl_property, device, "COALARM"),
                    )
                )
            else:
                hl_entities.append(HomeLINKDevice(hl_coordinator, hl_property, device))
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
        self._property = coordinator.data["properties"][self._key]
        self._startup = dt.utcnow()
        self._config_options = config_options
        self._root_topic = ""
        if self._config_options.get(CONF_MQTT_ENABLE):
            async_when_setup(hass, MQTT_DOMAIN, self._async_subscribe)

    @property
    def name(self) -> str:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        status = "GOOD"
        for devicekey in self._property["devices"]:
            device = self._property["devices"][devicekey]
            if device.status.operationalstatus != "GOOD":
                status = device.status.operationalstatus
        return status != "GOOD"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        return BinarySensorDeviceClass.SAFETY

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        hl_property = self._property["property"]
        return {
            "reference": hl_property.reference,
            "address": hl_property.address,
            "latitide": hl_property.latitude,
            "longitude": hl_property.longitude,
            "tags": hl_property.tags,
        }

    @property
    def device_info(self):
        """Entity device information."""
        return {
            ATTR_IDENTIFIERS: {(DOMAIN, "property", self._key)},
            ATTR_NAME: self._key,
            ATTR_MANUFACTURER: "HomeLINK",
            ATTR_MODEL: "Property",
            ATTR_CONFIGURATION_URL: "https://dashboard.live.homelync.io/#/pages/portfolio/one-view",
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._property = self.coordinator.data["properties"][self._key]
        self.async_write_ha_state()

    async def _async_subscribe(
        self, hass: HomeAssistant, component  # pylint: disable=unused-argument
    ):
        self._set_root_topic()
        await self._async_subscribe_topic(hass, "+/event/")
        await self._async_subscribe_topic(hass, "+/alert/+/")

    async def _async_subscribe_topic(self, hass, topic):
        sub_topic = f"{self._root_topic}{topic}{self._key.lower()}/#"
        _LOGGER.debug("Subscribing to: %s", sub_topic)
        await mqtt.async_subscribe(hass, sub_topic, self._async_message_received)

    @callback
    async def _async_message_received(self, msg):
        payload = json.loads(msg.payload)
        msgdate = parser.parse(payload["raisedDate"])
        if msgdate >= self._startup:
            payload = json.loads(msg.payload)
            if f"/{EVENT_ALERT}/" in msg.topic:
                self._raise_event(EVENT_ALERT, payload)
            elif f"/{EVENT_EVENT}/" in msg.topic:
                self._raise_event(EVENT_EVENT, payload)
            else:
                self._raise_event(EVENT_UNKNOWN, payload)

    def _raise_event(self, event_type, payload):
        self.hass.bus.fire(
            f"{DOMAIN}_{event_type}",
            payload,
        )
        _LOGGER.debug("%s_%s - %s", DOMAIN, event_type, payload)

    def _set_root_topic(self):
        if CONF_MQTT_TOPIC in self._config_options:
            self._root_topic = self._config_options.get(CONF_MQTT_TOPIC)
            if not self._root_topic.endswith("/"):
                self._root_topic = f"{self._root_topic}/"


class HomeLINKDevice(HomeLINKEntity, BinarySensorEntity):
    """Device entity object for HomeLINK sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
        sub_type=None,
    ) -> None:
        """Device entity object for HomeLINKi sensor."""
        super().__init__(coordinator, hl_property_key, device_key)

        self._attr_unique_id = f"{self._parent_key}_{self._key} {sub_type}".rstrip()
        self._sub_type = sub_type

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._sub_type}" if self._sub_type else None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        if self._device.status.operationalstatus == "GOOD":
            return False

        return bool(self._get_alerts())

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        modeltype = self._sub_type or self._device.modeltype
        if modeltype == "FIREALARM":
            return BinarySensorDeviceClass.SMOKE
        elif modeltype == "COALARM":
            return BinarySensorDeviceClass.CO
        elif modeltype in ["EIACCESSORY", "GATEWAY"]:
            return BinarySensorDeviceClass.PROBLEM
        return None

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attributes = {
            "installationdate": self._device.installationdate,
            "installedby": self._device.installedby,
            "replacedate": self._device.replacedate,
            "signalstrength": self._device.metadata.signalstrength,
            "lastseendate": self._device.metadata.lastseendate,
            "connectivitytype": self._device.metadata.connectivitytype,
            "lasttesteddate": self._device.status.lasttesteddate,
            "datacollectionstatus": self._device.status.datacollectionstatus,
        }
        if alerts := self._get_alerts():
            alert_attribute = [
                {
                    "eventtype": alert.eventtype,
                    "severity": alert.severity,
                    "category": alert.category,
                    "type": alert.hl_type,
                    "description": alert.description,
                }
                for alert in alerts
            ]
            attributes["alerts"] = alert_attribute

        return attributes

    def _get_alerts(self):
        alerts = []
        for alert in self.coordinator.data["properties"][self._parent_key]["alerts"]:
            if self._device.rel.self == alert.rel.device:
                if not self._sub_type:
                    alerts.append(alert)
                    continue

                if (
                    (self._sub_type == "FIREALARM" and alert.eventtype == "FIRE_ALARM")
                    or (self._sub_type == "COALARM" and alert.eventtype == "CO_ALARM")
                    or alert.eventtype not in ["FIRE_ALARM", "CO_ALARM"]
                ):
                    alerts.append(alert)

        return alerts
