[![Validate with hassfest](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hassfest.yaml) [![HACS Validate](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hacs.yaml/badge.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/actions/workflows/hacs.yaml) [![CodeFactor](https://www.codefactor.io/repository/github/rogerselwyn/AICO_HomeLINK/badge)](https://www.codefactor.io/repository/github/rogerselwyn/AICO_HomeLINK) [![Downloads for latest release](https://img.shields.io/github/downloads/RogerSelwyn/AICO_HomeLINK/latest/total.svg)](https://github.com/RogerSelwyn/AICO_HomeLINK/releases/latest)

![GitHub release](https://img.shields.io/github/v/release/RogerSelwyn/AICO_HomeLINK) [![maintained](https://img.shields.io/maintenance/yes/2023.svg)](#) [![maintainer](https://img.shields.io/badge/maintainer-%20%40RogerSelwyn-blue.svg)](https://github.com/RogerSelwyn) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration) 


# AICO HomeLINK integration for Home Assistant

The `homelink` platform allows you to view the status of your AICO alarm system. This table provides a list of AICO devices and there support status:

| **Model No** | **Sensor Type** |**Model Type**    |**Supported** | **Notes**                   |
|:-------------|:-----------------|:-----------------|:------------:|:----------------------------|
| Ei1000G      | Gateway          | GATEWAY          | True         | Required                    |
| Ei1020       | Condensation, Damp, Mould |         | False        | No support                  |
| Ei1025       | Condensation, Damp, Mould, Air |    | False        | No support                  |
| Ei3014       | Heat             | FIREALARM        | True         |                             |
| Ei3016       | Smoke            | FIREALARM        | True         |                             |
| Ei3018       | CO               |                  | False        | It may work, but untested   |
| Ei3024       | Heat, Smoke      |                  | False        | It may work, but untested   |
| Ei3028       | CO, Heat         | FIRECOALARM      | True         |                             |
| Ei3030       | CO, Heat, Smoke  |                  | False        | It may work, but untested   |
| Ei450        | Alarm Controller | EIACCESSORY      | True         |                             |

These are the presented as the following entity types within Home Assistant:

- Binary Sensor
  - Property status
  - Device status
- Sensor 
  - Device last tested date
  - Device replace by date

### [Buy Me A ~~Coffee~~ Beer 🍻](https://buymeacoffee.com/rogtp)
I work on this integration because I like things to work well for myself and others, and for it to deliver as much as is achievable with the API. Please don't feel you are obligated to donate, but of course it is appreciated.

# Documentation

The full documentation is available here - [AICO HomeLINK](https://rogerselwyn.github.io/AICO_HomeLINK/)

