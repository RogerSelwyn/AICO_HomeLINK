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
If you wish to receive alerts via MQTT (the base integration will update every 30 seconds) to give you quicker notification of alerts, then please follow the instructions here [MQTT](#mqtt)


