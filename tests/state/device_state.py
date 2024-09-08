"""Expected states."""

import datetime

from dateutil.tz import tzutc

LIVINGROOM_FIREALARM_GOOD = {
    "serialnumber": "D8EAF0D0",
    "installationdate": datetime.datetime(2023, 9, 5, 0, 0, tzinfo=tzutc()),
    "installedby": "Dummy User",
    "replacedate": datetime.datetime(2034, 6, 26, 0, 0, tzinfo=tzutc()),
    "metadata": {
        "signalstrength": -50,
        "lastseendate": datetime.datetime(
            2024, 8, 11, 9, 30, 24, 840000, tzinfo=tzutc()
        ),
        "connectivitytype": "EIRF868",
    },
    "status": {
        "operationalstatus": "GOOD",
        "lasttesteddate": datetime.datetime(2024, 9, 6, 9, 5, 16, tzinfo=tzutc()),
        "datacollectionstatus": "ACTIVE",
    },
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "smoke",
    "friendly_name": "DUMMY_USER_My_House LIVINGROOM FIREALARM",
}

HALLWAY1_EIACCESSORY_GOOD = {
    "serialnumber": "D8F7C0E8",
    "installationdate": datetime.datetime(2023, 9, 5, 0, 0, tzinfo=tzutc()),
    "installedby": "Dummy User",
    "replacedate": datetime.datetime(2034, 7, 3, 0, 0, tzinfo=tzutc()),
    "metadata": {
        "signalstrength": -53,
        "lastseendate": datetime.datetime(2024, 9, 6, 9, 9, 41, 473000, tzinfo=tzutc()),
        "connectivitytype": "EIRF868",
    },
    "status": {
        "operationalstatus": "GOOD",
        "lasttesteddate": datetime.datetime(2024, 9, 6, 9, 5, 16, tzinfo=tzutc()),
        "datacollectionstatus": "ACTIVE",
    },
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "problem",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 EIACCESSORY",
}

KITCHEN_GATEWAY_GOOD = {
    "serialnumber": "C3CEC7FB",
    "installationdate": datetime.datetime(2023, 9, 5, 0, 0, tzinfo=tzutc()),
    "installedby": "Dummy User",
    "replacedate": datetime.datetime(2034, 4, 24, 0, 0, tzinfo=tzutc()),
    "metadata": {
        "signalstrength": -79,
        "lastseendate": datetime.datetime(
            2024, 9, 7, 9, 24, 19, 466000, tzinfo=tzutc()
        ),
        "connectivitytype": "GSM",
    },
    "status": {
        "operationalstatus": "GOOD",
        "lasttesteddate": None,
        "datacollectionstatus": "ACTIVE",
    },
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "problem",
    "friendly_name": "DUMMY_USER_My_House KITCHEN GATEWAY",
}

HALLWAY1_ENVCO2SENSOR_GOOD = {
    "serialnumber": "001FD75F",
    "installationdate": datetime.datetime(
        2023, 11, 16, 15, 48, 30, 627000, tzinfo=tzutc()
    ),
    "installedby": "Dummy User",
    "replacedate": datetime.datetime(2033, 8, 15, 0, 0, tzinfo=tzutc()),
    "metadata": {
        "signalstrength": -54,
        "lastseendate": datetime.datetime(
            2024, 9, 7, 9, 24, 19, 471000, tzinfo=tzutc()
        ),
        "connectivitytype": "EIRF868",
    },
    "status": {
        "operationalstatus": "GOOD",
        "lasttesteddate": None,
        "datacollectionstatus": "ACTIVE",
    },
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "problem",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR",
}

KITCHEN_FIREALARM_GOOD = {
    "serialnumber": "D6F7C1DC",
    "installationdate": datetime.datetime(2023, 9, 5, 0, 0, tzinfo=tzutc()),
    "installedby": "Dummy User",
    "replacedate": datetime.datetime(2034, 5, 8, 0, 0, tzinfo=tzutc()),
    "metadata": {
        "signalstrength": -50,
        "lastseendate": datetime.datetime(
            2024, 8, 10, 18, 12, 11, 460000, tzinfo=tzutc()
        ),
        "connectivitytype": "EIRF868",
    },
    "status": {
        "operationalstatus": "GOOD",
        "lasttesteddate": datetime.datetime(2024, 9, 6, 9, 5, 16, tzinfo=tzutc()),
        "datacollectionstatus": "ACTIVE",
    },
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "smoke",
    "friendly_name": "DUMMY_USER_My_House KITCHEN FIREALARM",
}

UTILITY_FIRECOALARM_GOOD = {
    "serialnumber": "D6FCD4F0",
    "installationdate": datetime.datetime(2023, 9, 5, 0, 0, tzinfo=tzutc()),
    "installedby": "Dummy User",
    "replacedate": datetime.datetime(2034, 5, 29, 0, 0, tzinfo=tzutc()),
    "metadata": {
        "signalstrength": -50,
        "lastseendate": datetime.datetime(
            2024, 8, 10, 12, 11, 7, 460000, tzinfo=tzutc()
        ),
        "connectivitytype": "EIRF868",
    },
    "status": {
        "operationalstatus": "GOOD",
        "lasttesteddate": datetime.datetime(2024, 9, 6, 9, 5, 16, tzinfo=tzutc()),
        "datacollectionstatus": "ACTIVE",
    },
    "attribution": "Data provided by AICO HomeLINK",
    "device_class": "smoke",
    "friendly_name": "DUMMY_USER_My_House UTILITY FIRECOALARM",
}
