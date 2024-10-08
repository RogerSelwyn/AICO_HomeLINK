---
title: Home
nav_order: 1
---

# AICO HomeLINK integration for Home Assistant

The `homelink` platform allows you to view the status of your AICO alarm system. Note that you need an AICO HomeLINK dashboard account with Landlord access to be able to create the credentials needed to use this integration.

This table provides a list of AICO 1000 and 3000 series devices and their support status. It is possible that other RadioLINK devices will also work, but these have not been tested at all:

| **Model No** | **Sensor Type**  |**Model Type**    |**Supported** | **Notes**                   |
|:-------------|:-----------------|:-----------------|:------------:|:----------------------------|
| Ei1000G      | Gateway          | GATEWAY          | True         | Required                    |
| Ei1020       | Condensation, Damp, Mould |         | False        | It may work, but untested   |
| Ei1025       | Condensation, Damp, Mould, Air | ENVCO2SENSOR | True |                           |
| Ei3014       | Heat             | FIREALARM        | True         |                             |
| Ei3016       | Smoke            | FIREALARM        | True         |                             |
| Ei3018       | CO               |                  | False        | It may work, but untested   |
| Ei3024       | Heat, Smoke      |                  | False        | It may work, but untested   |
| Ei3028       | CO, Heat         | FIRECOALARM      | True         |                             |
| Ei3030       | CO, Heat, Smoke  | FIRECOALARM      | True         |                             |
| Ei450        | Alarm Controller | EIACCESSORY      | True         |                             |

These are the presented as the following entity types within Home Assistant:

- Binary Sensor
  - Property status
  - Property Fire/Heat/CO Alarm Overall Status
  - Property Environment Overall Status
  - Device status
- Event 
  - Property last MQTT event (with MQTT enabled)
  - Device last MQTT event (with MQTT enabled)
- Sensor 
  - Device last tested date
  - Device replace by date
  - CO2, Humidity, Temperature
  - Insights (with Insights enabled)

# Installation

You can either use HACS or install the component manually:

- **HACS** - [Home Assistant Community Store (HACS)](https://hacs.xyz/) - search for and install AICO HomelINK

- **Manual** - Put the files from `/custom_components/homelink/` in your folder `<config directory>/custom_components/homelin/`

## Configuration

### Base Integration
Configuration is done via the Home Assistant Integrations UI dialogue which will request a Client ID and Secret that you must obtain from the [HomeLINK Dashboard](https://dashboard.live.homelync.io/#/pages/admin/integrations). You will need to have an `admin` account on your dashboard to enable access to the integrations dialogue. If you have a `standard` account you will need to request an admin account from AICO HomeLINK. 

You will need to create a set of credentials by going to the `Access Keys` tab of the integrations dialogue and requesting a `Web Api` credential with the `Standard` scope. Make a note of the credentials generated and enter them into the standard Home Assistant integration installation dialogue. If you input incorrect credentials and it fails to authenticate at setup time, then you will likely need to delete the credentials via the Home Assistant Application Credentials and start again. 

**Note:-** Only one instance of the integration can be installed to Home Assistant. However, all properties and devices you have access to will be exposed.

### Insights
If you have environment devices (Ei1020 and Ei1025) installed, then you may optionally enable Insight sensors. These will display the level of various types of risk as a percentage.

### MQTT
If you wish to receive alerts via MQTT (the base integration will update every 30 seconds) to give you quicker notification of alerts and readings, then please follow the instructions here - [MQTT Setup](mqtt.md#setup-and-configuration).

### Webhook
If you wish to receive alerts via Webhook (the base integration will update every 30 seconds) to give you quicker notification of alerts and readings, then please follow the instructions here - [Webhook Setup](webhook.md#setup-and-configuration).

