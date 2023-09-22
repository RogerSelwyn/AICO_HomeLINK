"""HomeLINK coordinators."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pyhomelink import HomeLINKApi
from pyhomelink.exceptions import ApiException, AuthException

from .const import COORD_ALERTS, COORD_DEVICES, COORD_PROPERTIES, COORD_PROPERTY

# from .testdata.test_data import get_test_data

_LOGGER = logging.getLogger(__name__)


class HomeLINKDataCoordinator(DataUpdateCoordinator):
    """HomeLINK Data object."""

    def __init__(self, hass: HomeAssistant, hl_api: HomeLINKApi) -> None:
        """Initialize HomeLINKDataCoordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="HomeLINK Data",
            update_interval=timedelta(seconds=30),
        )
        self._hl_api = hl_api
        self._count = 1

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
                    coord_properties[hl_property.reference] = {
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

                return {COORD_PROPERTIES: coord_properties}
        except AuthException as auth_err:
            raise ConfigEntryAuthFailed from auth_err
        except ApiException as api_err:
            raise UpdateFailed(
                f"Error communicating with HL API: {api_err}"
            ) from api_err
