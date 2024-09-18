"""HomeLINK utilities."""

from dateutil import parser
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import (
    ATTR_ALARM,
    ATTR_DEVICE,
    ATTR_HOMELINK,
    ATTR_PROPERTY,
    CONF_PROPERTIES,
    DASHBOARD_URL,
    DOMAIN,
    MODELTYPE_GATEWAY,
    MQTT_ACTIONTIMESTAMP,
)


def build_device_identifiers(device_id):
    """Build device identifiers."""
    return {(DOMAIN, ATTR_DEVICE, device_id.upper())}


def build_mqtt_device_key(device, key, gateway_key):
    """Build the device key gateway-serialnumber."""
    return key if device.modeltype == MODELTYPE_GATEWAY else f"{gateway_key}-{key}"


def get_message_date(payload):
    """Get the action timestamp from the message."""
    return parser.parse(payload[MQTT_ACTIONTIMESTAMP])


def property_device_info(key):
    """Property device information."""
    return DeviceInfo(
        identifiers={(DOMAIN, ATTR_PROPERTY, key)},
        name=key,
        manufacturer=ATTR_HOMELINK,
        model=ATTR_PROPERTY.capitalize(),
        configuration_url=DASHBOARD_URL,
    )


def alarm_device_info(key, alarm_type):
    """Property device information."""
    return DeviceInfo(
        identifiers={(DOMAIN, ATTR_ALARM, f"{key} {alarm_type}")},
        name=f"{key} {alarm_type}",
        via_device=(DOMAIN, ATTR_PROPERTY, key),
        manufacturer=ATTR_HOMELINK,
        model=ATTR_ALARM.capitalize(),
    )


def device_device_info(identifiers, parent_key, device):
    """Device device information."""
    return DeviceInfo(
        identifiers=identifiers,
        name=f"{parent_key} {device.location} {device.modeltype}",
        via_device=(DOMAIN, ATTR_PROPERTY, parent_key),
        manufacturer=device.manufacturer,
        model=device.modeltype,
        model_id=device.model,
    )


def include_property(options, hl_property):
    """Check if property is to be included."""
    properties = options.get(CONF_PROPERTIES, {})

    return properties.get(hl_property, True)
