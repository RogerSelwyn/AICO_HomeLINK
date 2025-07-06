"""Support for HomeLINK sensors."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dateutil import parser
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from pyhomelink import HomeLINKReadingType
from pyhomelink.device import Device, RelEnvironment
from pyhomelink.insight import Insight

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
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    HOMELINK_MESSAGE_MQTT,
    MODELLIST_ENERGY,
    MODELLIST_ENVIRONMENT,
    MODELTYPE_SMARTMETERELEC,
    MODELTYPE_SMARTMETERGAS,
    MODELTYPE_SMARTMETERGASELEC,
    MQTT_READINGDATE,
    MQTT_VALUE,
    READINGS_ENVIRONMENT,
    READINGS_SENSOR_ELECTRIC,
    READINGS_SENSOR_ELECTRIC_TARIFF,
    READINGS_SENSOR_GAS,
    READINGS_SENSOR_GAS_TARIFF,
    SENSOR_TRANSLATION_KEY,
)
from .helpers.config_data import HLConfigEntry
from .helpers.coordinator import HomeLINKDataCoordinator
from .helpers.entity import HomeLINKAlarmEntity, HomeLINKDeviceEntity
from .helpers.utils import (
    build_mqtt_device_key,
    device_device_info,
    raise_reading_event,
)

PARALLEL_UPDATES = 1


@dataclass(kw_only=True, frozen=True)
class HomeLINKEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], StateType]


@dataclass(kw_only=True, frozen=True)
class HomeLINKEntityDescription(
    SensorEntityDescription, HomeLINKEntityDescriptionMixin
):
    """Describes HomeLINK sensor entity."""


SENSOR_TYPES: tuple[HomeLINKEntityDescription, ...] = (
    HomeLINKEntityDescription(  # pylint: disable=unexpected-keyword-arg
        key=ATTR_REPLACEDATE,
        device_class=SensorDeviceClass.DATE,
        translation_key="replace_by_date",
        value_fn=lambda data: data.replacedate.date() or None,
    ),
    HomeLINKEntityDescription(  # pylint: disable=unexpected-keyword-arg
        key=ATTR_LASTTESTDATE,
        device_class=SensorDeviceClass.TIMESTAMP,
        translation_key="last_tested_date",
        value_fn=lambda data: data.status.lasttesteddate,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: HLConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = entry.runtime_data.coordinator

    # Process each property which has sensor for:
    # - Device
    # - Insight - the number of these build up over time, but do not then drop off

    @callback
    def async_add_sensor_property(hl_property) -> None:
        # Callback since this can be initiated post setup by coordinator
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
                _add_sensor_insight(hl_property, insight)

    @callback
    def async_add_sensor_device(
        hl_property: str,
        device_key: str,
        device: Device,
        gateway_key: str | None,  # pylint: disable=unused-argument
    ) -> None:
        # Callback since this can be initiated post setup by coordinator

        # Non-energy devices
        # - Adds replace by date and last tested date sensors
        # - Adds Reading sensors (if it is an environment device)
        # Energy (virtual) devices - Adds gas/electric sensors as needed based on model type

        if device.modeltype not in MODELLIST_ENERGY:
            async_add_entities(
                [
                    HomeLINKSensor(hl_coordinator, hl_property, device_key, description)
                    for description in SENSOR_TYPES
                ]
            )
            if isinstance(device.rel, RelEnvironment):
                for reading, reading_type in READINGS_ENVIRONMENT.items():
                    if hasattr(device.rel.readings, reading):
                        _add_sensor_reading(hl_property, reading_type, device_key)

        else:
            if device.modeltype in [
                MODELTYPE_SMARTMETERGASELEC,
                MODELTYPE_SMARTMETERELEC,
            ]:
                _add_sensor_energy_reading(
                    hl_property, READINGS_SENSOR_ELECTRIC, device_key
                )
                _add_sensor_energy_reading(
                    hl_property, READINGS_SENSOR_ELECTRIC_TARIFF, device_key
                )
            if device.modeltype in [
                MODELTYPE_SMARTMETERGASELEC,
                MODELTYPE_SMARTMETERGAS,
            ]:
                _add_sensor_energy_reading(hl_property, READINGS_SENSOR_GAS, device_key)
                _add_sensor_energy_reading(
                    hl_property, READINGS_SENSOR_GAS_TARIFF, device_key
                )

    def _add_sensor_reading(
        hl_property: str, reading_type: str, device_key: str
    ) -> None:
        async_add_entities(
            [
                HomeLINKReadingSensor(
                    entry, hl_coordinator, hl_property, device_key, reading_type
                )
            ]
        )

    def _add_sensor_energy_reading(
        hl_property: str, reading_type: str, device_key: str
    ) -> None:
        async_add_entities(
            [
                HomeLINKEnergyReadingSensor(
                    entry, hl_coordinator, hl_property, device_key, reading_type
                )
            ]
        )

    def _add_sensor_insight(hl_property: str, insight: Insight) -> None:
        # If insight relates to a 'virtual' room then create room insight sensor
        # otherwise create a property insight sensor
        if insight.appliesto == APPLIESTO_ROOM:
            async_add_entities(
                [HomeLINKRoomInsightSensor(hl_coordinator, hl_property, insight)]
            )
        else:
            async_add_entities(
                [HomeLINKPropertyInsightSensor(hl_coordinator, hl_property, insight)]
            )

    for property_ref in hl_coordinator.data[COORD_PROPERTIES]:
        async_add_sensor_property(property_ref)

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_PROPERTY, async_add_sensor_property)
    )

    entry.async_on_unload(
        async_dispatcher_connect(hass, HOMELINK_ADD_DEVICE, async_add_sensor_device)
    )


class HomeLINKSensor(HomeLINKDeviceEntity, SensorEntity):
    """Sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    entity_description: HomeLINKEntityDescription

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        device_key: str,
        description: HomeLINKEntityDescription,
    ) -> None:
        """Device entity object for HomeLINK sensor."""
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} {description.key}"
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return native value."""
        return self.entity_description.value_fn(self._device)

    def _update_attributes(self) -> None:
        if self._is_data_in_coordinator():
            self._device = self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_DEVICES
            ][self._key]
            self._gateway_key = self.coordinator.data[COORD_PROPERTIES][
                self._parent_key
            ][COORD_GATEWAY_KEY]

    def _is_data_in_coordinator(self) -> bool:
        if (
            self._parent_key in self.coordinator.data[COORD_PROPERTIES]
            and self._key
            in self.coordinator.data[COORD_PROPERTIES][self._parent_key][COORD_DEVICES]
        ):
            return True
        return False


class HomeLINKReadingSensor(HomeLINKDeviceEntity, SensorEntity):
    """Reading sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: HLConfigEntry,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        device_key: str,
        readingtype: str,
    ) -> None:
        """Entity object - Reading - for HomeLINK sensor."""
        self._readingtype = readingtype
        self._state = None
        self._readingdate: datetime | None = None
        super().__init__(coordinator, hl_property_key, device_key)

        self._entry = entry

        self._attr_unique_id = f"{self._parent_key}_{self._key} {readingtype}"
        # Setup the HA attributes based on type of sensor.
        # There is probably a better way of doing this.
        if readingtype == HomeLINKReadingType.CO2:
            self._attr_device_class = SensorDeviceClass.CO2
            self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif readingtype == HomeLINKReadingType.HUMIDITY:
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif readingtype == HomeLINKReadingType.TEMPERATURE:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif readingtype in [READINGS_SENSOR_ELECTRIC, READINGS_SENSOR_GAS]:
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL
        elif readingtype in [
            READINGS_SENSOR_ELECTRIC_TARIFF,
            READINGS_SENSOR_GAS_TARIFF,
        ]:
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_native_unit_of_measurement = "GBp/kWh"
            self._attr_suggested_display_precision = 2
        self._unregister_message_handler: Callable[[], None] | None = None

    @property
    def native_value(self) -> Any:
        """Return native value."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_READINGDATE: self._readingdate, ATTR_TYPE: ATTR_READING}

    @property
    def device_info(self) -> DeviceInfo:
        """Entity device information."""
        return device_device_info(self._identifiers, self._parent_key, self._device)

    def _update_attributes(self) -> None:
        if not self._is_data_in_coordinator():
            return
        # Extract the right data from co-ordinator
        # - Is it the right reading type
        # - Is it the right device (remove the gateway key if needed)
        # - Get the latest reading (because they may not be sorted)
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

                for value in device.values:
                    if (
                        self._readingdate is None
                        or value.readingdate > self._readingdate
                    ):
                        self._update_values(value)
                if self.hass:
                    self.async_write_ha_state()

                break

    def _is_data_in_coordinator(self) -> bool:
        return (
            self._parent_key in self.coordinator.data[COORD_PROPERTIES]
            and self._key
            in self.coordinator.data[COORD_PROPERTIES][self._parent_key][COORD_DEVICES]
        )

    def _update_values(self, value: Any) -> None:
        self._state = value.value
        self._readingdate = value.readingdate

    async def async_added_to_hass(self) -> None:
        """Register message handler."""
        # If MQTT or webhooks is enabled then we need the handler for message processing
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
    async def _async_message_handle(
        self, payload: dict, topic: str, messagetype: str, readingtype: str
    ) -> None:
        # Happy to process any messages retained on the MQTT broker to bring us up to date
        readingdate = parser.parse(payload[MQTT_READINGDATE])

        if not self._readingdate or readingdate > self._readingdate:
            raise_reading_event(self.hass, messagetype, readingtype, topic, payload)
            self._state = payload[MQTT_VALUE]
            self._readingdate = readingdate
            self.async_write_ha_state()


class HomeLINKEnergyReadingSensor(HomeLINKReadingSensor):
    """An energy Reading Sensor."""

    @property
    def translation_key(self) -> str:
        """Entity Translation Key."""
        return SENSOR_TRANSLATION_KEY[self._readingtype]


class HomeLINKPropertyInsightSensor(HomeLINKAlarmEntity, SensorEntity):
    """Property Insight sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        insight: Insight,
    ) -> None:
        """Insight entity object for HomeLINK sensor."""
        self._insight = insight
        super().__init__(coordinator, hl_property_key, ALARMTYPE_ENVIRONMENT)
        self._attr_unique_id = f"{self._key}_{ALARMTYPE_ENVIRONMENT} {insight.hl_type}"

    @property
    def name(self) -> str:
        """Return name."""
        return self._insight.hl_type.capitalize()

    @property
    def native_value(self) -> Any:
        """Return native value."""
        return self._insight.value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_TYPE: ATTR_INSIGHT_PROPERTY,
            ATTR_INSIGHTID: self._insight.insightid,
            ATTR_RISKLEVEL: self._insight.risklevel,
            ATTR_CALCULATEDAT: self._insight.calculatedat,
        }

    def _update_attributes(self) -> None:
        for insight in self.coordinator.data[COORD_PROPERTIES][self._key][
            COORD_INSIGHTS
        ]:
            if (
                insight.appliesto == APPLIESTO_PROPERTY
                and insight.hl_type == self._insight.hl_type
            ):
                self._insight = insight

    def _is_data_in_coordinator(self) -> bool:
        return any(
            (
                insight.appliesto == APPLIESTO_PROPERTY
                and insight.hl_type == self._insight.hl_type
            )
            for insight in self.coordinator.data[COORD_PROPERTIES][self._key][
                COORD_INSIGHTS
            ]
        )


class HomeLINKRoomInsightSensor(HomeLINKDeviceEntity, SensorEntity):
    """Device Insight sensor entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property_key: str,
        insight: Insight,
    ) -> None:
        """Insight entity object for HomeLINK sensor."""
        self._insight = insight
        device_key = self._get_device_key(
            coordinator, hl_property_key, insight.location
        )
        super().__init__(coordinator, hl_property_key, device_key)
        self._attr_unique_id = f"{self._parent_key}_{self._key} {insight.hl_type}"

    def _get_device_key(
        self, coordinator: HomeLINKDataCoordinator, hl_property_key: str, location: str
    ):
        # An insight 'virtual' location does not have a hard linked environment device,
        # so we have to go figure it out by looking for the locations on the available
        # environment type devices
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
        """Return name."""
        return self._insight.hl_type.capitalize()

    @property
    def native_value(self) -> Any:
        """Return native value."""
        return self._insight.value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_TYPE: ATTR_INSIGHT_ROOM,
            ATTR_INSIGHTID: self._insight.insightid,
            ATTR_RISKLEVEL: self._insight.risklevel,
            ATTR_CALCULATEDAT: self._insight.calculatedat,
        }

    def _update_attributes(self) -> None:
        for insight in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
            COORD_INSIGHTS
        ]:
            if (
                insight.appliesto == APPLIESTO_ROOM
                and insight.location == self._insight.location
                and insight.hl_type == self._insight.hl_type
            ):
                self._insight = insight

    def _is_data_in_coordinator(self) -> bool:
        return any(
            (
                insight.appliesto == APPLIESTO_ROOM
                and insight.location == self._insight.location
                and insight.hl_type == self._insight.hl_type
            )
            for insight in self.coordinator.data[COORD_PROPERTIES][self._parent_key][
                COORD_INSIGHTS
            ]
        )
