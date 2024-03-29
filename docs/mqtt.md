---
title: MQTT
nav_order: 5
---

# MQTT 

## Setup and configuration
If you wish to:
* Receive alerts via MQTT (the base integration will update every 30 seconds) to give you quicker notification of alerts
* Receive readings from environment sensors 

You will also need to set up an MQTT integration on the `Access Keys` tab of the HomeLINK dashboard.

You may feed the MQTT messages into the integration by two methods:
* HomeLINK MQTT - Simpler to set up, but does not bring the messages onto the HA MQTT message queue where they can be picked up by other integrations and add-ons
* Home Assistant MQTT - Complex to set up, since you must know how to bridge messages on to the HA MQTT broker.

### HomeLINK MQTT

All the information you need is in the MQTTX file that you should download. In the configuration:-
* Turn on `Enable MQTT`
* Turn on `Use HomeLINK MQTT broker`
* Press `Next` and configure HomeLINK MQTT settings:-
  * Client ID - Use clientId
  * Username - Use username
  * Password - Use password
  * Topic - The file provides 5 topics. Please just use the first level (your landlord reference) with `/#` on the end. e.g. `joe_bloggs/reading/#` should be entered as `joe_bloggs/#`
* Press `Submit`

### HA MQTT

It is beyond the scope of this guide to define how you bridge the data onto your HA broker. I personally use the EMQX add-on and have struggled to get the standard HA Eclipse Mosquitto broker to connect to HomeLINK. If using EMQX you cannot specify the client ID directly, but the connector name is prepended to it, so name the connector in line with your landlord ID (e.g. `joe_bloggs`). At this time, HomeLINK only support MQTT v3.1.1, and you must use an encrypted connection over port 8883.

All the information you need is in the MQTTX file that you should download. Topic - The file provides 5 topics. Please just use the first level (your landlord reference) with `/#` on the end. e.g. `joe_bloggs/reading/#` should be entered as `joe_bloggs/#`

Once you have the data available to Home Assistant on your MQTT broker, you can configure the options for the HomeLINK integration to enable MQTT. In the configuration:-
* Turn on `Enable MQTT`
* Turn off `Use HomeLINK MQTT broker`
* Press `Next` and configure HA MQTT settings:-
  * Topic - Enter the same topic as above. If you have rewritten the topic to an alternative root, then please make sure you include this in the root field. For instance if `joe_bloggs/#` has been written to `homelink/joe_bloggs/#`, then enter the same value into the text box
* Press `Submit`


## Processing

The AICO HomeLINK integration raises Home Assistant events based on incoming [MQTT messages](https://help.live.homelync.io/hc/en-us/articles/7278758696465-MQTT-Topic-Structure) for the majority of messages (at this time `insight`, `insightcomponent` and `notification` are ignored). It will raise the event as `homelink_{message_type}` or `homelink_unknown` based on the message type received in the MQTT topic structure. Plus it outputs a debug entry. The event will be similar to the below:

```
event_type: homelink_alert
data:
  sub_type: device
  topic_tree:
    - alert
    - active
    - joe_bloggs_home
    - c3cec7fb-d6fcd4f0
    - co-alarm
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

Additionally:
* If the message type is `reading` it will update the relevant sensors status and `readingdate` attribute.
* If the message type is `alert`, `device` or `property` it will trigger an update to all entities to ensure they reflect current state.
