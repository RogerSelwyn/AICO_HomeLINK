"""Config flow for HomeLINK integration."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Mapping
from copy import deepcopy
from typing import Any, Self

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_WEBHOOK_ID
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.helpers.selector import BooleanSelector, TextSelector

from pyhomelink.api import HomeLINKApi

from .const import (
    ATTR_EXTERNAL_URL,
    CONF_ERROR_AUTHENTICATING,
    CONF_ERROR_TOPIC,
    CONF_EVENT_ENABLE,
    CONF_INSIGHTS_ENABLE,
    CONF_INVALID_APPLICATION_CREDENTIALS,
    CONF_MQTT_CLIENT_ID,
    CONF_MQTT_ENABLE,
    CONF_MQTT_HOMELINK,
    CONF_MQTT_TOPIC,
    CONF_PROPERTIES,
    CONF_WEBHOOK_ENABLE,
    DOMAIN,
)
from .helpers.api import AsyncConfigEntryAuth
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
    VERSION = 2
    MINOR_VERSION = 0

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
    ) -> ConfigFlowResult:
        """Create an entry for auth."""

        # HomeLINK service does not support scope authentication, client id/secret
        # is a pseudo userid/password that provides an expiring access token.
        # So there is no re-auth possible.
        if self._reauth_config_entry:
            return self.async_abort(reason="oauth_error")

        # Retrieve a token is possible, check it is valid and set expires_at as needed
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
        except aiohttp.client_exceptions.ClientConnectorError:
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
        self,
        entry_data: Mapping[str, Any],  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""

        # No (re-)auth is provide by HomeLINK (see not earlier)
        # This process guides user to delete and re-add the integration.
        # Unless they know how to hack the application credentials with a new
        # client id/secret

        self._reauth_config_entry = self._get_reauth_entry()
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth dialog."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> ConfigFlowResult:
        """Create an entry for HomeLINK ."""
        existing_entry = await self.async_set_unique_id(DOMAIN)
        if existing_entry:
            return self.async_update_reload_and_abort(
                existing_entry, data_updates=data, unique_id=self.unique_id
            )

        return await super().async_oauth_create_entry(data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """HomeLINK options callback."""
        return HomeLINKOptionsFlowHandler(config_entry)

    def is_matching(self, other_flow: Self) -> bool:
        """Return True if other_flow is matching this flow."""
        return False


class HomeLINKOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for HomeLINK."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize HomeLINK options flow."""
        options = config_entry.options
        self._properties = options.get(CONF_PROPERTIES, {})
        self._mqtt_enable = options.get(CONF_MQTT_ENABLE, False)
        self._webhook_enable = options.get(CONF_WEBHOOK_ENABLE, False)
        self._event_enable = options.get(CONF_EVENT_ENABLE, False)
        self._insights_enable = options.get(CONF_INSIGHTS_ENABLE, False)
        self._mqtt_topic = options.get(CONF_MQTT_TOPIC, "landlord_name")
        self._mqtt_homelink = options.get(CONF_MQTT_HOMELINK, True)
        self._mqtt_client_id = options.get(CONF_MQTT_CLIENT_ID, "")
        self._mqtt_username = options.get(CONF_USERNAME, "")
        self._mqtt_password = options.get(CONF_PASSWORD, "")
        self._webhook_id = options.get(CONF_WEBHOOK_ID, None)
        self._user_input: dict[str, Any] | None = None
        self._webhook_displayed = False
        self._property_list: list[str] = []

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Set up the option flow."""
        self._property_list = await self._async_get_properties()

        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        # sourcery skip: last-if-guard
        """Handle a flow initialized by the user."""

        # Need at least one property selected
        # If MQTT enabled then show MQTT form or HomeLINK form
        # If Webhooks enabled then show Webhooks form (which provide the webhook url)
        errors = {}
        if user_input is not None:
            stored_properties = deepcopy(user_input.get(CONF_PROPERTIES))
            self._user_input = user_input
            self._properties = {}
            conf_properties: Any = user_input.get(CONF_PROPERTIES)
            for hl_property in self._property_list:
                self._properties[hl_property] = hl_property in conf_properties
            self._user_input[CONF_PROPERTIES] = self._properties

            self._insights_enable = user_input.get(CONF_INSIGHTS_ENABLE)
            self._mqtt_enable = user_input.get(CONF_MQTT_ENABLE)
            self._webhook_enable = user_input.get(CONF_WEBHOOK_ENABLE)
            self._mqtt_homelink = user_input.get(CONF_MQTT_HOMELINK)

            if len(stored_properties) == 0:  # type: ignore[arg-type]
                errors[CONF_PROPERTIES] = "must_select_one"

            if not self._webhook_enable:
                user_input[CONF_WEBHOOK_ID] = None
            else:
                try:
                    get_url(self.hass, allow_internal=False)
                except NoURLAvailableError:
                    errors["base"] = "no_external_url"
            if not errors:
                if self._mqtt_enable:
                    if self._mqtt_homelink:
                        return await self.async_step_homelink_mqtt()
                    return await self.async_step_ha_mqtt()
                if self._webhook_enable:
                    return await self.async_step_homelink_webhook()

                return self.async_create_entry(title="", data=user_input)

        display_properties = [
            hl_property
            for hl_property, value in self._properties.items()
            if value is True
        ]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PROPERTIES,
                        default=display_properties,
                    ): cv.multi_select(self._property_list),
                    vol.Optional(
                        CONF_INSIGHTS_ENABLE,
                        default=self._insights_enable,
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_MQTT_ENABLE,
                        default=self._mqtt_enable,
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_MQTT_HOMELINK,
                        default=self._mqtt_homelink,
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_WEBHOOK_ENABLE,
                        default=self._webhook_enable,
                    ): BOOLEAN_SELECTOR,
                }
            ),
            last_step=False,
            errors=errors,
        )

    async def _async_get_properties(self) -> list[str]:
        # Perform authentication and fail if not possible
        # Then retrieve the property list
        implementation = (
            await config_entry_oauth2_flow.async_get_config_entry_implementation(
                self.hass, self.config_entry
            )
        )
        session = config_entry_oauth2_flow.OAuth2Session(
            self.hass, self.config_entry, implementation
        )
        try:
            await session.async_ensure_token_valid()
        except aiohttp.client_exceptions.ClientResponseError as err:
            if err.status == 401:
                errmsg = CONF_INVALID_APPLICATION_CREDENTIALS

            else:
                errmsg = CONF_ERROR_AUTHENTICATING
            _LOGGER.error(errmsg)
            raise AbortFlow(errmsg) from err

        except aiohttp.client_exceptions.ClientConnectorError as err:
            errmsg = CONF_ERROR_AUTHENTICATING
            _LOGGER.error(errmsg)
            raise AbortFlow(errmsg) from err

        hl_api = HomeLINKApi(
            AsyncConfigEntryAuth(
                aiohttp_client.async_get_clientsession(self.hass), session
            )
        )
        properties = await hl_api.async_get_properties()
        property_list = [hl_property.reference for hl_property in properties]
        for hl_property in property_list:
            if hl_property not in self._properties:
                self._properties[hl_property] = True

        working_properties = dict(self._properties)
        for hl_property in working_properties:
            if hl_property not in property_list:
                del self._properties[hl_property]
        return property_list

    async def async_step_ha_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle HA MQTT setup."""
        # Once mqtt form processed, if webhooks enabled, show that form
        if user_input is not None:
            self._mqtt_topic = _remove_suffixes(user_input.get(CONF_MQTT_TOPIC))
            self._event_enable = user_input.get(CONF_EVENT_ENABLE)
            user_input[CONF_MQTT_TOPIC] = self._mqtt_topic

            self._user_input = {**user_input, **self._user_input}  # type: ignore[dict-item]
            if self._webhook_enable:
                return await self.async_step_homelink_webhook()
            return self.async_create_entry(title="", data=self._user_input)

        last_step = not self._webhook_enable
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
            last_step=last_step,
        )

    async def async_step_homelink_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle HomeLINK MQTT setup."""
        # Once mqtt form processed, test the connection then if webhooks enabled, show that form
        errors = {}
        if user_input is not None:
            self._event_enable = user_input.get(CONF_EVENT_ENABLE)
            self._mqtt_client_id = user_input.get(CONF_MQTT_CLIENT_ID)
            self._mqtt_username = user_input.get(CONF_USERNAME)
            self._mqtt_password = user_input.get(CONF_PASSWORD)
            self._mqtt_topic = _remove_suffixes(user_input.get(CONF_MQTT_TOPIC))
            user_input[CONF_MQTT_TOPIC] = self._mqtt_topic

            self._user_input = {**user_input, **self._user_input}  # type: ignore[dict-item]
            errors = await self._async_test_connection()
            if not errors:
                if self._webhook_enable:
                    return await self.async_step_homelink_webhook()
                return self.async_create_entry(title="", data=self._user_input)

        last_step = not self._webhook_enable
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
            last_step=last_step,
        )

    async def async_step_homelink_webhook(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle HomeLINK MQTT setup."""
        # This form just shows the webhook url that the user must use on the HomeLINK dashboard
        if not self._webhook_id:
            self._webhook_id = webhook.async_generate_id()
        user_input = {CONF_WEBHOOK_ID: self._webhook_id}

        if not self._webhook_displayed:
            external_url = get_url(self.hass, allow_internal=False)
            self._webhook_displayed = True
            return self.async_show_form(
                step_id="homelink_webhook",
                description_placeholders={
                    CONF_WEBHOOK_ID: self._webhook_id,
                    ATTR_EXTERNAL_URL: external_url,
                },
            )
        self._user_input = {**user_input, **self._user_input}  # type: ignore[dict-item]
        return self.async_create_entry(title="", data=self._user_input)

    async def _async_test_connection(self) -> dict:
        hl_mqtt = HomeLINKMQTT(self.hass, self._user_input)

        if ret := await hl_mqtt.async_try_connect():
            return (
                {"base": ret}
                if ret != CONF_ERROR_TOPIC
                else {CONF_MQTT_TOPIC: CONF_ERROR_TOPIC}
            )
        return {}


def _remove_suffixes(topic):
    return topic.removesuffix("#").removesuffix("/") if topic else None


def _add_suffixes(topic):
    return f"{topic}/#" if topic else None
