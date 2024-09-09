"""Test setup process."""

from .conftest import HomelinkMockConfigEntry


async def test_webhook_init(
    hass,
    setup_webhook_integration,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Test full HomeLINK initialisation with webhooks."""
    assert webhook_config_entry.runtime_data.webhook
