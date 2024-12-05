"""Constants for HomeLINK integration."""

from datetime import timedelta
from enum import StrEnum

ALARMS_NONE = "None"
ALARMTYPE_ALARM = "alarm"
ALARMTYPE_ENVIRONMENT = "environment"
APPLIESTO_PROPERTY = "PROPERTY"
APPLIESTO_ROOM = "ROOM"
ATTRIBUTION = "Data provided by AICO HomeLINK"

ATTR_ACTIONTIMESTAMP = "actiontimestamp"
ATTR_ADDRESS = "address"
ATTR_ALARM = "property element"
ATTR_ALARMED_DEVICES = "alarmed_devices"
ATTR_ALARMED_ROOMS = "alarmed_rooms"
ATTR_ALERTID = "alertid"
ATTR_ALERTS = "alerts"
ATTR_CALCULATEDAT = "calculatedat"
ATTR_CATEGORY = "category"
ATTR_CONNECTIVITYTYPE = "connectivitytype"
ATTR_DATACOLLECTIONSTATUS = "datacollectionstatus"
ATTR_DESCRIPTION = "description"
ATTR_DEVICE = "device"
ATTR_DEVICE_INFO = "device_info"
ATTR_EVENTTYPE = "eventtype"
ATTR_EXTERNAL_URL = "external_url"
ATTR_HOMELINK = "HomeLINK"
ATTR_ID = "id"
ATTR_INSIGHT_ROOM = "room_insight"
ATTR_INSIGHT_PROPERTY = "property_insight"
ATTR_INSIGHTID = "insightid"
ATTR_INSTALLATIONDATE = "installationdate"
ATTR_INSTALLEDBY = "installedby"
ATTR_INTEGRATIONS_URL = "integrations_url"
ATTR_LASTSEENDATE = "lastseendate"
ATTR_LASTTESTDATE = "lasttesteddate"
ATTR_METADATA = "metadata"
ATTR_MODEL = "model"
ATTR_MODELTYPE = "modeltype"
ATTR_OPERATIONALSTATUS = "operationalstatus"
ATTR_PAYLOAD = "payload"
ATTR_PROPERTY = "property"
ATTR_RAISEDDATE = "raiseddate"
ATTR_READING = "reading"
ATTR_READINGDATE = "readingdate"
ATTR_READINGS = "readings"
ATTR_REPLACEDATE = "replacedate"
ATTR_REFERENCE = "reference"
ATTR_RISKLEVEL = "risklevel"
ATTR_SERIALNUMBER = "serialnumber"
ATTR_SEVERITY = "severity"
ATTR_SIGNALSTRENGTH = "signalstrength"
ATTR_SOURCE = "source"
ATTR_STATUS = "status"
ATTR_STATUSID = "statusid"
ATTR_SUB_TYPE = "sub_type"
ATTR_TAGS = "tags"
ATTR_TOPIC = "topic_tree"
ATTR_TYPE = "type"

CATEGORY_INSIGHT = "INSIGHT"

CONF_ERROR_AUTHENTICATING = "error_authenticating"
CONF_ERROR_CREDENTIALS = "invalid_credentials"
CONF_ERROR_TOPIC = "invalid_topic"
CONF_ERROR_UNAVAILABLE = "server_unavailable"
CONF_EVENT_ENABLE = "event_enable"
CONF_INVALID_APPLICATION_CREDENTIALS = "invalid_application_credentials"

CONF_INSIGHTS_ENABLE = "insights_enable"
CONF_MQTT_CLIENT_ID = "mqtt_client_id"
CONF_MQTT_ENABLE = "mqtt_enable"
CONF_MQTT_HOMELINK = "mqtt_homelink"
CONF_MQTT_TOPIC = "mqtt_topic"

CONF_PROPERTIES = "properties"
CONF_WEBHOOK_ENABLE = "webhook_enable"


COORD_ALERTS = "alerts"
COORD_CONFIG_ENTRY_OPTIONS = "config_entry_options"
COORD_DATA_MQTT = "mqtt"
COORD_DATA_WEBHOOK = "webhook"
COORD_DEVICES = "devices"
COORD_GATEWAY_KEY = "gateway_key"
COORD_INSIGHTS = "insights"
COORD_LOOKUP_EVENTTYPE = "eventtypes"
COORD_PROPERTIES = "properties"
COORD_PROPERTY = "property"
COORD_READINGS = "readings"
DASHBOARD_URL = "https://dashboard.live.homelync.io/#/pages/portfolio/one-view"
DOMAIN = "homelink"

EVENTTYPE_INSIGHT = "INSIGHT"

HOMELINK_ADD_DEVICE = f"{DOMAIN}_add_device"
HOMELINK_ADD_PROPERTY = f"{DOMAIN}_add_property"
HOMELINK_LOOKUP_EVENTTYPE = "eventType"
HOMELINK_MESSAGE_EVENT = "{domain}_event_{key}"
HOMELINK_MESSAGE_MQTT = "{domain}_mqtt_{key}"

HOMELINK_MQTT_PROTOCOL = "tcp"
HOMELINK_MQTT_KEEPALIVE = 60
HOMELINK_MQTT_PORT = 8883
HOMELINK_MQTT_SERVER = "conduit.live.homelync.io"

INTEGRATIONS_URL = "https://dashboard.live.homelync.io/#/pages/admin/integrations"

KNOWN_DEVICES_ID = "id"
KNOWN_DEVICES_CHILDREN = "children"
KNOWN_DEVICES_DEVICEID = "deviceid"
KNOWN_DEVICES_MODEL = "model"

MODELTYPE_COALARM = "COALARM"
MODELTYPE_EIACCESSORY = "EIACCESSORY"
MODELTYPE_ENVCO2SENSOR = "ENVCO2SENSOR"
MODELTYPE_ENVSENSOR = "ENVSENSOR"
MODELTYPE_FIREALARM = "FIREALARM"
MODELTYPE_FIRECOALARM = "FIRECOALARM"
MODELTYPE_GATEWAY = "GATEWAY"
MODELTYPE_SMARTMETERGASELEC = "SMARTMETERGASELEC"
MODELTYPE_SMARTMETERELEC = "SMARTMETERELEC"
MODELTYPE_SMARTMETERGAS = "SMARTMETERGAS"
MODELLIST_ALARMS = [MODELTYPE_FIREALARM, MODELTYPE_FIRECOALARM]
MODELLIST_ENERGY = [
    MODELTYPE_SMARTMETERGASELEC,
    MODELTYPE_SMARTMETERELEC,
    MODELTYPE_SMARTMETERGAS,
]
MODELLIST_ENVIRONMENT = [MODELTYPE_ENVCO2SENSOR, MODELTYPE_ENVSENSOR]
MODELLIST_PROBLEMS = [MODELTYPE_EIACCESSORY, MODELTYPE_GATEWAY]

MQTT_ACTIONTIMESTAMP = "actionTimestamp"
MQTT_CATEGORY = "category"
MQTT_DEVICESERIALNUMBER = "deviceSerialNumber"
MQTT_EVENTTYPEID = "eventTypeId"
MQTT_INSIGHTID = "insightId"
MQTT_READINGDATE = "readingDate"
MQTT_SEVERITY = "severity"
MQTT_SOURCEID = "sourceId"
MQTT_SOURCEMODEL = "sourceModel"
MQTT_SOURCEMODELTYPE = "sourceModelType"
MQTT_STATUSID = "statusId"
MQTT_VALUE = "value"

READINGS_CO2 = "co2readings"
READINGS_HUMIDITY = "humidityreadings"
READINGS_TEMPERATURE = "temperaturereadings"
READINGS_SENSOR_CO2 = "environment-co2-indoor"
READINGS_SENSOR_ELECTRIC = "electricity-power-hour"
READINGS_SENSOR_ELECTRIC_TARIFF = "tariff-electricity-power-hour"
READINGS_SENSOR_GAS = "gas-power-hour"
READINGS_SENSOR_GAS_TARIFF = "tariff-gas-power-hour"
READINGS_SENSOR_HUMIDITY = "environment-humidity-indoor"
READINGS_SENSOR_TEMPERATURE = "environment-temperature-indoor"
READINGS_ENVIRONMENT = {
    READINGS_CO2: READINGS_SENSOR_CO2,
    READINGS_HUMIDITY: READINGS_SENSOR_HUMIDITY,
    READINGS_TEMPERATURE: READINGS_SENSOR_TEMPERATURE,
}

RETRIEVAL_INTERVAL_READINGS = timedelta(minutes=5)

SENSOR_TRANSLATION_KEY = {
    READINGS_SENSOR_ELECTRIC: "electricity",
    READINGS_SENSOR_GAS: "gas",
    READINGS_SENSOR_ELECTRIC_TARIFF: "electricity_tariff",
    READINGS_SENSOR_GAS_TARIFF: "gas_tariff",
}

STATUS_GOOD = "GOOD"
STATUS_NOT_GOOD = "NOT_GOOD"

WEBHOOK_ACTION = "action"
WEBHOOK_DEVICECOUNT = "deviceCount"
WEBHOOK_DEVICESERIALNUMBER = "deviceSerialNumber"
WEBHOOK_NAME = "homelink"
WEBHOOK_NOTIFICATIONID = "notificationId"
WEBHOOK_PROPERTY_REFERENCE = "propertyReference"
WEBHOOK_READINGTYPEID = "readingTypeId"
WEBHOOK_REPLACEBYDATE = "replaceByDate"
WEBHOOK_STATUSID = "statusId"


class HomeLINKMessageType(StrEnum):
    """HomeLINK Message Types."""

    MESSAGE_ALERT = "alert"
    MESSAGE_DEVICE = "device"
    MESSAGE_EVENT = "event"
    MESSAGE_INSIGHT = "insight"
    MESSAGE_INSIGHTCOMPONENT = "insightcomponent"
    MESSAGE_NOTIFICATION = "notification"
    MESSAGE_PROPERTY = "property"
    MESSAGE_READING = "reading"
    MESSAGE_UNKNOWN = "unknown"
