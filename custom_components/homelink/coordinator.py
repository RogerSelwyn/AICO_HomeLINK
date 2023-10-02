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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pyhomelink import HomeLINKApi
from pyhomelink.exceptions import ApiException, AuthException

from .const import COORD_DEVICES  # DOMAIN,
from .const import (
    ATTR_PROPERTY,
    COORD_ALERTS,
    COORD_GATEWAY_KEY,
    COORD_PROPERTIES,
    COORD_PROPERTY,
    HOMELINK_ADD_DEVICE,
    HOMELINK_ADD_PROPERTY,
    KNOWN_DEVICES_CHILDREN,
    KNOWN_DEVICES_ID,
    MODELTYPE_GATEWAY,
)

# from .testdata.test_data import get_test_data

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
        self._count = 1
        self._entry = entry
        self._known_properties = {}
        self._ent_reg = entity_registry.async_get(hass)
        self._dev_reg = device_registry.async_get(hass)
        self._first_refresh = True

    async def _async_update_data(self):
        """Fetch data from API endpoint."""

        try:
            async with asyncio.timeout(10):
                properties = await self._hl_api.async_get_properties()
                devices = await self._hl_api.async_get_devices()
                coord_properties = {}
                for hl_property in properties:
                    coord_devices = [
                        device
                        for device in devices
                        if device.rel.hl_property == hl_property.rel.self
                    ]
                    gateway_key = next(
                        (
                            device.serialnumber
                            for device in devices
                            if device.modeltype == MODELTYPE_GATEWAY
                        ),
                        None,
                    )
                    coord_properties[hl_property.reference] = {
                        COORD_GATEWAY_KEY: gateway_key,
                        COORD_PROPERTY: hl_property,
                        COORD_DEVICES: {
                            device.serialnumber: device for device in coord_devices
                        },
                        COORD_ALERTS: await hl_property.async_get_alerts(),
                    }
                    # ##### Must be removed
                    # coord_properties = get_test_data(self.hass, self._count)
                    # self._count += 1
                    # ##### Must be removed

                await self._async_check_for_changes(coord_properties)
                return {COORD_PROPERTIES: coord_properties}
        except AuthException as auth_err:
            raise ConfigEntryAuthFailed from auth_err
        except ApiException as api_err:
            raise UpdateFailed(
                f"Error communicating with HL API: {api_err}"
            ) from api_err

    async def _async_check_for_changes(self, coord_properties):
        if not self._known_properties:
            self._build_known_properties()

        known_properties = deepcopy(self._known_properties)

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

    def _delete_device_and_entities(self, device):
        entities = entity_registry.async_entries_for_device(self._ent_reg, device, True)
        for entity in entities:
            self._ent_reg.async_remove(entity.entity_id)
        self._dev_reg.async_remove_device(device)
