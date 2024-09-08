"""Constants for HOmelINK testing."""

import time

from custom_components.homelink.const import DOMAIN

CLIENT_ID = "1234"
CLIENT_SECRET = "5678"
# REDIRECT_URI = "https://example.com/auth/external/callback"
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
