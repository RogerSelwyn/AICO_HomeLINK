---
title: MQTT
nav_order: 5
---

# MQTT Processing

The AICO HomeLINK integration raises Home Assistant events based on incoming [MQTT messages](https://help.live.homelync.io/hc/en-us/articles/7278758696465-MQTT-Topic-Structure). It will raise the event as `homelink_{message_type}` or `homelink_unknown` based on the message type received in the MQTT topic structure. Plus it outputs a debug entry.

In addition, if the message type is `alert` it will trigger an update to all entities to ensure they reflect current state.

At this time no further processing is done on MQTT messages. This will be improved as I receive details of what the MQTT messages look like, which is not currently available to me.