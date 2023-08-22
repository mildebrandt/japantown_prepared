import os
import requests
import logging

from . import DataSource
from .. import cache
from datetime import date
from typing import Optional
from urllib.parse import urljoin


LOG = logging.getLogger(__name__)


class baaqmd(DataSource):
    base_url = "https://baaqmdrtaqd.azurewebsites.net/"

    air_severity = {
        0: "Good",
        51: "Moderate",
        101: "Unhealthy for sensitive groups",
        151: "Unhealthy",
        201: "Very unhealthy",
        301: "Hazardous",
    }

    def load_air_quality(self) -> dict:
        results = cache.get(self.__class__.__name__)

        if results is None:
            url = urljoin(self.base_url, "rtaqd-api/aqiHighData")
            params = {"authkey": self.authkey, "lang": "en"}
            headers = {"content-type": "application/json"}
            data = {
                "dataType": "aqi",
                "dataView": "daily",
                "startDate": str(date.today()),
                "parameterId": 49,
            }
            resp = requests.post(url, params=params, headers=headers, json=data)
            results = resp.json()["results"]
            cache.set(self.__class__.__name__, results)

        return results

    def get_stations(self, zones: Optional[dict] = None) -> dict:
        if zones is None:
            zones = self.zones

        zones_from_source = self.load_air_quality()

        stations = []
        for zone_from_source in zones_from_source:
            for zone in zones:
                if zone["name"] == zone_from_source["Zone Name"]:
                    if "station_ids" in zone:
                        for station in zone_from_source["Stations"]:
                            if station["stationId"] in zone["station_ids"]:
                                station["Zone Name"] = zone_from_source["Zone Name"]
                                stations.append(station)
                    else:
                        for station in zone_from_source["Stations"]:
                            station["Zone Name"] = zone_from_source["Zone Name"]
                            stations.append(station)
        return stations

    def get_status(self) -> dict:
        stations = self.get_stations()

        bad_air_stations = []
        for station in stations:
            # Some stations don't report apiHighAggregate
            if "aqiHighAggregate" not in station:
                continue

            air_severity_label = "Good"
            air_quality_is_degraded = False

            for severity in sorted(self.air_severity.keys()):
                if station["aqiHighAggregate"]["value"] >= severity:
                    air_severity_label = self.air_severity[severity]
                    if severity > 0:
                        air_quality_is_degraded = True
                    continue

            if air_quality_is_degraded:
                bad_air_stations.append(
                    {
                        "name": station["stationName"],
                        "zone": station["Zone Name"],
                        "type": station["aqiHighAggregate"]["parameterName"],
                        "value": station["aqiHighAggregate"]["value"],
                        "status": air_severity_label,
                        "raw_data": station,
                    }
                )

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
                message += f"---\n"
                alerts.append(station)
                hash_strings.append(
                    f"{station['zone']}{station['name']}{station['status']}"
                )
        else:
            message = "Air levels normal."
            hash_strings.append("normal")

        return {
            "message": message,
            "alerts": alerts,
            "hash": self.create_hash(hash_strings),
        }


# Used only for testing
if __name__ == "__main__":
    air_monitor = baaqmd(
        authkey=os.environ["BAAQMD_AUTHKEY"],
        zone="Santa Clara Valley",
        station_id=7032,
    )
    print(air_monitor.get_status()["message"])
