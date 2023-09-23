"""Config flow for HomeLINK integration."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Mapping
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import CONF_MQTT_ENABLE, CONF_MQTT_TOPIC, DOMAIN

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

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create an entry for auth."""
        if self._reauth_config_entry:
            return self.async_abort(reason="oauth_error")
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

    async def async_oauth_create_entry(self, data: dict) -> FlowResult:
        """Create an entry for HomeLINK ."""
        existing_entry = await self.async_set_unique_id(DOMAIN)
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        return await super().async_oauth_create_entry(data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """HomeLINK options callback."""
        return HomeLINKOptionsFlowHandler(config_entry)


class HomeLINKOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for HomeLINK."""

    def __init__(self, config_entry):
        """Initialize HomeLINK options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Set up the option flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MQTT_ENABLE,
                        default=self.config_entry.options.get(CONF_MQTT_ENABLE, False),
                    ): bool,
                    vol.Optional(
                        CONF_MQTT_TOPIC,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_MQTT_TOPIC, ""
                            )
                        },
                    ): str,
                }
            ),
        )
