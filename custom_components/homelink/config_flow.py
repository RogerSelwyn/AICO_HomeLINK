"""Config flow for HomeLINK integration."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Mapping
from typing import Any

import aiohttp
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

OAUTH_TOKEN_TIMEOUT_SEC = 30

_LOGGER = logging.getLogger(__name__)


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Google Calendars OAuth2 authentication."""

    DOMAIN = DOMAIN

    def __init__(self) -> None:
        """Set up instance."""
        super().__init__()
        self._reauth_config_entry: config_entries.ConfigEntry | None = None
        # self._device_flow: DeviceFlow | None = None

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create an entry for auth."""
        _LOGGER.debug("Creating config entry from external data")
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        try:
            async with asyncio.timeout(OAUTH_TOKEN_TIMEOUT_SEC):
                token = await self.flow_impl.async_resolve_external_data(
                    self.external_data
                )
            if not token:
                _LOGGER.error("Error authenticating: %s", "token")
                return self.async_abort(reason="oauth_error")
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout resolving OAuth token: %s", err)
            return self.async_abort(reason="timeout_connect")
        except aiohttp.client_exceptions.ClientResponseError as err:
            if err.status == 401:
                return self.async_abort(reason="oauth_error")
            raise
        except aiohttp.client_exceptions.ClientConnectorError as err:
            return self.async_abort(reason="cannot_connect")

        # Force int for non-compliant oauth2 providers
        try:
            token["expires_in"] = int(token["expires_in"])
        except ValueError as err:
            _LOGGER.warning("Error converting expires_in to int: %s", err)
            return self.async_abort(reason="oauth_error")
        token["expires_at"] = time.time() + token["expires_in"]

        self.logger.info("Successfully authenticated")

        return await self.async_oauth_create_entry(
            {"auth_implementation": self.flow_impl.domain, "token": token}
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]  # pylint: disable=unused-argument
    ) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        self._reauth_config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm reauth dialog."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()
