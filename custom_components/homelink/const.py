"""Constants for HomeLINK integration."""
from enum import StrEnum

ATTRIBUTION = "Data provided by AICO HomeLINK"
CONF_MQTT_ENABLE = "mqtt_enable"
CONF_MQTT_TOPIC = "mqtt_topic"
DOMAIN = "homelink"


class HomeLINKMessageType(StrEnum):
    """HomeLINK Message Types."""

    EVENT_ALERT = "alert"
    EVENT_DEVICE = "device"
    EVENT_EVENT = "event"
    EVENT_NOTIFICATION = "notification"
    EVENT_PROPERTY = "property"
    EVENT_READING = "reading"
    EVENT_UNKNOWN = "unknown"
