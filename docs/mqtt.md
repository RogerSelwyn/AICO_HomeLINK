---
title: MQTT
nav_order: 5
---

# MQTT 

## Setup and configuration
If you wish to receive alerts via MQTT (the base integration will update every 30 seconds) to give you quicker notification of alerts, then you will also need to set up an MQTT integration on the `Access Keys` tab of the HomeLINK dashboard.

You may feed the MQTT messages into the integration by two methods:
* HomeLINK MQTT - Simpler to set up, but does not bring the messages onto the HA MQTT message queue where they can be picked up by other integrations and add-ons
* Home Assistant MQTT - Complex to set up, since you must know how to bridge messages on to the HA MQTT broker.

### HomeLINK MQTT

All the information you need is in the MQTTX file that you should download. In the configuration:-
* Turn on `Enable MQTT updates`
* Turn on `Use HomeLINK MQTT broker`
* Client ID - Use clientId
* Username - Use username
* Password - Use password
* Topic - The file provides 5 topics. Please just use the first level (your landlord reference) with `/#` on the end. e.g. `joe_bloggs/reading/#` should be entered as `joe_bloggs/#`

### HA MQTT

It is beyond the scope of this guide to define how you bridge the data onto your HA broker. Some information is provided below, with an example that may help you for the standard HA `Mosquitto Broker`. I personally use the EMQX add-on, which while more GUI based for configuration, has complications around configuring the client_id required by HomeLINK.

All the information you need is in the MQTTX file that you should download. 
* clientId - Used for `local_clientid` (it might be for the remote, I forget)
* username - Used for `remote_username`
* password - Used for `remote_password`
* host/port - Use for `address`
* topic - The file provides 5 topics. Please just use the first level (your landlord reference) with `/#` on the end. e.g. `joe_bloggs/reading/#` should be entered as `joe_bloggs/#`

```
connection homelink
address conduit.live.homelync.io:8883
remote_username externalmqtt:joe_bloggs-hassio
remote_password obscurepassword
topic joe_bloggs/# in 0
bridge_capath /etc/ssl/certs/
local_clientid joe_bloggs_obscure
remote_clientid joe_bloggs_obscure
```

Once you have the data available to Home Assistant on your MQTT broker, you can configure the options for the HomeLINK integration to enable MQTT. In the configuration:-
* Turn on `Enable MQTT updates`
* Turn off `Use HomeLINK MQTT broker`
* Topic - Enter the same topic as above. If you have rewritten the topic to an alternative root, then please make sure you include this in the root field. For instance if `joe_bloggs/#` has been written to `homelink/joe_bloggs/#`, then enter the same value into the text box.

## Processing

The AICO HomeLINK integration raises Home Assistant events based on incoming [MQTT messages](https://help.live.homelync.io/hc/en-us/articles/7278758696465-MQTT-Topic-Structure). It will raise the event as `homelink_{message_type}` or `homelink_unknown` based on the message type received in the MQTT topic structure. Plus it outputs a debug entry. The event will be similar to the below:

```
event_type: homelink_alert
data:
  sub_type: device
  device_info:
    identifiers:
      - - homelink
        - device
        - D6FCD4F0
    name: JOE_BLOGGS_Home UTILITY FIRECOALARM
    via_device:
      - homelink
      - property
      - JOE_BLOGGS_Home
    manufacturer: Ei
    model: Ei3028 (FIRECOALARM)
  payload:
    category: DEVICE
    eventId: 12323588-534c-4e82-bfe5-345fed4505be
    resolvedDate: null
    resolvingEventId: null
    resolvingEventTypeDescription: null
    resolvingEventTypeId: null
    resolvingEventTypeName: null
    statusId: ACTIVE
    description: "D6FCD4F0 in location Hallway 1: Fire Alarm Activated"
    deviceId: ""
    devicePhySerialNumber: D6FCD4F0
    deviceSerialNumber: D6FCD4F0
    eventTypeId: CO_ALARM
    eventTypeName: Fire alarm activated
    landlordReference: ""
    location: HALLWAY1
    locationNickname: Back Door
    manufacturerReference: EI
    propertyDisplayReference: ""
    propertyId: ""
    propertyReference: ""
    raisedDate: "2023-12-31T15:27:33Z"
    room: Hallway 1
    severity: HIGH
    sourceId: EI
    sourceModel: EI3016
    sourceModelType: COALARM
    title: Fire Alarm Activated
    __IDENTITY: ""
    action: ADD
    actionTimestamp: "2023-12-31T15:27:33.000Z"
origin: LOCAL
time_fired: "2023-09-27T08:25:24.155962+00:00"
context:
  id: 01HBAVWADVWNKN23XXA4WDXFZR
  parent_id: null
  user_id: null
```

In addition, if the message type is `alert`, `device` or `property` it will trigger an update to all entities to ensure they reflect current state.

Also, it will set an `alertstatus` on the alert listed against a device showing what state it is in. This will show for example `FIRE_ALARM` in the initial state and `CANCEL` when the alarm has been silenced.