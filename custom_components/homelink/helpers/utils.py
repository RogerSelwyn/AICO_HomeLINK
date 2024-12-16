"""HomeLINK utilities."""

import logging
from datetime import datetime
from types import MappingProxyType
from typing import Any

from dateutil import parser
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from pyhomelink.device import Device

from ..const import (
    ATTR_ALARM,
    ATTR_DEVICE,
    ATTR_DEVICE_INFO,
    ATTR_HOMELINK,
    ATTR_PAYLOAD,
    ATTR_PROPERTY,
    ATTR_READING,
    ATTR_SUB_TYPE,
    ATTR_TOPIC,
    CONF_PROPERTIES,
    DASHBOARD_URL,
    DOMAIN,
    MODELTYPE_GATEWAY,
    MQTT_ACTIONTIMESTAMP,
)

_LOGGER = logging.getLogger(__name__)


def build_device_identifiers(device_id: str) -> set[tuple[str, str]]:
    """Build device identifiers."""
    return {(DOMAIN, device_id.upper())}


def build_mqtt_device_key(device: Device, key: str, gateway_key: str) -> str:
    """Build the device key gateway-serialnumber."""
    return key if device.modeltype == MODELTYPE_GATEWAY else f"{gateway_key}-{key}"


def get_message_date(payload: dict) -> datetime:
    """Get the action timestamp from the message."""
    return parser.parse(payload[MQTT_ACTIONTIMESTAMP])


def property_device_info(key: str) -> DeviceInfo:
    """Property device information."""
    return DeviceInfo(
        identifiers={(DOMAIN, key)},
        name=key,
        manufacturer=ATTR_HOMELINK,
        model=ATTR_PROPERTY.capitalize(),
        configuration_url=DASHBOARD_URL,
    )


def alarm_device_info(key: str, alarm_type: str) -> DeviceInfo:
    """Property device information."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{key} {alarm_type}")},
        name=f"{key} {alarm_type}",
        via_device=(DOMAIN, key),
        manufacturer=ATTR_HOMELINK,
        model=ATTR_ALARM.capitalize(),
    )


def device_device_info(
    identifiers: set[tuple[str, str]], parent_key: str, device: Device
) -> DeviceInfo:
    """Device device information."""
    return DeviceInfo(
        identifiers=identifiers,
        name=f"{parent_key} {device.location} {device.modeltype}",
        via_device=(DOMAIN, parent_key),
        manufacturer=device.manufacturer,
        model=device.modeltype,
        model_id=device.model,
    )


def include_property(options: MappingProxyType[str, Any], hl_property: str) -> bool:
    """Check if property is to be included."""
    properties = options.get(CONF_PROPERTIES, {})

    return properties.get(hl_property, True)


def raise_property_alarm_event(
    hass: HomeAssistant, event_type: str, topic: str, payload: dict
) -> None:
    """Raise a property event."""
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {
            ATTR_SUB_TYPE: ATTR_PROPERTY,
            ATTR_TOPIC: topic.split("/"),
            ATTR_PAYLOAD: payload,
        },
    )
    _LOGGER.debug("%s - %s_%s - %s", ATTR_PROPERTY, DOMAIN, event_type, payload)


def raise_device_event(
    hass: HomeAssistant,
    device_info: DeviceInfo,
    event_type: str,
    topic: str,
    payload: dict,
) -> None:
    """Raise a device event."""
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {
            ATTR_SUB_TYPE: ATTR_DEVICE,
            ATTR_TOPIC: topic.split("/"),
            ATTR_DEVICE_INFO: device_info,
            ATTR_PAYLOAD: payload,
        },
    )
    _LOGGER.debug(
        "%s - %s_%s - %s - %s",
        ATTR_DEVICE,
        DOMAIN,
        event_type,
        device_info,
        payload,
    )


def raise_reading_event(
    hass: HomeAssistant, event_type: str, readingtype: str, topic: str, payload: dict
) -> None:
    """Raise a reading event."""
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {
            ATTR_SUB_TYPE: ATTR_READING,
            ATTR_TOPIC: topic.split("/"),
            ATTR_PAYLOAD: payload,
        },
    )
    _LOGGER.debug(
        "%s - %s_%s - %s - %s",
        ATTR_READING,
        DOMAIN,
        event_type,
        readingtype,
        payload,
    )
