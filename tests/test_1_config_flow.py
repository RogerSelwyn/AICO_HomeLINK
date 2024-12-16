"""Test the HomeLINK config flow."""

# Note that MQTT config setup is not tested as yet
from asyncio import TimeoutError
from unittest.mock import Mock, patch

from aiohttp import ClientConnectorError, ClientResponseError
import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.homelink.const import (
    CONF_INSIGHTS_ENABLE,
    CONF_MQTT_ENABLE,
    CONF_MQTT_HOMELINK,
    CONF_PROPERTIES,
    CONF_WEBHOOK_ENABLE,
    DOMAIN,
)
from homeassistant import config_entries
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import HomelinkMockConfigEntry
from .helpers.const import CLIENT_ID, CLIENT_SECRET, TOKEN
from .helpers.utils import create_mock, mock_token_call


async def test_config_flow_no_credentials(hass: HomeAssistant) -> None:
    """Test config flow base case with no credentials registered."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "missing_credentials"


async def test_config_flow_api_errors(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,  # pylint: disable=unused-argument
) -> None:
    """Check for api_error handling."""

    mock_token_call(aioclient_mock, TOKEN)

    with (
        patch(
            "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation.async_resolve_external_data",
            side_effect=ClientResponseError(None, None, status=401),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "oauth_error"

    with (
        patch(
            "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation.async_resolve_external_data",
            side_effect=ClientResponseError(None, None, status=500),
        ),
        pytest.raises(ClientResponseError),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    with patch(
        "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation.async_resolve_external_data",
        side_effect=ClientConnectorError(Mock(), OSError()),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "cannot_connect"

    with patch(
        "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation.async_resolve_external_data",
        side_effect=TimeoutError(OSError()),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "timeout_connect"

    with patch(
        "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation.async_resolve_external_data",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "oauth_error"

    with patch(
        "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation.async_resolve_external_data",
        return_value={"expires_in": "1.2"},
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "oauth_error"


@pytest.mark.usefixtures("current_request_with_host")
async def test_full_flow(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,  # pylint: disable=unused-argument
) -> None:
    """Check full flow."""

    mock_token_call(aioclient_mock, TOKEN)

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
    setup_credentials: None,  # pylint: disable=unused-argument
) -> None:
    """Check for second installation of integration."""

    mock_token_call(aioclient_mock, TOKEN)

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
    base_config_entry: HomelinkMockConfigEntry,
    setup_base_integration: None,
) -> None:
    """Test reauth an existing profile reauthenticates the config entry."""

    mock_token_call(aioclient_mock, TOKEN)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": base_config_entry.entry_id,
        },
        data=base_config_entry.data,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={"confirm": True}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "oauth_error"


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow_default(
    hass: HomeAssistant,
    base_config_entry: HomelinkMockConfigEntry,
    setup_base_integration: None,
) -> None:
    """Test options flow."""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = result["data_schema"].schema
    assert _get_schema_default(schema, CONF_INSIGHTS_ENABLE) is False
    assert _get_schema_default(schema, CONF_MQTT_ENABLE) is False
    assert _get_schema_default(schema, CONF_MQTT_HOMELINK) is True
    assert _get_schema_default(schema, CONF_WEBHOOK_ENABLE) is False

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_INSIGHTS_ENABLE: False,
            CONF_MQTT_HOMELINK: False,
            CONF_WEBHOOK_ENABLE: False,
        },
    )
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert "result" in result
    assert result["result"] is True
    assert result["data"]["webhook_id"] is None
    assert result["data"][CONF_PROPERTIES] == {"DUMMY_USER_My_House": True}
    assert result["data"][CONF_INSIGHTS_ENABLE] is False
    assert result["data"][CONF_MQTT_ENABLE] is False
    assert result["data"][CONF_MQTT_HOMELINK] is False
    assert result["data"][CONF_WEBHOOK_ENABLE] is False


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow_webhooks_insights(
    hass: HomeAssistant,
    base_config_entry: HomelinkMockConfigEntry,
    setup_base_integration: None,
) -> None:
    """Test options flow with webhooks and insights."""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
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
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert "result" in result
    assert result["result"] is True
    assert result["data"]["webhook_id"] is not None
    assert result["data"][CONF_INSIGHTS_ENABLE] is True
    assert result["data"][CONF_WEBHOOK_ENABLE] is True


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow_webhooks_no_external_utl(
    hass: HomeAssistant,
    base_config_entry: HomelinkMockConfigEntry,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
) -> None:
    """Test options flow for no external url for webhooks."""

    create_mock(aioclient_mock, "/property", "base/property.json")
    base_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(base_config_entry.entry_id)

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_INSIGHTS_ENABLE: False,
            CONF_MQTT_HOMELINK: False,
            CONF_WEBHOOK_ENABLE: True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "errors" in result
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "no_external_url"


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow_no_properties(
    hass: HomeAssistant,
    base_config_entry: HomelinkMockConfigEntry,
    setup_base_integration: None,
) -> None:
    """Test options flow with webhooks and insights."""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_PROPERTIES: [],
            CONF_INSIGHTS_ENABLE: False,
            CONF_MQTT_HOMELINK: False,
            CONF_WEBHOOK_ENABLE: False,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "errors" in result
    assert "properties" in result["errors"]
    assert result["errors"]["properties"] == "must_select_one"


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow_removed_property(
    hass: HomeAssistant,
    base_config_entry: HomelinkMockConfigEntry,
    setup_base_integration: None,
) -> None:
    """Test options flow with webhooks and insights."""

    hass.config_entries.async_update_entry(
        base_config_entry,
        options={
            CONF_PROPERTIES: {
                "DUMMY_USER_Removed_Property": True,
                "DUMMY_USER_My_House": True,
            },
        },
    )
    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_PROPERTIES: ["DUMMY_USER_My_House"],
            CONF_INSIGHTS_ENABLE: False,
            CONF_MQTT_HOMELINK: False,
            CONF_WEBHOOK_ENABLE: False,
        },
    )
    assert result["data"][CONF_PROPERTIES] == {"DUMMY_USER_My_House": True}


@pytest.mark.usefixtures("current_request_with_host")
async def test_options_flow_auth_error(
    hass: HomeAssistant,
    base_config_entry: HomelinkMockConfigEntry,
    setup_base_integration: None,
) -> None:
    """Test options flow with webhooks and insights."""

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientResponseError(
                None,
                None,
                status=401,
            ),
        ),
    ):
        result = await hass.config_entries.options.async_init(
            base_config_entry.entry_id
        )
    assert result["type"] is FlowResultType.ABORT
    assert result.get("reason") == "invalid_application_credentials"

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientResponseError(
                None,
                None,
                status=500,
            ),
        ),
    ):
        result = await hass.config_entries.options.async_init(
            base_config_entry.entry_id
        )
    assert result["type"] is FlowResultType.ABORT
    assert result.get("reason") == "error_authenticating"

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientConnectorError(Mock(), OSError()),
        ),
    ):
        result = await hass.config_entries.options.async_init(
            base_config_entry.entry_id
        )
    assert result["type"] is FlowResultType.ABORT
    assert result.get("reason") == "error_authenticating"


def _get_schema_default(schema, key_name):
    """Iterate schema to find a key."""
    for schema_key in schema:
        if schema_key == key_name:
            return schema_key.default()
    raise KeyError(f"{key_name} not found in schema")
