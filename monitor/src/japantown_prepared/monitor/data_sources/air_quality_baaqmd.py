import os
from datetime import date, timedelta
from typing import Optional
from urllib.parse import urljoin

import requests

from .. import cache, logger
from . import DataSource


def list_to_dict(_list: list, key: str) -> dict:
    return {i[key]: i for i in _list}


class baaqmd(DataSource):
    base_url = "https://baaqmdrtaqd.azurewebsites.net/"

    alert_level = 51  # Value to start alerting
    alert_levels = {
        0: "Good",
        51: "Moderate",
        101: "Unhealthy for sensitive groups",
        151: "Unhealthy",
        201: "Very unhealthy",
        301: "Hazardous",
    }

    def query_air_quality_data(self) -> dict:
        results = cache.get(self.__class__.__name__)

        if results is None:
            logger.debug("No air quality data in cache.")
            # Get the readings and cache them. We get both today's and
            # yesterday's readings since the data from the API seems to
            # be delayed by 1 to 2 hours. Otherwise we'd miss readings
            # around 10:00pm and 11:00pm.
            url = urljoin(self.base_url, "rtaqd-api/aqiHighData")
            params = {"authkey": self.authkey, "lang": "en"}
            headers = {"content-type": "application/json"}
            data = {
                "dataType": "aqi",
                "dataView": "daily",
                "startDate": str(date.today()),
                "parameterId": 49,
            }
            today = requests.post(
                url,
                params=params,
                headers=headers,
                json=data,
                timeout=self.http_timeout,
            ).json()

            data = {
                "dataType": "aqi",
                "dataView": "daily",
                "startDate": str(date.today() - timedelta(days=1)),
                "parameterId": 49,
            }
            yesterday = requests.post(
                url,
                params=params,
                headers=headers,
                json=data,
                timeout=self.http_timeout,
            ).json()
            results = [yesterday, today]

            cache.set(self.__class__.__name__, results)
        else:
            logger.debug("Found air quality data in cache.")

        return results

    def get_latest_value_for_station(self, station) -> dict:
        aqi = {
            "type": None,
            "value": -300,
            "status": None,
        }

        # Some stations don't report aqiHigh
        if "aqiHigh" not in station:
            logger.debug(
                f"Attribute 'aqiHigh' not found for station {station.get('stationName', '')}."
            )
            return aqi

        for aqiHigh in station["aqiHigh"]:
            if aqiHigh["value"] < 0:
                break

            aqi["type"] = aqiHigh["parameterName"]
            aqi["value"] = aqiHigh["value"]

        for severity in sorted(self.alert_levels.keys()):
            if aqi["value"] >= severity:
                aqi["status"] = self.alert_levels[severity]
            else:
                break

        return aqi

    def get_latest_value_by_station(self, zones: Optional[list] = None) -> list:
        if zones is None:
            zones = self.zones

        yesterday, today = self.query_air_quality_data()

        yesterday_zones = list_to_dict(yesterday["results"], "Zone Name")
        today_zones = list_to_dict(today["results"], "Zone Name")

        stations = {}
        for zone in zones:
            # Read yesterday's value and record the latest non-negative value.
            if zone["name"] in yesterday_zones:
                stations_in_zone = list_to_dict(
                    yesterday_zones[zone["name"]]["Stations"], "stationId"
                )

                # Read from all stations if no stations are specified.
                if "station_ids" not in zone:
                    station_ids = stations_in_zone.keys()
                else:
                    station_ids = zone["station_ids"]

                for station_id in station_ids:
                    station = stations_in_zone[station_id]
                    aqi = self.get_latest_value_for_station(station)
                    aqi.update(
                        {
                            "name": station["stationName"],
                            "zone": zone["name"],
                        }
                    )

                    if aqi["value"] >= 0:
                        stations[station_id] = aqi

            # Read today's value and update the latest non-negative value.
            if zone["name"] in today_zones:
                stations_in_zone = list_to_dict(
                    today_zones[zone["name"]]["Stations"], "stationId"
                )

                # Read from all stations if no stations are specified.
                if "station_ids" not in zone:
                    station_ids = stations_in_zone.keys()
                else:
                    station_ids = zone["station_ids"]

                for station_id in station_ids:
                    station = stations_in_zone[station_id]
                    aqi = self.get_latest_value_for_station(station)
                    aqi.update(
                        {
                            "name": station["stationName"],
                            "zone": zone["name"],
                        }
                    )

                    if aqi["value"] >= 0:
                        stations[station_id] = aqi

        return stations.values()

    def get_status(self) -> dict:
        stations = self.get_latest_value_by_station()

        bad_air_stations = []
        for station in stations:
            if station["value"] >= self.alert_level:
                bad_air_stations.append(station)

        alerts = []
        hash_strings = []

        if bad_air_stations:
            message = "ALERT!! The following air quality readings are above threshold levels:\n"

            for station in bad_air_stations:
                message += f"  Name: {station['name']}\n"
                message += f"  Zone: {station['zone']}\n"
                message += f"  Type: {station['type']}\n"
                message += f"  Value: {station['value']}\n"
                message += f"  Status: {station['status']}\n"
                message += "---\n"
                alerts.append(station)
                hash_strings.append(
                    f"{station['zone']}{station['name']}{station['status']}"
                )
        else:
            message = "Air levels normal."
            hash_strings.append("normal")

        result = {
            "message": message,
            "alerts": alerts,
            "hash": self.create_hash(hash_strings),
        }

        logger.debug(f"Current air quality: \n{result}")

        return result


# Used only for testing
if __name__ == "__main__":
    air_monitor = baaqmd(
        authkey=os.environ["BAAQMD_AUTHKEY"],
        zone="Santa Clara Valley",
        station_id=7032,
    )
    print(air_monitor.get_status()["message"])
