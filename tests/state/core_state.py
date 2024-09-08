"""Expected states."""

# import datetime

# from dateutil.tz import tzutc

HOME_GOOD = {
    "reference": "DUMMY_USER_My_House",
    "address": "My House Town City County PostCode GB",
    "latitude": 60.01953704,
    "longitude": 1.36647542,
    "tags": ["COTTAGE"],
    "alarmed_devices": "None",
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "safety",
    "friendly_name": "DUMMY_USER_My_House",
}

ALARM_GOOD = {
    "alarmed_devices": "None",
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "safety",
    "friendly_name": "DUMMY_USER_My_House alarm",
}

ENVIRONMENT_GOOD = {
    "alarmed_devices": "None",
    "alarmed_rooms": "None",
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "safety",
    "friendly_name": "DUMMY_USER_My_House environment",
}
