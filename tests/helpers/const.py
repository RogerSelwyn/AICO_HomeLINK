"""Constants for HOmelINK testing."""

import time

from custom_components.homelink.const import (  # CONF_EVENT_ENABLE,; CONF_MQTT_ENABLE,; CONF_MQTT_HOMELINK,; CONF_MQTT_TOPIC,
    CONF_INSIGHTS_ENABLE,
    CONF_PROPERTIES,
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
TOKEN_URL = f"{BASE_AUTH_URL}/oauth2?client={CLIENT_ID}&secret={CLIENT_SECRET}"

REFRESH_CONFIG_ENTRY = {
    "auth_implementation": DOMAIN,
    "token": {
        "access_token": TOKEN,
        "refresh_token": None,
        "scope": "standard",
        "token_type": "bearer",
        "expires_in": 72000,
        "expires_at": time.time() - 1000,
    },
}


WEBHOOK_ID = webhook.async_generate_id()
WEBHOOK_OPTIONS = {
    CONF_PROPERTIES: {
        "DUMMY_USER_Ignored_Property": False,
        "DUMMY_USER_My_House": True,
    },
    CONF_WEBHOOK_ENABLE: True,
    CONF_WEBHOOK_ID: WEBHOOK_ID,
}
INSIGHT_OPTIONS = {
    CONF_INSIGHTS_ENABLE: True,
}
# MQTT_HA_OPTIONS = {
#     CONF_MQTT_TOPIC: "dummy_user",
#     CONF_MQTT_ENABLE: True,
#     CONF_MQTT_HOMELINK: False,
#     CONF_EVENT_ENABLE: True,
# }

# MQTT_HL_OPTIONS = {
#     CONF_MQTT_TOPIC: "dummy_user",
#     CONF_MQTT_ENABLE: True,
#     CONF_MQTT_HOMELINK: True,
#     CONF_EVENT_ENABLE: True,
# }
