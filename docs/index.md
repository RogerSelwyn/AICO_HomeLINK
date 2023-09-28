---
title: Home
nav_order: 1
---

# AICO HomeLINK integration for Home Assistant

The `homelink` platform allows you to view the status of your AICO alarm system.

There is currently support for the following device types within Home Assistant:

- Binary Sensor
  - Property status
  - Device status
- Sensor 
  - Device last tested date
  - Device replace by date

# Installation

# Installation

You can either use HACS or install the component manually:

- **HACS** - Add this GitHub as a custom repository in HACS, then search for and install AICO HomelINK

- **Manual** - Put the files from `/custom_components/homelink/` in your folder `<config directory>/custom_components/homelin/`

## Configuration

### Base Integration
Configuration is done via the Home Assistant Integrations UI dialogue which will request a Client ID and Secret that you must obtain from the [HomeLINK Dashboard](https://dashboard.live.homelync.io/#/pages/admin/integrations). You will need to have an `admin` account on your dashboard to enable access to the integrations dialogue. If you have a `standard` account you will need to request an admin account from AICO HomeLINK. 

You will need to create a set of credentials by going to the `Access Keys` tab of the integrations dialogue and requesting a `Web Api` credential with the `Standard` scope. Make a note of the credentials generated and enter them into the standard Home Assistant integration installation dialogue. If you input incorrect credentials and it fails to authenticate at setup time, then you will likely need to delete the credentials via the Home Assistant Application Credentials and start again. 

**Note:-** Only one instance of the integration can be installed to Home Assistant. However, all properties and devices you have access to will be exposed.

### MQTT
If you wish to receive alerts via MQTT (the base integration will update every 30 seconds) to give you quicker notification of alerts, then you will also need to set up an MQTT integration on the `Access Keys` tab of the HomeLINK dashboard. You will then need to retrieve this data via your MQTT broker. It is beyond the scope of this guide to define how you add it to your broker. 

All the information you need is in the MQTTX file that you should download. 
* clientId - Used be for `local_clientid` (it might be for the remote, I forget)
* username - Used for `remote_username`
* password - Used for `remote_password`
* host/port - Use for `address`
* topic - The file provides 5 topics. Please just use the first level with `/#` on the end. e.g. `joe_bloggs/reading/#` should be entered as `joe_bloggs/#`

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

Once you have the data available to Home Assistant on your MQTT broker, you can configure the options for the HomeLINK integration to enable MQTT. Please enter the same topic as above. If you have rewritten the topic to an alternative root, then please make sure you include this in the root field. For instance if `joe_bloggs/#` has been written to `homelink/joe_bloggs/#`, then enter the same value into the text box.

