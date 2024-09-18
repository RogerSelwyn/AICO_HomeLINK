"""Test sensors."""

from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import HomelinkMockConfigEntry, standard_mocks
from .helpers.utils import add_device_mocks, add_property_mocks


async def test_add_property(
    hass: HomeAssistant,
    setup_insight_integration: None,
    insight_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test addition of new property."""
    coordinator = insight_config_entry.runtime_data.coordinator
    devices = device_registry.devices.get_devices_for_config_entry_id(
        insight_config_entry.entry_id
    )
    assert len(devices) == 10

    entities = er.async_entries_for_config_entry(
        entity_registry, insight_config_entry.entry_id
    )
    assert len(entities) == 41

    aioclient_mock.clear_requests()
    add_property_mocks(aioclient_mock)

    await coordinator.async_refresh()
    await hass.async_block_till_done()
    devices = device_registry.devices.get_devices_for_config_entry_id(
        insight_config_entry.entry_id
    )
    assert len(devices) == 16

    entities = er.async_entries_for_config_entry(
        entity_registry, insight_config_entry.entry_id
    )
    assert len(entities) == 56


async def test_add_device(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test addition of new device."""
    coordinator = base_config_entry.runtime_data.coordinator
    devices = device_registry.devices.get_devices_for_config_entry_id(
        base_config_entry.entry_id
    )
    assert len(devices) == 10

    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 27

    aioclient_mock.clear_requests()
    add_device_mocks(aioclient_mock)

    await coordinator.async_refresh()
    await hass.async_block_till_done()
    devices = device_registry.devices.get_devices_for_config_entry_id(
        base_config_entry.entry_id
    )
    assert len(devices) == 11

    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 30


async def test_delete_device(
    hass: HomeAssistant,
    setup_base_integration: None,
    base_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test deletion of device."""
    coordinator = base_config_entry.runtime_data.coordinator

    aioclient_mock.clear_requests()
    add_device_mocks(aioclient_mock)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    devices = device_registry.devices.get_devices_for_config_entry_id(
        base_config_entry.entry_id
    )
    assert len(devices) == 11

    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 30

    aioclient_mock.clear_requests()
    standard_mocks(aioclient_mock)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    devices = device_registry.devices.get_devices_for_config_entry_id(
        base_config_entry.entry_id
    )
    assert len(devices) == 10

    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 27


async def test_delete_property(
    hass: HomeAssistant,
    setup_insight_integration: None,
    insight_config_entry: HomelinkMockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    aioclient_mock: AiohttpClientMocker,
):
    """Test deletion of device."""
    coordinator = insight_config_entry.runtime_data.coordinator

    aioclient_mock.clear_requests()
    add_property_mocks(aioclient_mock)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    devices = device_registry.devices.get_devices_for_config_entry_id(
        insight_config_entry.entry_id
    )
    assert len(devices) == 16

    entities = er.async_entries_for_config_entry(
        entity_registry, insight_config_entry.entry_id
    )
    assert len(entities) == 56

    aioclient_mock.clear_requests()
    standard_mocks(aioclient_mock)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    devices = device_registry.devices.get_devices_for_config_entry_id(
        insight_config_entry.entry_id
    )
    assert len(devices) == 10

    entities = er.async_entries_for_config_entry(
        entity_registry, insight_config_entry.entry_id
    )
    assert len(entities) == 41
