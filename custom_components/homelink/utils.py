"""HomeLINK utilities."""

from .const import DOMAIN


def build_device_identifiers(device_id):
    """Build device identifiers"""
    return {(DOMAIN, "device", device_id.upper())}
