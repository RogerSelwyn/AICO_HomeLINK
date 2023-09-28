"""Helpers for raising events."""
import logging

from ..const import (
    ATTR_DEVICE,
    ATTR_DEVICE_INFO,
    ATTR_PAYLOAD,
    ATTR_PROPERTY,
    ATTR_SUB_TYPE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def raise_property_event(hass, event_type, payload):
    """Raise a property event."""
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {ATTR_SUB_TYPE: ATTR_PROPERTY, ATTR_PAYLOAD: payload},
    )
    _LOGGER.debug("%s - %s_%s - %s", ATTR_PROPERTY, DOMAIN, event_type, payload)


def raise_device_event(hass, device_info, event_type, payload):
    """Raise a device event."""
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {
            ATTR_SUB_TYPE: ATTR_DEVICE,
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