"""Constants for HOmelINK testing."""

import time

from custom_components.homelink.const import (
    CONF_INSIGHTS_ENABLE,
    CONF_WEBHOOK_ENABLE,
    DOMAIN,
)
from homeassistant.components import webhook
from homeassistant.const import CONF_WEBHOOK_ID

CLIENT_ID = "1234"
CLIENT_SECRET = "5678"
EXTERNAL_URL = "https://example.com"
BASE_AUTH_URL = "https://auth.live.homelync.io"
BASE_API_URL = "https://frontier.live.homelync.io/v1"
TOKEN = "longtoken"
TITLE = "mock"
BASE_CONFIG_ENTRY = {
    "auth_implementation": DOMAIN,
    "token": {
        "access_token": TOKEN,
        "refresh_token": None,
        "scope": "standard",
        "token_type": "bearer",
        "expires_in": 72000,
        "expires_at": time.time() + (20 * 60 * 60),
    },
}

WEBHOOK_ID = webhook.async_generate_id()
WEBHOOK_OPTIONS = {
    CONF_WEBHOOK_ENABLE: True,
    CONF_WEBHOOK_ID: WEBHOOK_ID,
}
INSIGHT_OPTIONS = {
    CONF_INSIGHTS_ENABLE: True,
}
