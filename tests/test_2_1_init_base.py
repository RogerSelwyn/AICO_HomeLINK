"""Test setup process."""

from copy import deepcopy
from unittest.mock import Mock, patch

from aiohttp import ClientConnectorError, ClientResponseError, ClientSession
import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.homelink import async_setup_entry
from custom_components.homelink.helpers import api
from homeassistant.config import async_process_ha_core_config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.setup import async_setup_component

from .conftest import HomelinkMockConfigEntry, standard_mocks
from .helpers.const import DOMAIN, EXTERNAL_URL, REFRESH_CONFIG_ENTRY, TITLE, TOKEN_URL
from .helpers.utils import check_entity_state, mock_token_call


async def test_setup_errors(
    hass: HomeAssistant,
    setup_credentials: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test for setup errors."""
    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientResponseError(
                None,
                None,
                status=401,
            ),
        ),
        pytest.raises(ConfigEntryAuthFailed),
    ):
        await async_setup_entry(hass, base_config_entry)

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientResponseError(None, None, status=500),
        ),
        pytest.raises(ClientResponseError),
    ):
        await async_setup_entry(hass, base_config_entry)

    with (
        patch(
            "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_ensure_token_valid",
            side_effect=ClientConnectorError(Mock(), OSError()),
        ),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(hass, base_config_entry)


async def test_full_init(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
):
    """Test full HomeLINK initialisation."""

    assert hasattr(base_config_entry.runtime_data, "options")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house", "off")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house_alarm", "off")
    check_entity_state(hass, "binary_sensor.dummy_user_my_house_environment", "off")
    assert (
        hass.states.get("sensor.dummy_user_my_house_hallway1_envco2sensor_abandonment")
        is None
    )


@pytest.mark.filterwarnings(
    "ignore:coroutine 'AsyncMockMixin._execute_mock_call' was never awaited"
)
async def test_refresh_token(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
    refresh_config_entry: HomelinkMockConfigEntry,
):
    """Check token refresh."""

    refresh_config_entry.add_to_hass(hass)

    await async_process_ha_core_config(
        hass,
        {"external_url": EXTERNAL_URL},
    )
    standard_mocks(aioclient_mock)

    with patch(
        "custom_components.homelink.helpers.oauth2.HomeLINKOAuth2Implementation._async_token_refresh",
    ) as async_token_refresh:
        await hass.config_entries.async_setup(refresh_config_entry.entry_id)
    assert async_token_refresh.called


@pytest.fixture
async def local_oauth_impl(hass: HomeAssistant):
    """Local implementation."""
    assert await async_setup_component(hass, "auth", {})
    return config_entry_oauth2_flow.LocalOAuth2Implementation(
        hass, DOMAIN, "client_id", "client_secret", "authorize_url", TOKEN_URL
    )


async def test_invalid_token(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    local_oauth_impl: ClientSession,
    aiohttp_client_session: ClientSession,
):
    """Check invalid token."""
    data = deepcopy(REFRESH_CONFIG_ENTRY)
    config_entry = HomelinkMockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        unique_id=DOMAIN,
        data=data,
    )
    config_entry.runtime_data = None
    config_entry.add_to_hass(hass)

    new_token = "ACCESS_TOKEN_1"

    mock_token_call(aioclient_mock, new_token, post=True)
    oauth2_session = config_entry_oauth2_flow.OAuth2Session(
        hass, config_entry, local_oauth_impl
    )

    hl = api.AsyncConfigEntryAuth(aiohttp_client_session, oauth2_session)

    tok = await hl.async_get_access_token()
    assert tok == new_token
