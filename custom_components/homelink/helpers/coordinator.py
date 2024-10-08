"""HomeLINK coordinators."""

import asyncio
import logging
from copy import deepcopy
from datetime import date, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyhomelink import HomeLINKApi
from pyhomelink.exceptions import ApiException, AuthException

from ..const import (
    ATTR_ALARM,
    ATTR_PROPERTY,
    ATTR_READINGS,
    CONF_INSIGHTS_ENABLE,
    COORD_ALERTS,
    COORD_CONFIG_ENTRY_OPTIONS,
    COORD_DEVICES,
    COORD_GATEWAY_KEY,
    COORD_INSIGHTS,
    COORD_LOOKUP_EVENTTYPE,
    COORD_PROPERTIES,
    COORD_PROPERTY,
    COORD_READINGS,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    HOMELINK_LOOKUP_EVENTTYPE,
    KNOWN_DEVICES_CHILDREN,
    KNOWN_DEVICES_DEVICEID,
    KNOWN_DEVICES_ID,
    KNOWN_DEVICES_MODEL,
    MODELTYPE_GATEWAY,
    RETRIEVAL_INTERVAL_READINGS,
)
from .utils import include_property

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
        self._hass = hass
        self._hl_api = hl_api
        self._entry = entry
        self._known_properties = {}
        self._dev_reg = device_registry.async_get(hass)
        self._first_refresh = True
        self._eventtypes = []
        self._error = False
        self._throttle = datetime.now() - RETRIEVAL_INTERVAL_READINGS

    async def _async_setup(self) -> None:
        await self._async_get_eventtypes_lookup()

    async def _async_update_data(self):
        """Fetch data from API endpoint."""

        try:
            async with asyncio.timeout(10):
                coord_properties = await self._async_get_core_data()

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

        await self._async_check_for_changes(coord_properties)
        config_entry = self._entry.options

        self._error = False
        return {
            COORD_PROPERTIES: coord_properties,
            COORD_LOOKUP_EVENTTYPE: self._eventtypes,
            COORD_CONFIG_ENTRY_OPTIONS: config_entry,
        }

    async def _async_get_core_data(self):
        properties = await self._hl_api.async_get_properties()
        devices = await self._hl_api.async_get_devices()
        insights = (
            await self._hl_api.async_get_insights()
            if self._entry.options.get(CONF_INSIGHTS_ENABLE)
            else []
        )
        coord_properties = {}
        for hl_property in properties:
            if not include_property(self._entry.options, hl_property.reference):
                continue
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

            readings = []
            if datetime.now() >= self._throttle + RETRIEVAL_INTERVAL_READINGS:
                readings = await self._async_retrieve_readings(
                    hl_property, property_devices
                )
            coord_properties[hl_property.reference][COORD_READINGS] = readings
        return coord_properties

    async def _async_retrieve_readings(self, hl_property, property_devices):
        readings = []
        self._throttle = datetime.now()
        for device in property_devices.values():
            if hasattr(device.rel, ATTR_READINGS):
                readings = await hl_property.async_get_readings(date.today())
                break
        return readings

    async def _async_get_eventtypes_lookup(self):
        self._eventtypes = await self._hl_api.async_get_lookups(
            HOMELINK_LOOKUP_EVENTTYPE
        )

    async def _async_check_for_changes(self, coord_properties):
        if not self._known_properties:
            self._build_known_properties()

        known_properties = deepcopy(self._known_properties)
        await self._async_check_for_deletes(known_properties, coord_properties)
        self._check_for_adds(known_properties, coord_properties)

    def _build_known_properties(self):
        devices = device_registry.async_entries_for_config_entry(
            self._dev_reg, self._entry.entry_id
        )
        for device in devices:
            if device.model == ATTR_PROPERTY.capitalize():
                children = {
                    list(device_child.identifiers)[0][2]: {
                        KNOWN_DEVICES_DEVICEID: device_child.id,
                        KNOWN_DEVICES_MODEL: device_child.model,
                    }
                    for device_child in devices
                    if device_child.via_device_id == device.id
                }
                self._known_properties[list(device.identifiers)[0][2]] = {
                    KNOWN_DEVICES_ID: device.id,
                    KNOWN_DEVICES_CHILDREN: children,
                }

    async def _async_check_for_deletes(self, known_properties, coord_properties):
        for known_property, device_key in known_properties.items():
            if known_property not in coord_properties:
                for known_device, child_device in device_key[
                    KNOWN_DEVICES_CHILDREN
                ].items():
                    await self._async_delete_device_and_entities(
                        child_device[KNOWN_DEVICES_DEVICEID]
                    )
                    self._known_properties[known_property][KNOWN_DEVICES_CHILDREN].pop(
                        known_device
                    )
                await self._async_delete_device_and_entities(
                    device_key[KNOWN_DEVICES_ID]
                )
                self._known_properties.pop(known_property)
            else:
                coord_property = coord_properties[known_property]
                for known_device, child_device in device_key[
                    KNOWN_DEVICES_CHILDREN
                ].items():
                    if (
                        known_device in coord_property[COORD_DEVICES]
                        or child_device[KNOWN_DEVICES_MODEL].lower() == ATTR_ALARM
                    ):
                        continue

                    await self._async_delete_device_and_entities(
                        child_device[KNOWN_DEVICES_DEVICEID]
                    )
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
                    for device_key, device in hl_property[COORD_DEVICES].items():
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
                                device,
                                hl_property[COORD_GATEWAY_KEY],
                            )
                            added = True
            if added:
                self._known_properties = {}

        self._first_refresh = False

    async def _async_delete_device_and_entities(self, device):
        ent_reg = entity_registry.async_get(self._hass)
        entities = entity_registry.async_entries_for_device(ent_reg, device, True)
        for entity in entities:
            ent_reg.async_remove(entity.entity_id)
        self._dev_reg.async_remove_device(device)
