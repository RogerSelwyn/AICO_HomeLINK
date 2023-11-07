"""HomeLINK coordinators."""
import asyncio
import logging
from copy import deepcopy
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

from pyhomelink import HomeLINKApi
from pyhomelink.exceptions import ApiException, AuthException

from ..const import (ATTR_PROPERTY, COORD_ALERTS, COORD_DATA_MQTT,
                     COORD_DEVICES, COORD_GATEWAY_KEY, COORD_INSIGHTS,
                     COORD_LOOKUP_EVENTTYPE, COORD_PROPERTIES, COORD_PROPERTY,
                     DOMAIN, HOMELINK_ADD_DEVICE, HOMELINK_ADD_PROPERTY,
                     HOMELINK_LOOKUP_EVENTTYPE, KNOWN_DEVICES_CHILDREN,
                     KNOWN_DEVICES_ID, MODELTYPE_GATEWAY)

_LOGGER = logging.getLogger(__name__)


class HomeLINKDataCoordinator(DataUpdateCoordinator):
    """HomeLINK Data object."""

    def __init__(
        self, hass: HomeAssistant, hl_api: HomeLINKApi, entry: ConfigEntry
    ) -> None:
        """Initialize HomeLINKDataCoordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="HomeLINK Data",
            update_interval=timedelta(seconds=30),
            always_update=False,
        )
        self._hl_api = hl_api
        self._entry = entry
        self._known_properties = {}
        self._ent_reg = entity_registry.async_get(hass)
        self._dev_reg = device_registry.async_get(hass)
        self._first_refresh = True
        self._eventtypes = []
        self._error = False

    async def _async_update_data(self):
        """Fetch data from API endpoint."""

        try:
            async with asyncio.timeout(10):
                if not self._eventtypes:
                    await self._async_get_eventtypes_lookup()

                coord_properties = await self._async_get_core_data()

                await self._async_check_for_changes(coord_properties)
                hl_mqtt = self._get_previous_mqtt()

                self._error = False
                return {
                    COORD_PROPERTIES: coord_properties,
                    COORD_DATA_MQTT: hl_mqtt,
                    COORD_LOOKUP_EVENTTYPE: self._eventtypes,
                }
        except AuthException as auth_err:
            if not self._error:
                _LOGGER.warning("Error authenticating with HL API: %s", auth_err)
                self._error = True
            raise ConfigEntryAuthFailed from auth_err
        except ApiException as api_err:
            if not self._error:
                _LOGGER.warning("Error communicating with HL API: %s", api_err)
                self._error = True
            raise UpdateFailed(
                f"Error communicating with HL API: {api_err}"
            ) from api_err


    async def _async_get_core_data(self):
        properties = await self._hl_api.async_get_properties()
        devices = await self._hl_api.async_get_devices()
        insights = await self._hl_api.async_get_insights()
        coord_properties = {}
        for hl_property in properties:
            property_devices = {
                device.serialnumber: device
                for device in devices
                if device.rel.hl_property == hl_property.rel.self
            }
            gateway_key = next(
                (
                    device.serialnumber
                    for device in property_devices.values()
                    if device.modeltype == MODELTYPE_GATEWAY
                ),
                None,
            )
            property_insights = [
                insight
                for insight in insights
                if insight.rel.hl_property == hl_property.rel.self
            ]
            coord_properties[hl_property.reference] = {
                COORD_GATEWAY_KEY: gateway_key,
                COORD_PROPERTY: hl_property,
                COORD_DEVICES: property_devices,
                COORD_INSIGHTS: property_insights,
                COORD_ALERTS: await hl_property.async_get_alerts(),
            }

        return coord_properties

    async def _async_get_eventtypes_lookup(self):
        self._eventtypes = await self._hl_api.async_get_lookups(
            HOMELINK_LOOKUP_EVENTTYPE
        )

    def _get_previous_mqtt(self):
        return (
            self.hass.data[DOMAIN][self._entry.entry_id].data[COORD_DATA_MQTT]
            if (
                DOMAIN in self.hass.data
                and self._entry.entry_id in self.hass.data[DOMAIN]
                and COORD_DATA_MQTT in self.hass.data[DOMAIN][self._entry.entry_id].data
            )
            else None
        )

    async def _async_check_for_changes(self, coord_properties):
        if not self._known_properties:
            self._build_known_properties()

        known_properties = deepcopy(self._known_properties)
        self._check_for_deletes(known_properties, coord_properties)
        self._check_for_adds(known_properties, coord_properties)

    def _build_known_properties(self):
        devices = device_registry.async_entries_for_config_entry(
            self._dev_reg, self._entry.entry_id
        )
        for device in devices:
            if device.model == ATTR_PROPERTY.capitalize():
                children = {
                    list(device_child.identifiers)[0][2]: device_child.id
                    for device_child in devices
                    if device_child.via_device_id == device.id
                }
                self._known_properties[list(device.identifiers)[0][2]] = {
                    KNOWN_DEVICES_ID: device.id,
                    KNOWN_DEVICES_CHILDREN: children,
                }

    def _check_for_deletes(self, known_properties, coord_properties):
        for known_property, device_key in known_properties.items():
            if known_property not in coord_properties:
                for known_device, child_device in device_key[
                    KNOWN_DEVICES_CHILDREN
                ].items():
                    self._delete_device_and_entities(child_device)
                    self._known_properties[known_property][KNOWN_DEVICES_CHILDREN].pop(
                        known_device
                    )
                self._delete_device_and_entities(device_key[KNOWN_DEVICES_ID])
                self._known_properties.pop(known_property)
            else:
                coord_property = coord_properties[known_property]
                for known_device, child_device in device_key[
                    KNOWN_DEVICES_CHILDREN
                ].items():
                    if known_device in coord_property[COORD_DEVICES]:
                        continue

                    self._delete_device_and_entities(child_device)
                    self._known_properties[known_property][KNOWN_DEVICES_CHILDREN].pop(
                        known_device
                    )

    def _check_for_adds(self, known_properties, coord_properties):
        if not self._first_refresh:
            added = False
            for hl_property_key, hl_property in coord_properties.items():
                if hl_property_key not in known_properties:
                    dispatcher_send(self.hass, HOMELINK_ADD_PROPERTY, hl_property_key)
                    added = True
                else:
                    for device_key in hl_property[COORD_DEVICES]:
                        if (
                            device_key
                            not in self._known_properties[hl_property_key][
                                KNOWN_DEVICES_CHILDREN
                            ]
                        ):
                            dispatcher_send(
                                self.hass,
                                HOMELINK_ADD_DEVICE,
                                hl_property_key,
                                device_key,
                            )
                            added = True
            if added:
                self._known_properties = {}

        self._first_refresh = False

    def _delete_device_and_entities(self, device):
        entities = entity_registry.async_entries_for_device(self._ent_reg, device, True)
        for entity in entities:
            self._ent_reg.async_remove(entity.entity_id)
        self._dev_reg.async_remove_device(device)
