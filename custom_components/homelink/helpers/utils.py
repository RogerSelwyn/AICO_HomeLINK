"""HomeLINK utilities."""
import json
import os

from dateutil import parser
from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_VIA_DEVICE,
    Platform,
)

from ..const import (
    ATTR_ALARM,
    ATTR_DEVICE,
    ATTR_HOMELINK,
    ATTR_PROPERTY,
    DASHBOARD_URL,
    DOMAIN,
    MODELTYPE_GATEWAY,
    MQTT_ACTIONTIMESTAMP,
    STORAGE_ATTRIBUTES,
    STORAGE_DEVICE,
    STORAGE_DEVICES,
    STORAGE_ENCODING,
    STORAGE_STATEFILE,
)


def build_device_identifiers(device_id):
    """Build device identifiers"""
    if not device_id:
        pass
    return {(DOMAIN, ATTR_DEVICE, device_id.upper())}


def build_mqtt_device_key(device, key, gateway_key):
    """Build the device key gateway-serialnumber."""
    return key if device.modeltype == MODELTYPE_GATEWAY else f"{gateway_key}-{key}"


def get_message_date(payload):
    """Get the action timestamp from the message"""
    return parser.parse(payload[MQTT_ACTIONTIMESTAMP])


def property_device_info(key):
    """Property device information"""
    return {
        ATTR_IDENTIFIERS: {(DOMAIN, ATTR_PROPERTY, key)},
        ATTR_NAME: key,
        ATTR_MANUFACTURER: ATTR_HOMELINK,
        ATTR_MODEL: ATTR_PROPERTY.capitalize(),
        ATTR_CONFIGURATION_URL: DASHBOARD_URL,
    }


def alarm_device_info(key, alarm_type):
    """Property device information"""
    return {
        ATTR_IDENTIFIERS: {(DOMAIN, ATTR_ALARM, key, alarm_type)},
        ATTR_NAME: f"{key} {alarm_type}",
        ATTR_VIA_DEVICE: (DOMAIN, ATTR_PROPERTY, key),
        ATTR_MANUFACTURER: ATTR_HOMELINK,
        ATTR_MODEL: ATTR_ALARM.capitalize(),
    }


def device_device_info(identifiers, parent_key, device):
    """Device device information."""
    return {
        ATTR_IDENTIFIERS: identifiers,
        ATTR_NAME: f"{parent_key} {device.location} {device.modeltype}",
        ATTR_VIA_DEVICE: (DOMAIN, ATTR_PROPERTY, parent_key),
        ATTR_MANUFACTURER: device.manufacturer,
        ATTR_MODEL: f"{device.model} ({device.modeltype})",
    }


def read_state(hass, sensor_type, config_device):
    """Read state from storage."""
    statefile = os.path.join(hass.config.config_dir, STORAGE_STATEFILE)
    if os.path.isfile(statefile):
        with open(statefile, "r", encoding=STORAGE_ENCODING) as infile:
            file_content = json.load(infile)

        for sensor in file_content:
            if sensor[Platform.SENSOR] == sensor_type:
                for host in sensor[STORAGE_DEVICES]:
                    if host[STORAGE_DEVICE] == config_device:
                        return host[STORAGE_ATTRIBUTES]

    return None


def write_state(hass, sensor_type, config_device, new_attributes):
    """Write state to storage."""
    statefile = os.path.join(hass.config.config_dir, STORAGE_STATEFILE)
    file_content = []
    old_sensor = None
    if os.path.isfile(statefile):
        with open(statefile, "r", encoding=STORAGE_ENCODING) as infile:
            old_file_content = json.load(infile)
            for sensor in old_file_content:
                if sensor[Platform.SENSOR] != sensor_type:
                    file_content.append(sensor)
                else:
                    old_sensor = sensor

    sensor_devices = []
    if old_sensor:
        sensor_devices.extend(
            sensor
            for sensor in old_sensor[STORAGE_DEVICES]
            if sensor[STORAGE_DEVICE] != config_device
        )

    host_content = {
        STORAGE_DEVICE: config_device,
        STORAGE_ATTRIBUTES: new_attributes,
    }
    sensor_devices.append(host_content)
    sensor_content = {
        Platform.SENSOR: sensor_type,
        STORAGE_DEVICES: sensor_devices,
    }
    file_content.append(sensor_content)

    with open(statefile, "w", encoding=STORAGE_ENCODING) as outfile:
        json.dump(file_content, outfile, ensure_ascii=False, indent=4)
