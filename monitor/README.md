# Japantown Prepared Monitor
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/mildebrandt/japantown_prepared/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## TL;DR
```
git clone git@github.com:mildebrandt/japantown_prepared.git
cd japantown_prepared/monitor
pip install -r requirements.txt
python monitor.py
```

## Overview
This script will collect data on the water levels and air quality around San Jose, taken from the following sources:

Air quality:
https://www.baaqmd.gov/about-air-quality/current-air-quality/air-monitoring-data/#/aqi-highs

Water levels:
https://alert.valleywater.org/map?p=map

Running the script will return either a "levels normal" message or a detailed description of what has triggered an alert. The `config.yaml` file will tell the monitor what stations to look at for information. Here is an example:

```
cache_directory: "~/.cache/japantown_prepared_monitor"

valleywater:
  watershed: Guadalupe
  station_ids:
    - 5060
  cache_timeout_in_minutes: 15

baaqmd:
  authkey: JHRFBG84T548HBNFD38F0GIG05GJ48
  cache_timeout_in_minutes: 15
  zone: "Santa Clara Valley"
  station_id: 7032
```

#### valleywater config:
|Item|Description|
|-|-|
|watershed|The name of the watershed to monitor. **Optional**|
|station_ids|The IDs of the stations to monitor. **Optional**|
|cache_timeout_in_minutes|The number of minutes to cache the previous call to the API.|

If neither `watershed` nor `station_ids` are provided, then all stations are monitored. If both `watershed` and `station_ids` are provided, then all the stations within the watershed and the additional stations in `station_ids` are monitored.

#### baaqmd config:
|Item|Description|
|-|-|
|authkey|The authkey for the API.|
|station_id|The ID of the station to monitor.|
|zone|The zone where the station resides.|
|cache_timeout_in_minutes|The number of minutes to cache the previous call to the API.|

Currently, the tool is limited to monitoring only one air quality station.
