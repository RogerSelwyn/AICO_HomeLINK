"""Tests for AICO HomeLINK."""


def check_entity_state(hass, entity_name, entity_state, entity_attributes=None):
    """Check entity state."""
    state = hass.states.get(entity_name)
    assert state.state == entity_state
    if entity_attributes:
        # print(state.attributes)
        assert state.attributes == entity_attributes
