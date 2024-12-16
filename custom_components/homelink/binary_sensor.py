"""Support for HomeLINK sensors."""

from collections.abc import Callable
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from pyhomelink.alert import Alert
from pyhomelink.device import Device

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
    CONF_WEBHOOK_ENABLE,
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
    MODELLIST_ENERGY,
    MODELLIST_ENVIRONMENT,
    MODELLIST_PROBLEMS,
    MODELTYPE_COALARM,
    STATUS_GOOD,
    STATUS_NOT_GOOD,
    WEBHOOK_READINGTYPEID,
    HomeLINKMessageType,
)
from .helpers.config_data import HLConfigEntry
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import (
    HomeLINKAlarmEntity,
    HomeLINKDeviceEntity,
)
from .helpers.utils import (
    build_device_identifiers,
    build_mqtt_device_key,
    get_message_date,
    property_device_info,
    raise_device_event,
    raise_property_alarm_event,
)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: HLConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = entry.runtime_data.coordinator

    # Process each property which has binary_sensor for:
    # - Property
    # - Property (Fire) Alarm
    # - Property (Environment) Alarm - if there are eny environment devices
    # - Each device (apart from energy devices since they have no alert status)

    @callback
    def async_add_property(hl_property):
        # Callback since this can be initiated post setup by coordinator
        async_add_entities([HomeLINKProperty(hass, entry, hl_coordinator, hl_property)])
        async_add_entities(
            [HomeLINKAlarm(hass, entry, hl_coordinator, hl_property, ALARMTYPE_ALARM)]
        )
        environment = False
        for device_key, device in hl_coordinator.data[COORD_PROPERTIES][hl_property][
            COORD_DEVICES
        ].items():
            if device.modeltype not in MODELLIST_ENERGY:
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
    def async_add_device(
        hl_property: str,
        device_key: str,
        device: Device,  # pylint: disable=unused-argument
        gateway_key: str,  # pylint: disable=unused-argument
    ) -> None:
        # Callback since this can be initiated post setup by coordinator
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
        entry: HLConfigEntry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)
        self._status: bool | None = None
        self._alarms: list[str | None] | str = []
        self._dev_reg = device_registry.async_get(hass)
        self._key = hl_property_key
        self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
        self._gateway_key = self._property[COORD_GATEWAY_KEY]
        self._update_attributes()
        self._entry = entry
        self._attr_unique_id = f"{self._key}"
        if entry.options.get(CONF_MQTT_ENABLE):
            self._root_topic = _get_mqtt_topic(entry)

    @property
    def name(self) -> None:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self._status

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Entity device information."""
        return property_device_info(self._key)

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        return BinarySensorDeviceClass.SAFETY

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._update_attributes()
        self.async_write_ha_state()

    def _update_attributes(self) -> None:
        if self._key in self.coordinator.data[COORD_PROPERTIES]:
            self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
            self._gateway_key = self._property[COORD_GATEWAY_KEY]
            self._status, self._alarms = self._set_status()

    def _set_status(self) -> tuple[bool, list[str | None] | str]:
        status = STATUS_GOOD
        alarms = []
        # Identify if there are any alerts for the property and set status accordingly
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
        entry: HLConfigEntry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        alarm_type: str,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        self._alerts: list[dict] = []
        self._status: bool | None = None
        self._alarms_devices: list[str | None] | str = []
        self._alarms_rooms: list[str | None] | str = []
        self._dev_reg = device_registry.async_get(hass)
        super().__init__(coordinator, hl_property_key, alarm_type)
        self._entry = entry
        self._attr_unique_id = f"{self._key}_{alarm_type}"
        self._lastdate = dt_util.utcnow()
        self._unregister_message_handler: Callable[[], None] | None = None
        if entry.options.get(CONF_MQTT_ENABLE):
            self._root_topic = _get_mqtt_topic(entry)

    @property
    def name(self) -> None:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self._status

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device_class."""
        return BinarySensorDeviceClass.SAFETY

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attributes = {ATTR_ALARMED_DEVICES: self._alarms_devices}
        # If this is an environment sensor, then alerts link to 'virtual' rooms.
        if self._alarm_type == ALARMTYPE_ENVIRONMENT:
            attributes[ATTR_ALARMED_ROOMS] = self._alarms_rooms
        if self._alerts:
            attributes[ATTR_ALERTS] = self._alerts  # type: ignore[assignment]

        return attributes

    async def async_added_to_hass(self) -> None:
        """Register MQTT handler."""
        # If MQTT or webhooks is enabled then we need the handler for message processing
        await super().async_added_to_hass()
        if self._entry.options.get(CONF_MQTT_ENABLE) or self._entry.options.get(
            CONF_WEBHOOK_ENABLE
        ):
            # Build the unique key for the event
            event = HOMELINK_MESSAGE_MQTT.format(
                domain=DOMAIN, key=f"{self._key}_{self._alarm_type}"
            ).lower()

            self._unregister_message_handler = async_dispatcher_connect(
                self.hass, event, self._async_message_handle
            )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister MQTT handler."""
        if self._unregister_message_handler:
            self._unregister_message_handler()

    def _update_attributes(self) -> None:
        if self._is_data_in_coordinator():
            self._property = self.coordinator.data[COORD_PROPERTIES][self._key]
            self._gateway_key = self._property[COORD_GATEWAY_KEY]
            self._alerts = self._set_alerts()
            self._status, self._alarms_devices, self._alarms_rooms = self._set_status()

    def _is_data_in_coordinator(self) -> bool:
        if self._key in self.coordinator.data[COORD_PROPERTIES]:
            return True
        return False

    def _set_status(self) -> tuple[bool, list[str | None] | str, list[Any] | str]:
        status = STATUS_GOOD
        if self._alerts:
            status = STATUS_NOT_GOOD
        alarms_devices = []
        alarms_rooms = []
        # Identify if there are any alerts for the device and set status accordingly
        # If there is no serial number of location on the alert then it is not for a device
        # If it is for an environment sensor, then there will be no serial number, so allocate
        # to a 'virtual' room.
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

    def _set_alerts(self) -> list[dict]:
        # Alerts relate to devices on than environment sensor
        # so there is no location
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

    def _get_alerts(self) -> list[Alert]:
        # Retrieve the alert if:
        # - Device is environment and the alert is and insight
        # - Device is alarm and alert is not environment and not an insight
        # - Device is environment and alert is environment and not an insight
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
    async def _async_message_handle(
        self, topic: str, payload: dict, messagetype: str
    ) -> None:
        # Process message if it is new (so as to ignore messages retained on the MQTT broker)
        # Initiates a co-ordinator refresh for Device/Property/Alert
        msgdate = get_message_date(payload)
        if msgdate < self._lastdate:
            return
        self._lastdate = msgdate

        raise_property_alarm_event(self.hass, messagetype, topic, payload)

        if messagetype in [
            HomeLINKMessageType.MESSAGE_DEVICE,
            HomeLINKMessageType.MESSAGE_PROPERTY,
            HomeLINKMessageType.MESSAGE_ALERT,
        ]:
            await self.coordinator.async_refresh()
            return


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
        entry: HLConfigEntry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        device_key: str,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        self._alerts: list[dict] = []
        super().__init__(coordinator, hl_property_key, device_key)
        self._entry = entry

        self._attr_unique_id = f"{self._parent_key}_{self._key}".rstrip()
        self._lastdate = dt_util.utcnow()
        self._unregister_message_handler: Callable[[], None] | None = None
        self._device_class = self._build_device_class()

    @property
    def name(self) -> None:
        """Return the name of the sensor."""
        return None

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self._status

    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """Return the device_class."""
        return self._device_class

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
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
        """Register message handler."""
        # If MQTT or webhooks is enabled then we need the handler for message processing
        await super().async_added_to_hass()
        if self._entry.options.get(CONF_MQTT_ENABLE) or self._entry.options.get(
            CONF_WEBHOOK_ENABLE
        ):
            # Build the unique key for the event
            key = build_mqtt_device_key(self._device, self._key, self._gateway_key)
            event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=key).lower()
            self._unregister_message_handler = async_dispatcher_connect(
                self.hass, event, self._async_message_handle
            )

            # Also add a handler on location for environment sensor
            if self._device.modeltype in MODELLIST_ENVIRONMENT:
                event = HOMELINK_MESSAGE_MQTT.format(
                    domain=DOMAIN, key=self._device.location
                ).lower()
                self._unregister_message_handler = async_dispatcher_connect(
                    self.hass, event, self._async_message_handle
                )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister message handler."""
        if self._unregister_message_handler:
            self._unregister_message_handler()

    def _build_device_class(self) -> BinarySensorDeviceClass | None:
        modeltype = self._device.modeltype
        if modeltype in MODELLIST_ALARMS:
            return BinarySensorDeviceClass.SMOKE
        if modeltype == MODELTYPE_COALARM:
            return BinarySensorDeviceClass.CO
        if modeltype in MODELLIST_PROBLEMS or modeltype in MODELLIST_ENVIRONMENT:
            return BinarySensorDeviceClass.PROBLEM
        return None

    def _update_attributes(self) -> None:
        if not self._is_data_in_coordinator():
            return

        self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        self._gateway_key = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_GATEWAY_KEY
        ]
        self._alerts = self._set_alerts()
        self._status = self._set_status()

    def _is_data_in_coordinator(self) -> bool:
        if (
            self._parent_key not in self.coordinator.data[COORD_PROPERTIES]
            or self._key
            not in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_DEVICES
            ]
        ):
            return False
        return True

    def _set_status(self) -> bool:
        return bool(self._get_alerts())

    def _set_alerts(self) -> list[dict]:
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

    def _get_alerts(self) -> list[Alert]:
        # Retrieve the alert if:
        # - The alert is a device and is for the entity device
        # - The alert location is entity location and there is no serialnumber
        #   (which indicates it is an environment alert)
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
    async def _async_message_handle(
        self, payload: dict, topic: str, messagetype: str
    ) -> None:
        # Process message if it is new (so as to ignore messages retained on the MQTT broker)
        # If it is a reading then pass it over to the reading sensor by dispatch
        # Otherwise initiates a co-ordinator refresh for Alert
        msgdate = get_message_date(payload)
        if msgdate < self._lastdate and messagetype not in [
            HomeLINKMessageType.MESSAGE_READING,
        ]:
            return
        self._lastdate = msgdate

        if messagetype in [
            HomeLINKMessageType.MESSAGE_READING,
        ]:
            self._process_reading(payload, topic, messagetype)
            return

        raise_device_event(self.hass, self.device_info, messagetype, topic, payload)
        if messagetype in [
            HomeLINKMessageType.MESSAGE_ALERT,
        ]:
            await self.coordinator.async_refresh()

    def _process_reading(self, payload: dict, topic: str, messagetype: str) -> None:
        # Dispatch to reading sensor
        readingtype = payload[WEBHOOK_READINGTYPEID].replace(".", "-")

        key = build_mqtt_device_key(
            self._device, f"{self._key}-{readingtype}", self._gateway_key
        )

        event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=key).lower()
        dispatcher_send(self.hass, event, payload, topic, messagetype, readingtype)


def _get_mqtt_topic(entry: HLConfigEntry) -> str:
    mqtt_topic: Any = entry.options.get(CONF_MQTT_TOPIC)
    return mqtt_topic.removesuffix("#")
