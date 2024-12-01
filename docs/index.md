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
  - Electricity/Gas Consumption
  - Electricity/Gas Tariff

# Installation
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RogerSelwyn&repository=AICO_HomeLINK)

You can either use HACS or install the component manually:
- **HACS** - [Home Assistant Community Store (HACS)](https://hacs.xyz/) - search for and install AICO HomelINK

- **Manual** - Put the files from `/custom_components/homelink/` in your folder `<config directory>/custom_components/homelin/`

## Configuration
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=homelink)

<details markdown="1"><summary>Manual configuration</summary>
  
If the above My button doesn't work, you can also perform the following steps manually: 
* Browse to your Home Assistant instance.
* Go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations). 
* In the bottom right corner, select the [Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=homelink) button.
* From the list, select AICO HomeLINK.
* Follow the instructions on screen to complete the setup.
  
</details>

### Base Integration
The installation dialogue which will request a Client ID and Secret that you must obtain from the [HomeLINK Dashboard](https://dashboard.live.homelync.io/#/pages/admin/integrations). You will need to have an `admin` account on your dashboard to enable access to the integrations dialogue. If you have a `standard` account you will need to request an admin account from AICO HomeLINK. 

You will need to create a set of credentials by going to the `Access Keys` tab of the integrations dialogue and requesting a `Web Api` credential with the `Standard` scope. Make a note of the credentials generated and enter them into the standard Home Assistant integration installation dialogue. If you input incorrect credentials and it fails to authenticate at setup time, then you will likely need to delete the credentials via the Home Assistant Application Credentials and start again. 

**Note:-** Only one instance of the integration can be installed to Home Assistant. However, all properties and devices you have access to will be exposed.

#### Installation 
| **Name** | **Description**  |
|:---------|:-----------------|
| Client ID | Obtained from HomeLINK Dashboard |
| Client Secret | Obtained from HomeLINK Dashboard |

#### Options - Base
| **Name** | **Description**  |
|:---------|:-----------------|
| Properties | List of properties to create entities for |
| Insights | Enable Insight sensors (if available) |
| MQTT | Enable MQTT |
| HomeLINK MQTT | Use HomeLINK MQTT broker |
| Webhooks | Enable Webhooks |

#### Options - MQTT (HA)
| **Name** | **Description**  |
|:---------|:-----------------|
| Topic | The base subscription for your account |
| Events | Enable MQTT event entities |

#### Options - MQTT (HomeLINK)
| **Name** | **Description**  |
|:---------|:-----------------|
| MQTT Client ID | MQTT Client ID, obtained from HomeLINK Dashboard |
| Username | Obtained from HomeLINK Dashboard |
| Password | Obtained from HomeLINK Dashboard |
| Topic | The base subscription for your account |
| Events | Enable MQTT event entities |

#### Options - Webhooks
| **Name** | **Description**  |
|:---------|:-----------------|
| URL | URL to be used on the HomeLINK Dashboard |

### Insights
If you have environment devices (Ei1020 and Ei1025) installed, then you may optionally enable Insight sensors. These will display the level of various types of risk as a percentage.

### MQTT
If you wish to receive alerts via MQTT (the base integration will update every 30 seconds) to give you quicker notification of alerts and readings, then please follow the instructions here - [MQTT Setup](mqtt.md#setup-and-configuration).

### Webhook
If you wish to receive alerts via Webhook (the base integration will update every 30 seconds) to give you quicker notification of alerts and readings, then please follow the instructions here - [Webhook Setup](webhook.md#setup-and-configuration).

## Removing the integration

This integration follows standard integration removal. Remember to remove via HACS as well.

### To remove an integration instance from Home Assistant

1. Go to [**Settings** > **Devices & services**](https://my.home-assistant.io/redirect/integrations) and select the integration card.
2. From the list of devices, select the integration instance you want to remove.
3. Next to the entry, select the three-dot menu. Then, select **Delete**.

After deleting the integration, go to the app of the manufacturer and remove the Home Assistant integration from there as well.

