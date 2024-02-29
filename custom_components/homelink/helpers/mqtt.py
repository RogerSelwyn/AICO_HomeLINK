"""MQTT client for HomeLINK."""
import json
import logging
import queue

import paho.mqtt.client as paho_mqtt
from homeassistant.components import mqtt
from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.setup import async_when_setup

from ..const import (
    ALARMTYPE_ALARM,
    ALARMTYPE_ENVIRONMENT,
    CONF_ERROR_CREDENTIALS,
    CONF_ERROR_TOPIC,
    CONF_ERROR_UNAVAILABLE,
    CONF_MQTT_CLIENT_ID,
    CONF_MQTT_TOPIC,
    DOMAIN,
    HOMELINK_MESSAGE_EVENT,
    HOMELINK_MESSAGE_MQTT,
    HOMELINK_MQTT_KEEPALIVE,
    HOMELINK_MQTT_PORT,
    HOMELINK_MQTT_PROTOCOL,
    HOMELINK_MQTT_SERVER,
    MQTT_DEVICESERIALNUMBER,
    MQTT_INSIGHTID,
    HomeLINKMessageType,
)

_LOGGER = logging.getLogger(__name__)
MQTT_TIMEOUT = 5
CONNECT_ERROR = "connect"
SUBSCRIBE_ERROR = "subscribe"
OTHER_ERROR = "other"


class HomeLINKMQTT:
    """HomeLINK MQTT client."""

    def __init__(self, hass: HomeAssistant, options, properties=None):
        """Initialise the MQTT client."""
        if properties is None:
            properties = []
        self._hass = hass
        self._options = options
        self._root_topic = options.get(CONF_MQTT_TOPIC)
        self._mqtt_root_topic = f"{self._root_topic}/#"
        self._properties = properties
        self._client = None
        self._result: queue.Queue[bool] = queue.Queue(maxsize=1)
        self._socket_open = False
        self._connected = False
        self._subscribed = False
        self._error = False

    async def async_start(self):
        """Start up the MQTT client."""
        self._client_setup()

        await self._hass.async_add_executor_job(
            self._client.connect,
            HOMELINK_MQTT_SERVER,
            HOMELINK_MQTT_PORT,
            HOMELINK_MQTT_KEEPALIVE,
        )
        self._client.loop_start()
        try:
            self._result.get(timeout=MQTT_TIMEOUT)
            return None
        except queue.Empty:
            if not self._socket_open:
                return CONF_ERROR_UNAVAILABLE
            return CONF_ERROR_TOPIC if self._connected else CONF_ERROR_CREDENTIALS

    async def async_stop(self):
        """Stop up the MQTT client."""
        _LOGGER.debug("HomeLINK MQTT unsubscribed: %s", self._mqtt_root_topic)
        self._client.unsubscribe(self._mqtt_root_topic)
        self._client.disconnect()
        self._client.loop_stop()

    async def async_try_connect(self) -> None:
        """Try the connection."""

        self._client_setup()
        self._client.connect_async(HOMELINK_MQTT_SERVER, HOMELINK_MQTT_PORT)
        self._client.loop_start()
        try:
            self._result.get(timeout=MQTT_TIMEOUT)
            return None
        except queue.Empty:
            if not self._socket_open:
                return CONF_ERROR_UNAVAILABLE
            return CONF_ERROR_TOPIC if self._connected else CONF_ERROR_CREDENTIALS
        finally:
            if self._connected:
                self._client.disconnect()
            self._client.loop_stop()

    def _client_setup(self):
        protocol = paho_mqtt.MQTTv311
        transport = HOMELINK_MQTT_PROTOCOL

        client_id = self._options.get(CONF_MQTT_CLIENT_ID)
        username = self._options.get(CONF_USERNAME)
        password = self._options.get(CONF_PASSWORD)

        self._client = paho_mqtt.Client(
            client_id, protocol=protocol, transport=transport
        )
        self._client.username_pw_set(username, password)
        self._client.tls_set_context()

        self._client.on_socket_open = self._on_socket_open
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe

    def _on_socket_open(self, client, userdata, sock):  # pylint: disable=unused-argument
        self._socket_open = True

    @callback
    def _on_connect(self, client, userdata, flags, ret, properties=None):  # pylint: disable=unused-argument
        if not self._error:
            _LOGGER.debug("HomeLINK MQTT connected with result code: %s", ret)
        if ret == paho_mqtt.CONNACK_ACCEPTED:
            if self._error == CONNECT_ERROR:
                self._error = False
            self._connected = True
            client.subscribe(self._mqtt_root_topic, qos=2)

    @callback
    def _on_disconnect(self, client, userdata, ret, properties=None):  # pylint: disable=unused-argument
        if ret != paho_mqtt.MQTT_ERR_SUCCESS:
            if not self._connected:
                self._check_error(
                    CONNECT_ERROR, "HomeLINK MQTT error during connect. Code:", ret
                )
            elif not self._subscribed:
                self._check_error(
                    SUBSCRIBE_ERROR, "HomeLINK MQTT error during subscribe. Code:", ret
                )
            else:
                self._check_error(
                    OTHER_ERROR, "HomeLINK MQTT disconnected with result code:", ret
                )

    @callback
    def _on_message(self, client, userdata, msg):  # pylint: disable=unused-argument
        _async_forward_message(self._hass, msg, self._root_topic, self._properties)

    @callback
    def _on_subscribe(self, client, userdata, mid, granted_qos):  # pylint: disable=unused-argument
        _LOGGER.debug("HomeLINK MQTT subscribed: %s", self._mqtt_root_topic)
        if self._error == SUBSCRIBE_ERROR:
            self._error = False
        self._result.put("Subscribed")
        self._subscribed = True

    def _check_error(self, error_type, error_message, ret):
        err_type = "unspecified"
        if ret == 5:
            err_type = "Connection refused - Invalid credentials"
        elif ret == 7:
            err_type = "Connection refused - Invalid topic"
        error = f"{error_message} {ret} - {err_type}"
        if self._error != error_type:
            _LOGGER.warning(error)
            self._error = error_type


class HAMQTT:
    """HA MQTT Client."""

    def __init__(self, hass: HomeAssistant, options, properties):
        """Initialise the MQTT client."""
        self._hass = hass
        self._root_topic = options.get(CONF_MQTT_TOPIC)
        self._mqtt_root_topic = f"{self._root_topic}/#"
        self._properties = properties
        self._unsubscribe_task = None

    async def async_start(self):
        """Start up the MQTT client."""
        async_when_setup(self._hass, MQTT_DOMAIN, self._async_subscribe)

    async def async_stop(self):
        """Stop up the MQTT client."""
        _LOGGER.debug("HA MQTT unsubscribed: %s", self._mqtt_root_topic)
        self._unsubscribe_task()

    @callback
    async def _async_subscribe(
        self,
        hass: HomeAssistant,  # pylint: disable=unused-argument
        component,  # pylint: disable=unused-argument
    ):
        _LOGGER.debug("HA MQTT subscribed: %s", self._mqtt_root_topic)
        self._unsubscribe_task = await mqtt.async_subscribe(
            self._hass, self._mqtt_root_topic, self._async_message_received, qos=2
        )

    @callback
    async def _async_message_received(self, msg):
        await _async_forward_message(
            self._hass, msg, self._root_topic, self._properties
        )


async def _async_forward_message(hass, msg, root_topic, properties):
    key = _extract_property(msg.topic, root_topic, properties)
    if not key:
        return

    topic = msg.topic.removeprefix(f"{root_topic}/")
    messagetype = _extract_message_type(topic)

    # Ignore insights, insightcomponents and notifications
    if messagetype in [
        HomeLINKMessageType.MESSAGE_INSIGHT,
        HomeLINKMessageType.MESSAGE_INSIGHTCOMPONENT,
        HomeLINKMessageType.MESSAGE_NOTIFICATION,
    ]:
        return

    payload = json.loads(msg.payload)

    # Device added or deleted, so route to property binary sensor to trigger refresh
    if messagetype in [
        HomeLINKMessageType.MESSAGE_DEVICE,
        HomeLINKMessageType.MESSAGE_PROPERTY,
    ]:
        await _async_property_device_update_message(
            hass, key, topic, payload, messagetype
        )
        return

    # Event Message so route to event sensor
    if messagetype in [HomeLINKMessageType.MESSAGE_EVENT]:
        await _async_event_message(hass, key, payload)
        return

    # Device alert or reading so route to device binary sensor for onward handling
    if (
        messagetype
        in [HomeLINKMessageType.MESSAGE_ALERT, HomeLINKMessageType.MESSAGE_READING]
        and MQTT_DEVICESERIALNUMBER in payload
        and payload[MQTT_DEVICESERIALNUMBER]
    ):
        await _async_device_message(hass, topic, payload, messagetype)
        return

    # Property alert so route to 'alarm' binary sensor
    if messagetype in [HomeLINKMessageType.MESSAGE_ALERT]:
        await _async_alarm_message(hass, key, topic, payload, messagetype)
        return

    _LOGGER.warning("Unknown MQTT message type: %s - %s", messagetype, payload)


async def _async_property_device_update_message(hass, key, topic, payload, messagetype):
    event = HOMELINK_MESSAGE_MQTT.format(
        domain=DOMAIN, key=f"{key}_{ALARMTYPE_ALARM}"
    ).lower()
    dispatcher_send(hass, event, topic, payload, messagetype)


async def _async_event_message(hass, key, payload):
    if MQTT_DEVICESERIALNUMBER in payload and payload[MQTT_DEVICESERIALNUMBER]:
        event = HOMELINK_MESSAGE_EVENT.format(
            domain=DOMAIN, key=payload[MQTT_DEVICESERIALNUMBER]
        ).lower()
    else:
        event = HOMELINK_MESSAGE_EVENT.format(domain=DOMAIN, key=key).lower()
    dispatcher_send(hass, event, payload)


async def _async_alarm_message(hass, key, topic, payload, messagetype):
    if payload[MQTT_INSIGHTID]:
        alarm_type = ALARMTYPE_ENVIRONMENT
    else:
        alarm_type = ALARMTYPE_ALARM
    event = HOMELINK_MESSAGE_MQTT.format(
        domain=DOMAIN, key=f"{key}_{alarm_type}"
    ).lower()
    dispatcher_send(hass, event, topic, payload, messagetype)


async def _async_device_message(hass, topic, payload, messagetype):
    serialnumber = payload[MQTT_DEVICESERIALNUMBER]
    event = HOMELINK_MESSAGE_MQTT.format(domain=DOMAIN, key=serialnumber).lower()
    dispatcher_send(hass, event, payload, topic, messagetype)


def _extract_property(topic, root_topic, properties):
    if not properties:
        return None
    clean_topic = topic.removeprefix(root_topic)
    return next(
        (
            hl_property
            for hl_property in properties
            if hl_property.lower() in clean_topic
        ),
        None,
    )


def _extract_message_type(topic):
    messagetype = topic.split("/")[0]
    messagetypes = [item.value for item in HomeLINKMessageType]
    if messagetype in messagetypes:
        return messagetype

    return HomeLINKMessageType.MESSAGE_UNKNOWN


def _extract_classifier(topic, item):
    return topic.split("/")[item]
