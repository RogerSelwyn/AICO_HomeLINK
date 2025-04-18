"""API access for HomeLINK service."""

from typing import Any, cast

from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


class HomeLINKOAuth2Implementation(AuthImplementation):
    """OAuth implementation for Device Auth."""

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_credential: ClientCredential,
        authorization_server: AuthorizationServer,
    ) -> None:
        """Set up HomeLINK oauth."""
        super().__init__(
            hass=hass,
            auth_domain=domain,
            credential=client_credential,
            authorization_server=authorization_server,
        )

        self._name = client_credential.name

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """Resolve HomeLINK API Credentials object to Home Assistant token."""
        return await self._async_token_refresh()

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh tokens."""
        new_token = await self._async_token_refresh()
        return {**token, **new_token}

    async def _async_token_refresh(self) -> dict[Any, Any]:
        session = async_get_clientsession(self.hass)
        url = self.token_url.format(self.client_id, self.client_secret)
        resp = await session.get(url)
        resp.raise_for_status()
        token = cast("dict", await resp.json())
        # HomeLINK hasnon-standard OAUTH implementation since no `refresh`
        # token is used and there is no authorisation to the scope.
        # In effect client id/secret is just a userid/password that provides
        # a token that expires in the way a normal access token expires.
        return {
            "access_token": token["accessToken"],
            "refresh_token": None,
            "scope": "standard",
            "token_type": "Bearer",
            "expires_in": 20 * 60 * 60,
        }
