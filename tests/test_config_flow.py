"""Test the HomeLINK config flow.""" 
# Note that MQTT config is not tested

import pytest
from homeassistant import config_entries
from homeassistant.components.application_credentials import (
    ClientCredential, async_import_client_credential)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import \
    AiohttpClientMocker

from custom_components.homelink.const import (CONF_INSIGHTS_ENABLE,
                                              CONF_MQTT_ENABLE,
                                              CONF_MQTT_HOMELINK,
                                              CONF_WEBHOOK_ENABLE, DOMAIN)

from . import setup_integration
from .conftest import BASE_AUTH_URL, CLIENT_ID, CLIENT_SECRET, TOKEN

pytestmark = pytest.mark.usefixtures("mock_setup_entry")

async def test_config_flow_no_credentials(hass: HomeAssistant) -> None:
    """Test config flow base case with no credentials registered."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "missing_credentials"

async def test_config_flow_invalid_credentials(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None, # pylint: disable=unused-argument
) -> None:
    """Check for invalid credentials."""

    aioclient_mock.get(
        f"{BASE_AUTH_URL}/oauth2?client={CLIENT_ID}&secret={CLIENT_SECRET}",
        json=None,status=401
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "oauth_error"


@pytest.mark.usefixtures("current_request_with_host")
async def test_full_flow(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None, # pylint: disable=unused-argument
) -> None:
    """Check full flow."""

    aioclient_mock.get(
        f"{BASE_AUTH_URL}/oauth2?client={CLIENT_ID}&secret={CLIENT_SECRET}",
        json={'accessToken': TOKEN},
    )

    await async_import_client_credential(
        hass, DOMAIN, ClientCredential(CLIENT_ID, CLIENT_SECRET)
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert "result" in result
    assert result["result"].unique_id == DOMAIN
    assert "token" in result["result"].data
    assert result["result"].data["token"]["access_token"] == TOKEN
    assert result["result"].data["token"]["refresh_token"] is None

async def test_config_flow_second_instance(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None, # pylint: disable=unused-argument
) -> None:
    """Check for second installation of integration."""

    aioclient_mock.get(
        f"{BASE_AUTH_URL}/oauth2?client={CLIENT_ID}&secret={CLIENT_SECRET}",
        json={'accessToken': TOKEN},
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "single_instance_allowed"

@pytest.mark.usefixtures("current_request_with_host")
async def test_reauth(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    polling_config_entry: MockConfigEntry,
    setup_credentials: None, # pylint: disable=unused-argument
) -> None:
    """Test reauth an existing profile reauthenticates the config entry.""" 

    aioclient_mock.get(
        f"{BASE_AUTH_URL}/oauth2?client={CLIENT_ID}&secret={CLIENT_SECRET}",
        json={'accessToken': TOKEN},
    )

    await setup_integration(hass, polling_config_entry)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": polling_config_entry.entry_id,
        },
        data=polling_config_entry.data,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={"confirm": True}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow(
    hass: HomeAssistant,
    polling_config_entry: MockConfigEntry,
    setup_credentials: None, # pylint: disable=unused-argument
) -> None:
    """Test options config flow for a V1 bridge."""
    await setup_integration(hass, polling_config_entry)

    # polling_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(polling_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = result["data_schema"].schema
    assert (
        _get_schema_default(schema, CONF_INSIGHTS_ENABLE)
        is False
    )
    assert (
        _get_schema_default(schema, CONF_MQTT_ENABLE)
        is False
    )
    assert (
        _get_schema_default(schema, CONF_MQTT_HOMELINK)
        is True
    )
    assert (
        _get_schema_default(schema, CONF_WEBHOOK_ENABLE)
        is False
    )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_INSIGHTS_ENABLE: True,
            CONF_MQTT_HOMELINK: False,
            CONF_WEBHOOK_ENABLE: True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "homelink_webhook"
    assert "description_placeholders" in result
    assert "webhook_id" in result["description_placeholders"]
    assert result["description_placeholders"]["webhook_id"] is not None

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=None,
    )
    print("****************************>", result)
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert "result" in result
    assert result["result"] is True
    assert result["data"]["webhook_id"] is not None
    assert result["data"][CONF_INSIGHTS_ENABLE] is True
    assert result["data"][CONF_MQTT_ENABLE] is False
    assert result["data"][CONF_MQTT_HOMELINK] is False
    assert result["data"][CONF_WEBHOOK_ENABLE] is True




def _get_schema_default(schema, key_name):
    """Iterate schema to find a key."""
    for schema_key in schema:
        if schema_key == key_name:
            return schema_key.default()
    raise KeyError(f"{key_name} not found in schema")
