"""Constants for HomeLINK integration."""
from enum import StrEnum

ALARMS_NONE = "None"
ATTRIBUTION = "Data provided by AICO HomeLINK"

ATTR_ADDRESS = "address"
ATTR_ALARMED_DEVICES = "alarmed_devices"
ATTR_ALERTID = "alertid"
ATTR_ALERTS = "alerts"
ATTR_ALERTSTATUS = "alertstatus"
ATTR_CATEGORY = "category"
ATTR_CONNECTIVITYTYPE = "connectivitytype"
ATTR_DATACOLLECTIONSTATUS = "datacollectionstatus"
ATTR_DESCRIPTION = "description"
ATTR_DEVICE = "device"
ATTR_DEVICE_INFO = "device_info"
ATTR_EVENTTYPE = "eventtype"
ATTR_HOMELINK = "HomeLINK"
ATTR_INSTALLATIONDATE = "installationdate"
ATTR_INSTALLEDBY = "installedby"
ATTR_INTEGRATIONS_URL = "integrations_url"
ATTR_LASTSEENDATE = "lastseendate"
ATTR_LASTTESTDATE = "lasttesteddate"
ATTR_PAYLOAD = "payload"
ATTR_PROPERTY = "property"
ATTR_RAISEDDATE = "raiseddate"
ATTR_REPLACEDATE = "replacedate"
ATTR_REFERENCE = "reference"
ATTR_SERIALNUMBER = "serialnumber"
ATTR_SEVERITY = "severity"
ATTR_SIGNALSTRENGTH = "signalstrength"
ATTR_SUB_TYPE = "sub_type"
ATTR_TAGS = "tags"
ATTR_TOPIC = "topic_tree"
ATTR_TYPE = "type"

CONF_ERROR_CREDENTIALS = "invalid_credentials"
CONF_ERROR_TOPIC = "invalid_topic"
CONF_ERROR_UNAVAILABLE = "server_unavailable"

CONF_MQTT_CLIENT_ID = "mqtt_client_id"
CONF_MQTT_ENABLE = "mqtt_enable"
CONF_MQTT_HOMELINK = "mqtt_homelink"
CONF_MQTT_TOPIC = "mqtt_topic"

COORD_ALERTS = "alerts"
COORD_DEVICES = "devices"
COORD_GATEWAY_KEY = "gateway_key"
COORD_PROPERTIES = "properties"
COORD_PROPERTY = "property"
DASHBOARD_URL = "https://dashboard.live.homelync.io/#/pages/portfolio/one-view"
DATA_MQTT = "mqtt"
DOMAIN = "homelink"

ENTITY_NAME_LASTTESTDATE = "Last Tested Date"
ENTITY_NAME_REPLACEDATE = "Replace By Date"

HOMELINK_ADD_DEVICE = f"{DOMAIN}_add_device"
HOMELINK_ADD_PROPERTY = f"{DOMAIN}_add_property"
HOMELINK_MQTT_MESSAGE = "{domain}_mqtt_{key}"

HOMELINK_MQTT_PROTOCOL = "tcp"
HOMELINK_MQTT_KEEPALIVE = 60
HOMELINK_MQTT_PORT = 8883
HOMELINK_MQTT_SERVER = "conduit.live.homelync.io"


INTEGRATIONS_URL = "https://dashboard.live.homelync.io/#/pages/admin/integrations"

KNOWN_DEVICES_ID = "id"
KNOWN_DEVICES_CHILDREN = "children"

MODELTYPE_COALARM = "COALARM"
MODELTYPE_EIACCESSORY = "EIACCESSORY"
MODELTYPE_FIREALARM = "FIREALARM"
MODELTYPE_FIRECOALARM = "FIRECOALARM"
MODELTYPE_GATEWAY = "GATEWAY"
MODELTYPE_PROBLEMS = [MODELTYPE_EIACCESSORY, MODELTYPE_GATEWAY]

MQTT_ACTIONTIMESTAMP = "actionTimestamp"
MQTT_CLASSIFIER_ACTIVE = "active"
MQTT_DEVICESERIALNUMBER = "deviceSerialNumber"
MQTT_EVENTID = "eventId"
MQTT_EVENTTYPEID = "eventTypeId"
MQTT_RAISEDDATE = "raisedDate"

STATUS_GOOD = "GOOD"
STATUS_NOT_GOOD = "NOT_GOOD"

UNKNOWN = "RESOLVED/UNKNOWN"


class HomeLINKMessageType(StrEnum):
    """HomeLINK Message Types."""

    MESSAGE_ALERT = "alert"
    MESSAGE_DEVICE = "device"
    MESSAGE_EVENT = "event"
    MESSAGE_INSIGHT = "insight"
    MESSAGE_NOTIFICATION = "notification"
    MESSAGE_PROPERTY = "property"
    MESSAGE_READING = "reading"
    MESSAGE_UNKNOWN = "unknown"
