# Japantown Prepared Monitor

## TL;DR
```
git clone git@github.com:mildebrandt/japantown_prepared.git
cd japantown_prepared/monitor
pip install -r requirements.txt
python monitor
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

water:
  url: https://alertdata.valleywater.org/
  watershed: Guadalupe
  station_ids:
    - 5060
  cache_timeout_in_minutes: 15

air:
  url: https://baaqmdrtaqd.azurewebsites.net/
  authkey: JHRFBG84T548HBNFD38F0GIG05GJ48
  cache_timeout_in_minutes: 15
  zone: "Santa Clara Valley"
  station_id: 7032
```

#### Water config:
|Item|Description|
|-|-|
|url|The main API url to query.|
|watershed|The name of the watershed to monitor. **Optional**|
|station_ids|The IDs of the stations to monitor. **Optional**|
|cache_timeout_in_minutes|The number of minutes to cache the previous call to the API.|

If neither `watershed` nor `station_ids` are provided, then all stations are monitored. If both `watershed` and `station_ids` are provided, then all the stations within the watershed and the additional stations in `station_ids` are monitored.

#### Air config:
|Item|Description|
|-|-|
|url|The main API url to query.|
|authkey|The authkey for the API.|
|station_id|The ID of the station to monitor.|
|zone|The zone where the station resides.|
|cache_timeout_in_minutes|The number of minutes to cache the previous call to the API.|

Currently, the tool is limited to monitoring only one air quality station.