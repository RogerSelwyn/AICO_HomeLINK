"""Expected states."""

import datetime

from dateutil.tz import tzutc

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

ALARM_BAD = {
    "alarmed_devices": ["DUMMY_USER_My_House LIVINGROOM FIREALARM"],
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

ENVIRONMENT_BAD = {
    "alarmed_devices": "None",
    "alarmed_rooms": ["HALLWAY1"],
    "alerts": [
        {
            "alertid": "5f564e4f-2a47-431f-a470-134312f597fc",
            "status": "ACTIVE",
            "eventtype": "AIRQUALITY_MEDIUM",
            "severity": "MEDIUM",
            "raiseddate": datetime.datetime(2024, 9, 1, 23, 0, tzinfo=tzutc()),
            "category": "INSIGHT",
            "type": "INSIGHT",
            "description": "Airquality calculated as medium",
        },
        {
            "alertid": "37d39a93-b631-4e40-befe-80b568505f02",
            "status": "ACTIVE",
            "eventtype": "DAMPMOULD_RISK_HIGH",
            "severity": "HIGH",
            "raiseddate": datetime.datetime(2024, 7, 12, 23, 0, tzinfo=tzutc()),
            "category": "INSIGHT",
            "type": "INSIGHT",
            "description": "Dampmould calculated as high",
        },
    ],
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "safety",
    "friendly_name": "DUMMY_USER_My_House environment",
}
