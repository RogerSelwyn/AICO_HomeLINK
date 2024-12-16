"""Application_credentials platform for HomeLINK."""

from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from pyhomelink import AUTH_URL

from .const import ATTR_INTEGRATIONS_URL, INTEGRATIONS_URL
from .helpers.oauth2 import HomeLINKOAuth2Implementation


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return auth implementation."""
    return HomeLINKOAuth2Implementation(
        hass, auth_domain, credential, await async_get_authorization_server(hass)
    )


async def async_get_description_placeholders(
    hass: HomeAssistant,  # pylint: disable=unused-argument
) -> dict[str, str]:
    """Return description placeholders for the credentials dialog."""
    return {
        ATTR_INTEGRATIONS_URL: INTEGRATIONS_URL,
    }


async def async_get_authorization_server(
    hass: HomeAssistant,  # pylint: disable=unused-argument
) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url="None",
        token_url=AUTH_URL,
    )
