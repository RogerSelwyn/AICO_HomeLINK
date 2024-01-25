"""Support for HomeLINK sensors."""
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from dateutil import parser
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_STATE,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from pyhomelink import HomeLINKReadingType

from .const import (
    ALARMTYPE_ENVIRONMENT,
    APPLIESTO_PROPERTY,
    APPLIESTO_ROOM,
    ATTR_CALCULATEDAT,
    ATTR_INSIGHT_PROPERTY,
    ATTR_INSIGHT_ROOM,
    ATTR_INSIGHTID,
    ATTR_LASTTESTDATE,
    ATTR_READING,
    ATTR_READINGDATE,
    ATTR_READINGS,
    ATTR_REPLACEDATE,
    ATTR_RISKLEVEL,
    ATTR_TYPE,
    CONF_INSIGHTS_ENABLE,
    CONF_MQTT_ENABLE,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_INSIGHTS,
    COORD_PROPERTIES,
    COORD_READINGS,
    DOMAIN,
    ENTITY_NAME_LASTTESTDATE,
    ENTITY_NAME_REPLACEDATE,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    HOMELINK_MESSAGE_MQTT,
    MODELLIST_ENVIRONMENT,
    MQTT_READINGDATE,
    MQTT_VALUE,
)
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import HomeLINKAlarmEntity, HomeLINKDeviceEntity
from .helpers.events import raise_reading_event
from .helpers.utils import (
    build_device_identifiers,
    build_mqtt_device_key,
    device_device_info,
    read_state,
    write_state,
)


@dataclass
class HomeLINKEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], StateType]


@dataclass
class HomeLINKEntityDescription(
    SensorEntityDescription, HomeLINKEntityDescriptionMixin
):
    """Describes HomeLINK sensor entity."""


SENSOR_TYPES: tuple[HomeLINKEntityDescription, ...] = (
    HomeLINKEntityDescription(  # pylint: disable=unexpected-keyword-arg
        key=ATTR_REPLACEDATE,
        name=ENTITY_NAME_REPLACEDATE,
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: data.replacedate.date() or None,
    ),
    HomeLINKEntityDescription(  # pylint: disable=unexpected-keyword-arg
        key=ATTR_LASTTESTDATE,
        name=ENTITY_NAME_LASTTESTDATE,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.status.lasttesteddate,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_sensor_property(hl_property):
        for device_key, device in hl_coordinator.data[COORD_PROPERTIES][hl_property][
            COORD_DEVICES
        ].items():
            async_add_sensor_device(hl_property, device_key, device, None)
        if (
            entry.options.get(CONF_INSIGHTS_ENABLE)
            and COORD_INSIGHTS in hl_coordinator.data[COORD_PROPERTIES][hl_property]
        ):
            for insight in hl_coordinator.data[COORD_PROPERTIES][hl_property][
                COORD_INSIGHTS
            ]:
                _add_sensor_insight(insight)

    @callback
    def async_add_sensor_device(hl_property, device_key, device, gateway_key):  # pylint: disable=unused-argument
        async_add_entities(
            [
                HomeLINKSensor(hl_coordinator, hl_property, device_key, description)
                for description in SENSOR_TYPES
            ]
        )
        if hasattr(device.rel, ATTR_READINGS) and entry.options.get(CONF_MQTT_ENABLE):
            for reading in hl_coordinator.data[COORD_PROPERTIES][hl_property][
                COORD_READINGS
            ]:
                for readingdevice in reading.devices:
                    if readingdevice.serialnumber == device_key:
                        _add_sensor_reading(reading, device_key)

    def _add_sensor_reading(reading, device_key):
        async_add_entities(
            [
                HomeLINKReadingSensor(
                    entry, hl_coordinator, hl_property, device_key, reading.type
                )
            ]
        )

    def _add_sensor_insight(insight):
        if insight.appliesto == APPLIESTO_ROOM:
            async_add_entities(
                [HomeLINKRoomInsightSensor(hl_coordinator, hl_property, insight)]
            )
        else:
            async_add_entities(
                [HomeLINKPropertyInsightSensor(hl_coordinator, hl_property, insight)]
            )

    for hl_property in hl_coordinator.data[COORD_PROPERTIES]:
        async_add_sensor_property(hl_property)

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_PROPERTY, async_add_sensor_property)
    )

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_DEVICE, async_add_sensor_device)
    )


class HomeLINKSensor(HomeLINKDeviceEntity, SensorEntity):
    """Sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    entity_description: HomeLINKEntityDescription

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
        description: HomeLINKEntityDescription,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} {description.key}"
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._device)

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


class HomeLINKReadingSensor(SensorEntity):
    """Reading sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        entry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        device_key,
        readingtype,
    ) -> None:
        """Reading entity object for HomeLINK sensor."""
        self._readingtype = readingtype
        self._state = None
        self._readingdate = None
        self._parent_key = hl_property_key
        self._key = device_key
        self._device = coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_DEVICES
        ][self._key]
        self._gateway_key = coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_GATEWAY_KEY
        ]
        self._identifiers = build_device_identifiers(device_key)
        self._entry = entry

        self._attr_unique_id = f"{self._parent_key}_{self._key} {readingtype}"
        if readingtype == HomeLINKReadingType.CO2:
            self._attr_device_class = SensorDeviceClass.CO2
            self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
        elif readingtype == HomeLINKReadingType.HUMIDITY:
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif readingtype == HomeLINKReadingType.TEMPERATURE:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._unregister_mqtt_handler = None

        self._initial_attributes(coordinator)

    @property
    def native_value(self) -> Any:
        return self._state

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {ATTR_READINGDATE: self._readingdate, ATTR_TYPE: ATTR_READING}

    @property
    def device_info(self):
        """Entity device information."""
        return device_device_info(self._identifiers, self._parent_key, self._device)

    def _initial_attributes(self, coordinator):
        if (
            self._parent_key not in coordinator.data[COORD_PROPERTIES]
            or self._key
            not in coordinator.data[COORD_PROPERTIES][self._parent_key][COORD_DEVICES]
        ):
            return
        for reading in coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_READINGS
        ]:
            if reading.type != self._readingtype:
                continue
            for device in reading.devices:
                if device.serialnumber != self._key:
                    continue
                self._state = device.values[len(device.values) - 1].value
                self._readingdate = device.values[len(device.values) - 1].readingdate
                break

    async def async_added_to_hass(self) -> None:
        """Register MQTT handler."""
        await super().async_added_to_hass()
        if attributes := read_state(self.hass, self.device_class, self._key):
            self._state = attributes[ATTR_STATE]
            self._readingdate = parser.parse(attributes[ATTR_READINGDATE])
        if self._entry.options.get(CONF_MQTT_ENABLE):
            key = build_mqtt_device_key(
                self._device, f"{self._key}-{self._readingtype}", self._gateway_key
            )

            event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=key).lower()
            self._unregister_mqtt_handler = async_dispatcher_connect(
                self.hass, event, self._async_mqtt_handle
            )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister MQTT handler."""
        if self._unregister_mqtt_handler:
            self._unregister_mqtt_handler()

    @callback
    async def _async_mqtt_handle(self, msg, topic, messagetype, readingtype):
        payload = json.loads(msg.payload)
        raise_reading_event(self.hass, messagetype, readingtype, topic, payload)

        self._state = payload[MQTT_VALUE]
        self._readingdate = parser.parse(payload[MQTT_READINGDATE])
        write_state(
            self.hass,
            self.device_class,
            self._key,
            {
                ATTR_STATE: self._state,
                ATTR_READINGDATE: self._readingdate.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
        )
        self.async_write_ha_state()


class HomeLINKPropertyInsightSensor(HomeLINKAlarmEntity, SensorEntity):
    """Property Insight sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        insight,
    ) -> None:
        """Insight entity object for HomeLINK sensor."""
        self._insight = insight
        super().__init__(coordinator, hl_property_key, ALARMTYPE_ENVIRONMENT)
        self._attr_unique_id = f"{self._key}_{ALARMTYPE_ENVIRONMENT} {insight.hl_type}"

    @property
    def name(self) -> Any:
        return self._insight.hl_type.capitalize()

    @property
    def native_value(self) -> Any:
        return self._insight.value

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {
            ATTR_TYPE: ATTR_INSIGHT_PROPERTY,
            ATTR_INSIGHTID: self._insight.insightid,
            ATTR_RISKLEVEL: self._insight.risklevel,
            ATTR_CALCULATEDAT: parser.parse(self._insight.calculatedat),
        }

    def _update_attributes(self):
        for insight in self.coordinator.data[COORD_PROPERTIES][self._key][
            COORD_INSIGHTS
        ]:
            if (
                insight.appliesto == APPLIESTO_PROPERTY
                and insight.hl_type == self._insight.hl_type
            ):
                self.insight = insight


class HomeLINKRoomInsightSensor(HomeLINKDeviceEntity, SensorEntity):
    """Device Insight sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key,
        insight,
    ) -> None:
        """Insight entity object for HomeLINK sensor."""
        self._insight = insight
        device_key = self._get_device_key(
            coordinator, hl_property_key, insight.location
        )
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} {insight.hl_type}"

    def _get_device_key(self, coordinator, hl_property_key, location):
        return next(
            (
                device_key
                for device_key, device in coordinator.data[COORD_PROPERTIES][
                    hl_property_key
                ][COORD_DEVICES].items()
                if location in [device.location, device.locationnickname]
                and device.modeltype in MODELLIST_ENVIRONMENT
            ),
            None,
        )

    @property
    def name(self) -> Any:
        return self._insight.hl_type.capitalize()

    @property
    def native_value(self) -> Any:
        return self._insight.value

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {
            ATTR_TYPE: ATTR_INSIGHT_ROOM,
            ATTR_INSIGHTID: self._insight.insightid,
            ATTR_RISKLEVEL: self._insight.risklevel,
            ATTR_CALCULATEDAT: parser.parse(self._insight.calculatedat),
        }

    def _update_attributes(self):
        for insight in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_INSIGHTS
        ]:
            if (
                insight.appliesto == APPLIESTO_ROOM
                and insight.location == self._insight.location
                and insight.hl_type == self._insight.hl_type
            ):
                self.insight = insight
