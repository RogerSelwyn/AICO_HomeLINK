---
title: Webooks
nav_order: 10
---

# Webhooks

Note that webhooks will only work if there is internet based access to your Home Assistant instance.

## Setup and configuration

### Home Assistant Setup
You will also need to set up Webhooks on the HomeLINK dashboard. If you wish to:
* Receive alerts via Webhooks (the base integration will update every 30 seconds) to give you quicker notification of alerts
* Receive readings from environment sensors 

All the information you need is in the MQTTX file that you should download. In the configuration:-
* Turn on `Enable Webhooks`
* Click `Next`
* On the next page (depending on whether you have enabled MQTT or not), take a copy of the provided URL
* Press `Submit`

If you want to regenerate the webhook, disable the option and finish configuring the integration. Then re-enable the option and a new webhook will be provided.

### HomeLINK Setup

On the HomeLINK dashboard in the `Integrations` pages, go to the `Webhooks` tab. Using the URL saved from the HA setup as the `Endpoint Url`, register a webhook for each of the following as needed. The `HTTP Method` should be `POST` for all webhooks and the `Success Status Code` should be `200`.

| **Trigger**  | **Actions**         | **Notes**    |
|:-------------|:--------------------|:-------------|
| Property     | Add, Update, Remove |              |
| Device       | Add, Remove         |              |
| Alert        | Add, Resolve        |              |
| Reading      | Add                 | Only if environment sensor installed |
| Notification | Send                | Currently ignored |


## Processing

The AICO HomeLINK integration raises Home Assistant events based on incoming [webhook messages] for the majority of messages (at this time `notification` are ignored). It will raise the event as `homelink_{message_type}` based on the message type identified. Plus it outputs a debug entry. The event will be similar to the below:

```
event_type: homelink_alert
data:
  sub_type: device
  topic_tree:
    - ADD
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
