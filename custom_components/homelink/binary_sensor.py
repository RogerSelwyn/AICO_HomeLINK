"""Support for HomeLINK sensors."""

from homeassistant.components.binary_sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import HomeLINKDataCoordinator
from .entity import HomeLINKEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """HomeLINK Sensor Setup."""
    hl_coordinator: HomeLINKDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    hl_entities = []
    for hl_property in hl_coordinator.data["properties"]:
        hl_entities.append(HomeLINKPropertyEntity(hl_coordinator, hl_property))
        for device in hl_coordinator.data["properties"][hl_property]["devices"]:
            if (
                hl_coordinator.data["properties"][hl_property]["devices"][
                    device
                ].modeltype
                == "FIRECOALARM"
            ):
                hl_entities.extend(
                    (
                        HomeLINKDeviceEntity(
                            hl_coordinator, hl_property, device, "FIREALARM"
                        ),
                        HomeLINKDeviceEntity(
                            hl_coordinator, hl_property, device, "COALARM"
                        ),
                    )
                )
            else:
                hl_entities.append(
                    HomeLINKDeviceEntity(hl_coordinator, hl_property, device)
                )
    async_add_entities(hl_entities)


class HomeLINKPropertyEntity(
    CoordinatorEntity[HomeLINKDataCoordinator], BinarySensorEntity
):
    """Property entity object for HomeLINK sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: HomeLINKDataCoordinator,
        hl_property,
    ) -> None:
        """Property entity object for HomeLINK sensor."""
        super().__init__(coordinator)

        self._key = hl_property
        self._attr_unique_id = f"{self._key}"
        self._property = coordinator.data["properties"][self._key]
        # self.entity_description = description

    @property
    def name(self) -> str:
        """Return the name of the sensor as device name."""
        return None

    @property
    def is_on(self) -> str:
        """Return the state of the sensor."""
        status = "GOOD"
        for alert in self._property["alerts"]:
            if alert.status.operationalstatus != "GOOD":
                status = alert.status.operationalstatus
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


class HomeLINKDeviceEntity(HomeLINKEntity, BinarySensorEntity):
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
        return self._device.status.operationalstatus != "GOOD"

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
        return {
            "installationdate": self._device.installationdate,
            "installedby": self._device.installedby,
            "replacedate": self._device.replacedate,
            "signalstrength": self._device.metadata.signalstrength,
            "lastseendate": self._device.metadata.lastseendate,
            "connectivitytype": self._device.metadata.connectivitytype,
            "lasttesteddate": self._device.status.lasttesteddate,
            "datacollectionstatus": self._device.status.datacollectionstatus,
        }
