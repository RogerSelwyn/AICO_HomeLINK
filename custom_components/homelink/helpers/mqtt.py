"""MQTT client for HomeLINK."""
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
    CONF_ERROR_CREDENTIALS,
    CONF_ERROR_TOPIC,
    CONF_ERROR_UNAVAILABLE,
    CONF_MQTT_CLIENT_ID,
    CONF_MQTT_TOPIC,
    DOMAIN,
    HOMELINK_MQTT_KEEPALIVE,
    HOMELINK_MQTT_MESSAGE,
    HOMELINK_MQTT_PORT,
    HOMELINK_MQTT_PROTOCOL,
    HOMELINK_MQTT_SERVER,
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

    def _on_socket_open(
        self, client, userdata, sock
    ):  # pylint: disable=unused-argument
        self._socket_open = True

    @callback
    def _on_connect(
        self, client, userdata, flags, ret, properties=None
    ):  # pylint: disable=unused-argument
        if not self._error:
            _LOGGER.debug("HomeLINK MQTT connected with result code: %s", ret)
        if ret == paho_mqtt.CONNACK_ACCEPTED:
            if self._error == CONNECT_ERROR:
                self._error = False
            self._connected = True
            client.subscribe(self._mqtt_root_topic, qos=2)

    @callback
    def _on_disconnect(
        self, client, userdata, ret, properties=None
    ):  # pylint: disable=unused-argument
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
        _forward_message(self._hass, msg, self._root_topic, self._properties)

    @callback
    def _on_subscribe(
        self, client, userdata, mid, granted_qos
    ):  # pylint: disable=unused-argument
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

    async def async_start(self):
        """Start up the MQTT client."""
        async_when_setup(self._hass, MQTT_DOMAIN, self._async_subscribe)

    @callback
    async def _async_subscribe(
        self, hass: HomeAssistant, component  # pylint: disable=unused-argument
    ):
        _LOGGER.debug("HA MQTT subscribed: %s", self._root_topic)
        await mqtt.async_subscribe(
            self._hass, self._mqtt_root_topic, self._async_message_received, qos=2
        )

    @callback
    async def _async_message_received(self, msg):
        _forward_message(self._hass, msg, self._root_topic, self._properties)


def _forward_message(hass, msg, root_topic, properties):
    if key := _extract_property(msg.topic, root_topic, properties):
        event = HOMELINK_MQTT_MESSAGE.format(domain=DOMAIN, key=key).lower()
        dispatcher_send(hass, event, msg)


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