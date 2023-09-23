"""HomeLINK utilities."""

from .const import ATTR_DEVICE, DOMAIN


def build_device_identifiers(device_id):
    """Build device identifiers"""
    return {(DOMAIN, ATTR_DEVICE, device_id.upper())}
