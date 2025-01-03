[![Validate with hassfest](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hassfest.yaml) [![HACS Validate](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hacs.yaml/badge.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hacs.yaml) [![PYTest](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/test.yaml/badge.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/test.yaml) 

[![CodeFactor](https://www.codefactor.io/repository/github/rogerselwyn/AICO_HomeLINK/badge)](https://www.codefactor.io/repository/github/rogerselwyn/AICO_HomeLINK) [![Downloads for latest release](https://img.shields.io/github/downloads/RogerSelwyn/AICO_HomeLINK/latest/total.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/releases/latest) [![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/RogerSelwyn/AICO_HomeLINK/total?label=downloads%40all)](https://github.com/RogerSelwyn/AICO_HomeLINK/releases)


![GitHub release](https://img.shields.io/github/v/release/RogerSelwyn/AICO_HomeLINK) [![maintained](https://img.shields.io/maintenance/yes/2025.svg)](#) [![maintainer](https://img.shields.io/badge/maintainer-%20%40RogerSelwyn-blue.svg)](https://github.com/RogerSelwyn) [![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)


# AICO HomeLINK integration for Home Assistant 

The `homelink` platform allows you to view the status of your AICO alarm system. Note that you need an AICO HomeLINK dashboard account with Landlord access to be able to create the credentials needed to use this integration.

This table provides a list of AICO 1000 and 3000 series devices and their support status. It is possible that 600 series devices will also work, but these have not been tested at all:

| **Model No** | **Sensor Type** |**Model Type**    |**Supported** | **Notes**                   |
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
  - CO2, Humidity, Temperature (with MQTT enabled)

### [Buy Me A Beer 🍻](https://buymeacoffee.com/rogtp)
I work on this integration because I like things to work well for myself and others, and for it to deliver as much as is achievable with the API. Please don't feel you are obligated to donate, but of course it is appreciated.

<a href="https://www.buymeacoffee.com/rogtp" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a> 
<a href="https://www.paypal.com/donate/?hosted_button_id=F7TGHNGH7A526">
  <img src="https://github.com/RogerSelwyn/actions/blob/e82dab9e5643bbb82e182215a748a3024e3e7eac/images/paypal-donate-button.png" alt="Donate with PayPal" height="40"/>
</a>

# Documentation

The full documentation is available here - [AICO HomeLINK](https://rogerselwyn.github.io/AICO_HomeLINK/)

