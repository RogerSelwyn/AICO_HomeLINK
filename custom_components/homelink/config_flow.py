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
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.selector import BooleanSelector, TextSelector

from .const import (
    CONF_ERROR_TOPIC,
    CONF_EVENT_ENABLE,
    CONF_MQTT_CLIENT_ID,
    CONF_MQTT_ENABLE,
    CONF_MQTT_HOMELINK,
    CONF_MQTT_TOPIC,
    DOMAIN,
)
from .helpers.mqtt import HomeLINKMQTT

OAUTH_TOKEN_TIMEOUT_SEC = 30
BOOLEAN_SELECTOR = BooleanSelector()
TEXT_SELECTOR = TextSelector()

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
        options = config_entry.options
        self._mqtt_enable = options.get(CONF_MQTT_ENABLE, False)
        self._event_enable = options.get(CONF_EVENT_ENABLE, False)
        self._mqtt_topic = options.get(CONF_MQTT_TOPIC, "landlord_name")
        self._mqtt_homelink = options.get(CONF_MQTT_HOMELINK, True)
        self._mqtt_client_id = options.get(CONF_MQTT_CLIENT_ID, "")
        self._mqtt_username = options.get(CONF_USERNAME, "")
        self._mqtt_password = options.get(CONF_PASSWORD, "")

    async def async_step_init(
        self, user_input=None  # pylint: disable=unused-argument
    ) -> FlowResult:
        """Set up the option flow."""

        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._mqtt_enable = user_input.get(CONF_MQTT_ENABLE)
            self._mqtt_homelink = user_input.get(CONF_MQTT_HOMELINK)

            if self._mqtt_enable:
                if self._mqtt_homelink:
                    return await self.async_step_homelink_mqtt()
                return await self.async_step_ha_mqtt()

            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MQTT_ENABLE,
                        default=self._mqtt_enable,
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_MQTT_HOMELINK,
                        default=self._mqtt_homelink,
                    ): BOOLEAN_SELECTOR,
                }
            ),
            last_step=False,
        )

    async def async_step_ha_mqtt(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._mqtt_topic = _remove_suffixes(user_input.get(CONF_MQTT_TOPIC))
            self._event_enable = user_input.get(CONF_EVENT_ENABLE)
            user_input[CONF_MQTT_TOPIC] = self._mqtt_topic

            base_input = self._fake_base_input()
            combined_input = {**user_input, **base_input}
            return self.async_create_entry(title="", data=combined_input)

        return self.async_show_form(
            step_id="ha_mqtt",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MQTT_TOPIC,
                        description={
                            "suggested_value": _add_suffixes(self._mqtt_topic)
                        },
                    ): TEXT_SELECTOR,
                    vol.Optional(
                        CONF_EVENT_ENABLE,
                        default=self._event_enable,
                    ): BOOLEAN_SELECTOR,
                }
            ),
            last_step=False,
        )

    async def async_step_homelink_mqtt(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self._event_enable = user_input.get(CONF_EVENT_ENABLE)
            self._mqtt_client_id = user_input.get(CONF_MQTT_CLIENT_ID)
            self._mqtt_username = user_input.get(CONF_USERNAME)
            self._mqtt_password = user_input.get(CONF_PASSWORD)
            self._mqtt_topic = _remove_suffixes(user_input.get(CONF_MQTT_TOPIC))
            user_input[CONF_MQTT_TOPIC] = self._mqtt_topic

            base_input = self._fake_base_input()
            combined_input = {**user_input, **base_input}
            errors = await self._async_test_connection(combined_input)
            if not errors:
                return self.async_create_entry(title="", data=combined_input)

        return self.async_show_form(
            step_id="homelink_mqtt",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MQTT_CLIENT_ID,
                        description={"suggested_value": self._mqtt_client_id},
                    ): TEXT_SELECTOR,
                    vol.Required(
                        CONF_USERNAME,
                        description={"suggested_value": self._mqtt_username},
                    ): TEXT_SELECTOR,
                    vol.Required(
                        CONF_PASSWORD,
                        description={"suggested_value": self._mqtt_password},
                    ): str,
                    vol.Required(
                        CONF_MQTT_TOPIC,
                        description={
                            "suggested_value": _add_suffixes(self._mqtt_topic)
                        },
                    ): TEXT_SELECTOR,
                    vol.Optional(
                        CONF_EVENT_ENABLE,
                        default=self._event_enable,
                    ): BOOLEAN_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def _async_test_connection(self, options):
        hl_mqtt = HomeLINKMQTT(self.hass, options)

        if ret := await hl_mqtt.async_try_connect():
            return (
                {"base": ret}
                if ret != CONF_ERROR_TOPIC
                else {CONF_MQTT_TOPIC: CONF_ERROR_TOPIC}
            )
        return {}

    def _fake_base_input(self):
        return {
            CONF_MQTT_ENABLE: self._mqtt_enable,
            CONF_MQTT_HOMELINK: self._mqtt_homelink,
        }


def _remove_suffixes(topic):
    return topic.removesuffix("#").removesuffix("/") if topic else None


def _add_suffixes(topic):
    return f"{topic}/#" if topic else None
