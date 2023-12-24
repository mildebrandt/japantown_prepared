# Japantown Prepared Monitor
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/mildebrandt/japantown_prepared/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## TL;DR
```
git clone git@github.com:mildebrandt/japantown_prepared.git
cd japantown_prepared/monitor
python3 -m venv venv
. ./venv/bin/activate
pip install .
japantown_prepared_monitor
```

## Overview
This script will collect data on the water levels and air quality around San Jose, taken from the following sources:

Air quality:
https://www.baaqmd.gov/about-air-quality/current-air-quality/air-monitoring-data/#/aqi-highs

Water levels:
https://alert.valleywater.org/map?p=map

Running the script will return either a "levels normal" message or a detailed description of what has triggered an alert. The `config.yaml` file will tell the monitor what stations to look at for information. Here is an example:

```
global:
  cache_directory: "~/.cache/japantown_prepared_monitor"
  cache_expiry_in_seconds: 600

valleywater:
  watershed: Guadalupe
  station_ids:
    - 5060

baaqmd:
  authkey: JHRFBG84T548HBNFD38F0GIG05GJ48
  zones: 
    - name: "Santa Clara Valley"
      station_ids: 
        - 7032
```

String items in the `config.yaml` file can be overridden from the environment using the format `MONITOR__{section}__{attribute}`. For example, to override the `authkey` attribute in the `baaqmd` section, set the `MONITOR__baaqmd__authkey` environment variable.

#### valleywater config:
|Item|Description|
|-|-|
|watershed|The name of the watershed to monitor. **Optional**|
|station_ids|The IDs of the stations to monitor. **Optional**|

If neither `watershed` nor `station_ids` are provided, then all stations are monitored. If both `watershed` and `station_ids` are provided, then all the stations within the watershed and the additional stations in `station_ids` are monitored.

#### baaqmd config:
<table>
<tr>
<td><b>Item</b></td>
<td><b>Description</b></td>
</tr>
<td>authkey</td>
<td>The authkey for the API.</td>
</tr>
<tr>
<td>alert_levels</td>
<td>
```yaml
alert_levels:
    0: "Good"
    101: "Unhealthy for sensitive groups"
    151: "Unhealthy"
    201: "Very unhealthy"
    301: "Hazardous"
```
</td>
</tr>
<tr>
<td>zones</td>
<td>The zones to monitor.</td>
</tr>
</table

#### baaqmd zone config:
|Item|Description|
|-|-|
|station_ids|The IDs of the stations to monitor. **Optional**|

The `zones` are manditory. The `station_ids` are optional. If no station IDs are provided, all stations within that zone will be monitored.

## Adding new data sources
Each data source has its own file in the `data_sources` directory. In that file is a class which extends from the `DataSource` class. The name of the class is used to load the configuration from the `config.yaml` file. For example, in the `water_levels_valleywater.py` file, there's a class called `valleywater`. In the `config.yaml`, there's a corresponding attribute named `valleywater`. All the attributes under that will be available as instance variables. It's up to each class to implement the `get_status()` method and return the following structure:
```
{
    "message": ""  # A formatted string to show to the user.
    "alerts": []   # An array of dictionaries with attributes of interest
                   #   from several montioring stations if applicable.
}
```

## Development
You need `setuptools >= 68` and `pip >= 23` in order to install an "editable" package. Run the following commands to update your packages:
```bash
pip install --upgrade setuptools
python -m pip install --upgrade pip
```

Then run the following to install the editable package:
```bash
pip install -e .
```

At this point, you can make changes to the code and have them apply immediately when running the `japantown_prepared_monitor` script.

Packaging is done with `flit` and all metadata is found in the `pyproject.toml` file. To build and package, use the python build command from the `japantown_prepared/monitor` directory (the same directory as the `pyproject.toml` file):

```bash
python -m build
```
