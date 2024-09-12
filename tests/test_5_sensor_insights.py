"""Test setup process."""

from homeassistant.core import HomeAssistant

from .conftest import HomelinkMockConfigEntry
from .data.state.insight_state import (
    ABANDONMENT,
    AIRQUALITY,
    COLDHOMES,
    EXCESSHEAT,
    HEATLOSS,
    VENTILATION,
)
from .helpers.utils import check_entity_state


async def test_insights_init(
    hass: HomeAssistant,
    setup_insight_integration: None,
    insight_config_entry: HomelinkMockConfigEntry,
):
    """Test HomeLINK Insight entities."""

    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_abandonment",
        "0",
        ABANDONMENT,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_airquality",
        "63.7191",
        AIRQUALITY,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_coldhomes",
        "0.0282",
        COLDHOMES,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_excessheat",
        "0",
        EXCESSHEAT,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_heatloss",
        "28.1923",
        HEATLOSS,
    )
    check_entity_state(
        hass,
        "sensor.dummy_user_my_house_hallway1_envco2sensor_ventilation",
        "20.3674",
        VENTILATION,
    )
