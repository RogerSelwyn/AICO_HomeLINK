"""HomeLINK utilities."""
from dateutil import parser
from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_VIA_DEVICE,
)

from ..const import (
    ATTR_ALARM,
    ATTR_DEVICE,
    ATTR_HOMELINK,
    ATTR_PROPERTY,
    DASHBOARD_URL,
    DOMAIN,
    MODELTYPE_GATEWAY,
    MQTT_ACTIONTIMESTAMP,
)


def build_device_identifiers(device_id):
    """Build device identifiers"""
    return {(DOMAIN, ATTR_DEVICE, device_id.upper())}


def build_mqtt_device_key(device, key, gateway_key):
    """Build the device key gateway-serialnumber."""
    return key if device.modeltype == MODELTYPE_GATEWAY else f"{gateway_key}-{key}"


def get_message_date(payload):
    """Get the action timestamp from the message"""
    return parser.parse(payload[MQTT_ACTIONTIMESTAMP])


def property_device_info(key):
    """Property device information"""
    return {
        ATTR_IDENTIFIERS: {(DOMAIN, ATTR_PROPERTY, key)},
        ATTR_NAME: key,
        ATTR_MANUFACTURER: ATTR_HOMELINK,
        ATTR_MODEL: ATTR_PROPERTY.capitalize(),
        ATTR_CONFIGURATION_URL: DASHBOARD_URL,
    }


def alarm_device_info(key, alarm_type):
    """Property device information"""
    return {
        ATTR_IDENTIFIERS: {(DOMAIN, ATTR_ALARM, f"{key} {alarm_type}")},
        ATTR_NAME: f"{key} {alarm_type}",
        ATTR_VIA_DEVICE: (DOMAIN, ATTR_PROPERTY, key),
        ATTR_MANUFACTURER: ATTR_HOMELINK,
        ATTR_MODEL: ATTR_ALARM.capitalize(),
    }


def device_device_info(identifiers, parent_key, device):
    """Device device information."""
    return {
        ATTR_IDENTIFIERS: identifiers,
        ATTR_NAME: f"{parent_key} {device.location} {device.modeltype}",
        ATTR_VIA_DEVICE: (DOMAIN, ATTR_PROPERTY, parent_key),
        ATTR_MANUFACTURER: device.manufacturer,
        ATTR_MODEL: f"{device.model} ({device.modeltype})",
    }
