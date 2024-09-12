"""Expected Insight states."""

import datetime

from dateutil.tz import tzutc

ABANDONMENT = {
    "state_class": "measurement",
    "type": "room_insight",
    "insightid": "ad17c1ad-fecd-4f3c-bef1-7b373b7d7e0a",
    "risklevel": "LOW",
    "calculatedat": datetime.datetime(2024, 9, 8, 23, 0, tzinfo=tzutc()),
    "unit_of_measurement": "%",
    "attribution": "Data provided by AICO HomeLINK",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR Abandonment",
}
AIRQUALITY = {
    "state_class": "measurement",
    "type": "room_insight",
    "insightid": "c85d57a6-acfa-46f1-905d-2bca12997c92",
    "risklevel": "MEDIUM",
    "calculatedat": datetime.datetime(2024, 9, 8, 23, 0, tzinfo=tzutc()),
    "unit_of_measurement": "%",
    "attribution": "Data provided by AICO HomeLINK",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR Airquality",
}
COLDHOMES = {
    "state_class": "measurement",
    "type": "room_insight",
    "insightid": "c6e32e75-39c9-462f-85bf-f6b3d2826d75",
    "risklevel": "LOW",
    "calculatedat": datetime.datetime(2024, 9, 8, 23, 0, tzinfo=tzutc()),
    "unit_of_measurement": "%",
    "attribution": "Data provided by AICO HomeLINK",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR Coldhomes",
}
EXCESSHEAT = {
    "state_class": "measurement",
    "type": "room_insight",
    "insightid": "b62df70f-d407-442f-9289-ff4f3fec2978",
    "risklevel": "LOW",
    "calculatedat": datetime.datetime(2024, 9, 8, 23, 0, tzinfo=tzutc()),
    "unit_of_measurement": "%",
    "attribution": "Data provided by AICO HomeLINK",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR Excessheat",
}
HEATLOSS = {
    "state_class": "measurement",
    "type": "room_insight",
    "insightid": "9d5cf56b-3a59-4f2d-9389-2d2f5eb0b900",
    "risklevel": "LOW",
    "calculatedat": datetime.datetime(2024, 9, 8, 23, 0, tzinfo=tzutc()),
    "unit_of_measurement": "%",
    "attribution": "Data provided by AICO HomeLINK",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR Heatloss",
}
VENTILATION = {
    "state_class": "measurement",
    "type": "room_insight",
    "insightid": "ffc4875e-38e6-4bc5-b635-a757f92d0255",
    "risklevel": "LOW",
    "calculatedat": datetime.datetime(2024, 9, 8, 23, 0, tzinfo=tzutc()),
    "unit_of_measurement": "%",
    "attribution": "Data provided by AICO HomeLINK",
    "friendly_name": "DUMMY_USER_My_House HALLWAY1 ENVCO2SENSOR Ventilation",
}
