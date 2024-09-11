# pylint: disable=protected-access,redefined-outer-name
"""Global fixtures for integration."""

from dataclasses import dataclass
from datetime import date
import sys
from unittest.mock import Mock, patch

from aiohttp import ClientSession
from aiohttp.test_utils import TestClient
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.homelink import HLData
from custom_components.homelink.const import DOMAIN
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.components.webhook import async_generate_url
from homeassistant.config import async_process_ha_core_config
from homeassistant.core import Event, HomeAssistant
from homeassistant.setup import async_setup_component

from .helpers.const import (  # MQTT_HA_OPTIONS,; MQTT_HL_OPTIONS,
    BASE_CONFIG_ENTRY,
    CLIENT_ID,
    CLIENT_SECRET,
    EXTERNAL_URL,
    INSIGHT_OPTIONS,
    REFRESH_CONFIG_ENTRY,
    TITLE,
    WEBHOOK_OPTIONS,
)
from .helpers.utils import create_mock

pytest_plugins = "pytest_homeassistant_custom_component"  # pylint: disable=invalid-name
THIS_MODULE = sys.modules[__name__]


class HomelinkMockConfigEntry(MockConfigEntry):
    """Mock config entry with Homelink runtime_data."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialise HomelinkMockConfigEntry."""
        self.runtime_data: HLData = None
        super().__init__(*args, **kwargs)


@pytest.fixture
def aiohttp_client_session() -> None:
    """AIOHTTP client session."""
    return ClientSession


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # pylint: disable=unused-argument
    """Automatically enable loading custom integrations in all tests."""
    return


@pytest.fixture(autouse=True)
async def request_setup(current_request_with_host: None) -> None:  # pylint: disable=unused-argument
    """Request setup."""


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


@pytest.fixture
async def setup_credentials(hass: HomeAssistant) -> None:
    """Fixture to setup application credentials component."""
    await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(CLIENT_ID, CLIENT_SECRET),
    )


@pytest.fixture
def base_config_entry(hass: HomeAssistant) -> HomelinkMockConfigEntry:
    """Create HomeLINK entry in Home Assistant."""
    data = BASE_CONFIG_ENTRY
    entry = HomelinkMockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        unique_id=DOMAIN,
        data=data,
    )
    entry.runtime_data = None
    return entry


@pytest.fixture
def refresh_config_entry(
    hass: HomeAssistant,
) -> HomelinkMockConfigEntry:
    """Create HomeLINK entry in Home Assistant."""
    data = REFRESH_CONFIG_ENTRY
    entry = HomelinkMockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        unique_id=DOMAIN,
        data=data,
    )
    entry.runtime_data = None
    return entry


@pytest.fixture
def webhook_config_entry(hass: HomeAssistant) -> HomelinkMockConfigEntry:
    """Create HomeLINK entry in Home Assistant."""
    data = BASE_CONFIG_ENTRY
    entry = HomelinkMockConfigEntry(
        domain=DOMAIN, title=TITLE, unique_id=DOMAIN, data=data, options=WEBHOOK_OPTIONS
    )
    entry.runtime_data = None
    return entry


@pytest.fixture
def insight_config_entry(
    hass: HomeAssistant,
) -> HomelinkMockConfigEntry:
    """Create HomeLINK entry in Home Assistant."""
    data = BASE_CONFIG_ENTRY
    entry = HomelinkMockConfigEntry(
        domain=DOMAIN, title=TITLE, unique_id=DOMAIN, data=data, options=INSIGHT_OPTIONS
    )
    entry.runtime_data = None
    return entry


# @pytest.fixture
# def mqtt_ha_config_entry(
#     hass: HomeAssistant,
# ) -> HomelinkMockConfigEntry:
#     """Create HomeLINK entry in Home Assistant."""
#     data = BASE_CONFIG_ENTRY
#     entry = HomelinkMockConfigEntry(
#         domain=DOMAIN, title=TITLE, unique_id=DOMAIN, data=data, options=MQTT_HA_OPTIONS
#     )
#     entry.runtime_data = None
#     return entry


# @pytest.fixture
# def mqtt_hl_config_entry(
#     hass: HomeAssistant,
# ) -> HomelinkMockConfigEntry:
#     """Create HomeLINK entry in Home Assistant."""
#     data = BASE_CONFIG_ENTRY
#     entry = HomelinkMockConfigEntry(
#         domain=DOMAIN, title=TITLE, unique_id=DOMAIN, data=data, options=MQTT_HL_OPTIONS
#     )
#     entry.runtime_data = None
#     return entry


@pytest.fixture
async def setup_base_integration(
    request,
    hass,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
    base_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Fixture for setting up the component."""
    if hasattr(request, "param"):
        method_name = request.param
    else:
        method_name = "standard_mocks"

    mock_method = getattr(THIS_MODULE, method_name)
    mock_method(aioclient_mock)

    base_config_entry.add_to_hass(hass)

    await async_process_ha_core_config(
        hass,
        {"external_url": EXTERNAL_URL},
    )

    await hass.config_entries.async_setup(base_config_entry.entry_id)


@pytest.fixture
async def setup_webhook_integration(
    request,
    hass,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
    webhook_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Fixture for setting up the component."""
    if hasattr(request, "param"):
        method_name = request.param
    else:
        method_name = "standard_mocks"

    mock_method = getattr(THIS_MODULE, method_name)
    mock_method(aioclient_mock)

    webhook_config_entry.add_to_hass(hass)

    await async_process_ha_core_config(
        hass,
        {"external_url": EXTERNAL_URL},
    )

    await hass.config_entries.async_setup(webhook_config_entry.entry_id)


@pytest.fixture
async def setup_insight_integration(
    request,
    hass,
    aioclient_mock: AiohttpClientMocker,
    setup_credentials: None,
    insight_config_entry: HomelinkMockConfigEntry,
) -> None:
    """Fixture for setting up the component."""
    if hasattr(request, "param"):
        method_name = request.param
    else:
        method_name = "standard_mocks"

    mock_method = getattr(THIS_MODULE, method_name)
    mock_method(aioclient_mock)

    insight_config_entry.add_to_hass(hass)

    await async_process_ha_core_config(
        hass,
        {"external_url": EXTERNAL_URL},
    )

    await hass.config_entries.async_setup(insight_config_entry.entry_id)


# @pytest.fixture
# async def setup_mqtt_integration(
#     request,
#     hass,
#     aioclient_mock: AiohttpClientMocker,
#     setup_credentials: None,
#     mqtt_ha_config_entry: HomelinkMockConfigEntry,
#     mqtt_mock: MqttMockHAClient,
# ) -> None:
#     """Fixture for setting up the component."""
#     if hasattr(request, "param"):
#         method_name = request.param
#     else:
#         method_name = "standard_mocks"

#     mock_method = getattr(THIS_MODULE, method_name)
#     mock_method(aioclient_mock)

#     mqtt_ha_config_entry.add_to_hass(hass)

#     await async_process_ha_core_config(
#         hass,
#         {"external_url": EXTERNAL_URL},
#     )

#     await hass.config_entries.async_setup(mqtt_ha_config_entry.entry_id)


def standard_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Specific standard mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "base/lookup.json")
    create_mock(aioclient_mock, "/property", "base/property.json")
    create_mock(aioclient_mock, "/device", "base/device.json")
    create_mock(
        aioclient_mock, "/property/DUMMY_USER_My_House/alerts", "base/alerts.json"
    )
    create_mock(
        aioclient_mock,
        f"/property/DUMMY_USER_My_House/readings?date={date.today()}",
        "base/readings.json",
    )
    create_mock(aioclient_mock, "/insight", "base/insight.json")


def environment_alert_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Alert mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "base/lookup.json")
    create_mock(aioclient_mock, "/property", "base/property.json")
    create_mock(aioclient_mock, "/device", "base/device.json")
    create_mock(
        aioclient_mock,
        "/property/DUMMY_USER_My_House/alerts",
        "base/alerts_environment.json",
    )
    create_mock(
        aioclient_mock,
        f"/property/DUMMY_USER_My_House/readings?date={date.today()}",
        "base/readings.json",
    )


def alarm_alert_mocks(
    aioclient_mock: AiohttpClientMocker,
):
    """Alert mocks."""
    create_mock(aioclient_mock, "/lookup/eventType", "base/lookup.json")
    create_mock(aioclient_mock, "/property", "base/property.json")
    create_mock(aioclient_mock, "/device", "base/device.json")
    create_mock(
        aioclient_mock,
        "/property/DUMMY_USER_My_House/alerts",
        "base/alerts_alarm.json",
    )
    url = f"/property/DUMMY_USER_My_House/readings?date={date.today()}"
    create_mock(aioclient_mock, url, "base/readings.json")


# @dataclass
# class MQTTSetupData:
#     """A collection of data set up by the mqtt_setup fixture."""

#     hass: HomeAssistant
#     client: TestClient
#     event_listener: Mock
#     events: any


# @pytest.fixture
# async def mqtt_ha_setup(
#     hass: HomeAssistant,
#     aioclient_mock: AiohttpClientMocker,
#     setup_credentials: None,
#     mqtt_ha_config_entry: HomelinkMockConfigEntry,
#     hass_client_no_auth: ClientSessionGenerator,
#     mqtt_mock: MqttMockHAClient,
# ) -> MQTTSetupData:
#     """Set up integration."""
#     standard_mocks(aioclient_mock)
#     mqtt_ha_config_entry.add_to_hass(hass)
#     await hass.config_entries.async_setup(mqtt_ha_config_entry.entry_id)
#     await hass.async_block_till_done()

#     client = await hass_client_no_auth()

#     events = []

#     async def event_listener(event: Event) -> None:
#         events.append(event)

#     hass.bus.async_listen("homelink_alert", event_listener)
#     hass.bus.async_listen("homelink_device", event_listener)
#     hass.bus.async_listen("homelink_notification", event_listener)
#     hass.bus.async_listen("homelink_property", event_listener)
#     hass.bus.async_listen("homelink_reading", event_listener)
#     hass.bus.async_listen("homelink_unknown", event_listener)

#     return MQTTSetupData(hass, client, event_listener, events)


# @pytest.fixture
# async def mqtt_hl_setup(
#     hass: HomeAssistant,
#     aioclient_mock: AiohttpClientMocker,
#     setup_credentials: None,
#     mqtt_hl_config_entry: HomelinkMockConfigEntry,
#     hass_client_no_auth: ClientSessionGenerator,
#     mqtt_mock: MqttMockHAClient,
# ) -> MQTTSetupData:
#     """Set up integration."""
#     standard_mocks(aioclient_mock)
#     mqtt_hl_config_entry.add_to_hass(hass)
#     await hass.config_entries.async_setup(mqtt_hl_config_entry.entry_id)
#     await hass.async_block_till_done()

#     client = await hass_client_no_auth()

#     events = []

#     async def event_listener(event: Event) -> None:
#         events.append(event)

#     hass.bus.async_listen("homelink_alert", event_listener)
#     hass.bus.async_listen("homelink_device", event_listener)
#     hass.bus.async_listen("homelink_notification", event_listener)
#     hass.bus.async_listen("homelink_property", event_listener)
#     hass.bus.async_listen("homelink_reading", event_listener)
#     hass.bus.async_listen("homelink_unknown", event_listener)

#     return MQTTSetupData(hass, client, event_listener, events)


@dataclass
class WebhookSetupData:
    """A collection of data set up by the webhook_setup fixture."""

    hass: HomeAssistant
    client: TestClient
    webhook_url: str
    event_listener: Mock
    events: any


@pytest.fixture
async def webhook_setup(
    hass: HomeAssistant,
    setup_webhook_integration,
    webhook_config_entry: HomelinkMockConfigEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> WebhookSetupData:
    """Set up integration, client and webhook url."""

    client = await hass_client_no_auth()
    webhook_id = webhook_config_entry.options["webhook_id"]
    webhook_url = async_generate_url(hass, webhook_id)

    events = []

    async def event_listener(event: Event) -> None:
        events.append(event)

    hass.bus.async_listen("homelink_alert", event_listener)
    hass.bus.async_listen("homelink_device", event_listener)
    hass.bus.async_listen("homelink_notification", event_listener)
    hass.bus.async_listen("homelink_property", event_listener)
    hass.bus.async_listen("homelink_reading", event_listener)
    hass.bus.async_listen("homelink_unknown", event_listener)

    return WebhookSetupData(hass, client, webhook_url, event_listener, events)
