"""HomeLINK utilities."""
from dateutil import parser

from ..const import ATTR_DEVICE, DOMAIN, MODELTYPE_GATEWAY, MQTT_ACTIONTIMESTAMP


def build_device_identifiers(device_id):
    """Build device identifiers"""
    return {(DOMAIN, ATTR_DEVICE, device_id.upper())}


def build_mqtt_device_key(device, key, gateway_key):
    """Build the device key gateway-serialnumber."""
    return key if device.modeltype == MODELTYPE_GATEWAY else f"{gateway_key}-{key}"


def get_message_date(payload):
    """Get the action timestamp from the message"""
    return parser.parse(payload[MQTT_ACTIONTIMESTAMP])
