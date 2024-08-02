"""Support for HomeLINK sensors."""

import logging
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

# from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from pyhomelink import HomeLINKReadingType

from . import HLConfigEntry
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
    CONF_WEBHOOK_ENABLE,
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
    READINGS,
)
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import HomeLINKAlarmEntity, HomeLINKDeviceEntity
from .helpers.events import raise_reading_event
from .helpers.utils import (
    build_mqtt_device_key,
    device_device_info,
)

_LOGGER = logging.getLogger(__name__)


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
    hass: HomeAssistant, entry: HLConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = entry.runtime_data.coordinator

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
        if hasattr(device.rel, ATTR_READINGS):
            for reading, reading_type in READINGS.items():
                if hasattr(device.rel.readings, reading):
                    _add_sensor_reading(reading_type, device_key)

    def _add_sensor_reading(reading_type, device_key):
        async_add_entities(
            [
                HomeLINKReadingSensor(
                    entry, hl_coordinator, hl_property, device_key, reading_type
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


class HomeLINKReadingSensor(HomeLINKDeviceEntity, SensorEntity):
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
        super().__init__(coordinator, hl_property_key, device_key)

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
        self._unregister_message_handler = None

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

    def _update_attributes(self):
        if (
            self._parent_key not in self.coordinator.data[COORD_PROPERTIES]
            or self._key
            not in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_DEVICES
            ]
        ):
            return
        for reading in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_READINGS
        ]:
            if reading.type != self._readingtype:
                continue
            for device in reading.devices:
                if (
                    device.serialnumber.removeprefix(f"{self._gateway_key}-")
                    != self._key
                ):
                    continue

                if self._readingdate is None:
                    self._update_values(device.values[-1])
                else:
                    for value in device.values:
                        if value.readingdate > self._readingdate:
                            self._update_values(value)
                            self.async_write_ha_state()

                break

    def _update_values(self, value):
        self._state = value.value
        self._readingdate = value.readingdate

    async def async_added_to_hass(self) -> None:
        """Register message handler."""
        await super().async_added_to_hass()
        if self._entry.options.get(CONF_MQTT_ENABLE) or self._entry.options.get(
            CONF_WEBHOOK_ENABLE
        ):
            key = build_mqtt_device_key(
                self._device, f"{self._key}-{self._readingtype}", self._gateway_key
            )

            event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=key).lower()
            self._unregister_message_handler = async_dispatcher_connect(
                self.hass, event, self._async_message_handle
            )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister message handler."""
        if self._unregister_message_handler:
            self._unregister_message_handler()

    @callback
    async def _async_message_handle(self, payload, topic, messagetype, readingtype):
        readingdate = parser.parse(payload[MQTT_READINGDATE])

        if not self._readingdate or readingdate > self._readingdate:
            raise_reading_event(self.hass, messagetype, readingtype, topic, payload)
            self._state = payload[MQTT_VALUE]
            self._readingdate = readingdate
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
                self._insight = insight


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
                self._insight = insight
