import datetime
import logging
import os
import requests
import time
import yaml

from pathlib import Path
from urllib.parse import urljoin

LOG = logging.getLogger(__name__)

water_config = None
air_config = None
config_file = "config.yaml"

cache_directory = "~/.cache/cert_monitor"
water_data_file = f"{cache_directory}/water_data.yaml"
air_data_file = f"{cache_directory}/air_data.yaml"


def load_config(config_file=config_file):
    global water_config
    global air_config

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        water_config = config["water"]
        air_config = config["air"]


def create_cache_dir(cache_directory=cache_directory):
    try:
        os.makedirs(os.path.expanduser(cache_directory))
    except FileExistsError:
        pass


def load_water_stations():
    needs_update = False
    path = Path(os.path.expanduser(water_data_file))

    try:
        if (
            time.time() - path.stat().st_mtime
            > water_config["cache_timeout_in_minutes"] * 60
        ):
            needs_update = True
        else:
            with open(path) as f:
                stations = yaml.safe_load(f)
    except (FileExistsError, FileNotFoundError):
        needs_update = True

    if needs_update:
        resp = requests.get(urljoin(water_config["url"], "/Sensor/current"))
        stations = resp.json()["streams"]
        try:
            with open(path, "w") as f:
                yaml.safe_dump(stations, f)
        except FileNotFoundError:
            LOG.warning(f"Unable to save cache file: {path}")

    return stations


def get_water_stations(watershed=None, station_ids=None):
    all_stations = load_water_stations()

    if watershed is None and station_ids is None:
        return all_stations

    stations = []
    for station in all_stations:
        if station_ids is not None:
            if station["gageId"] in station_ids:
                stations.append(station)
        if watershed is not None:
            if station["watershed"] == watershed:
                stations.append(station)

    return stations


def get_water_stations_above_threshold(
    watershed=None, station_ids=None, above_threshold=1
):
    water_severity = {
        0: "Normal",
        1: "Take Action",
        2: "Minor Flooding",
        3: "Moderate Flooding",
        4: "Major Flooding",
    }

    stations = get_water_stations(watershed=watershed, station_ids=station_ids)

    stations_above_threshold = []
    for station in stations:
        is_above_threshold = False
        for threshold in range(above_threshold, 5):
            rated_key = f"th{threshold}_rated"
            direct_key = f"th{threshold}_direct"
            threshold_description_key = f"threshold{threshold}Desc"

            if (station[rated_key] != 0 and station["flow"] > station[rated_key]) or (
                station[direct_key] != 0 and station["stage"] > station[direct_key]
            ):
                extras = {
                    "severity_label": water_severity[threshold],
                    "expected_conditions": station[threshold_description_key],
                }
                is_above_threshold = True

        if is_above_threshold:
            station.update(extras)
            stations_above_threshold.append(station)

    return stations_above_threshold


def load_air_quality():
    needs_update = False
    path = Path(os.path.expanduser(air_data_file))

    try:
        if (
            time.time() - path.stat().st_mtime
            > air_config["cache_timeout_in_minutes"] * 60
        ):
            needs_update = True
        else:
            with open(path) as f:
                results = yaml.safe_load(f)
    except (FileExistsError, FileNotFoundError):
        needs_update = True

    if needs_update:
        url = urljoin(air_config["url"], "rtaqd-api/aqiHighData")
        params = {"authkey": air_config["authkey"], "lang": "en"}
        headers = {"content-type": "application/json"}
        data = {
            "dataType": "aqi",
            "dataView": "daily",
            "startDate": str(datetime.date.today()),
            "parameterId": 49,
        }
        resp = requests.post(url, params=params, headers=headers, json=data)
        results = resp.json()["results"]
        try:
            with open(path, "w") as f:
                yaml.safe_dump(results, f)
        except FileNotFoundError:
            LOG.warning(f"Unable to save cache file: {path}")

    return results


def get_air_quality(station_id=None):
    if station_id is None:
        station_id = air_config["station_id"]

    zones = load_air_quality()

    for zone in zones:
        for station in zone["Stations"]:
            if station["stationId"] == station_id:
                return station


air_severity = {
    0: "Good",
    51: "Moderate",
    101: "Unhealthy for sensitive groups",
    151: "Unhealthy",
    201: "Very unhealthy",
    301: "Hazardous",
}


load_config()

if __name__ == "__main__":
    water_stations = get_water_stations_above_threshold(watershed="Guadalupe")

    if water_stations:
        print("ALERT!! The following water level readings are above threshold levels:")

        for station in water_stations:
            print(f"  Name: {station['name']}")
            print(f"  Watershed: {station['watershed']}")
            print(f"  Status: {station['severity_label']}")
            print(f"  Expected conditions: {station['expected_conditions']}")
            print()
    else:
        print("Water levels normal.")

    air_station = get_air_quality()
    air_severity_label = "Good"
    air_quality_is_degraded = False

    for severity in sorted(air_severity.keys()):
        if air_station["aqiHighAggregate"]["value"] >= severity:
            air_severity_label = air_severity[severity]
            if severity > 0:
                air_quality_is_degraded = True
            continue

    if air_quality_is_degraded:
        print("ALERT!! Air quality is degraded:")
        print(f"  Name: {air_station['stationName']}")
        print(f"  Type: {air_station['aqiHighAggregate']['parameterName']}")
        print(f"  Value: {air_station['aqiHighAggregate']['value']}")
        print(f"  Status: {air_severity_label}")
    else:
        print("Air levels normal.")
