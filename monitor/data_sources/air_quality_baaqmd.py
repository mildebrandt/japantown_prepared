import requests

from . import DataSource
from datetime import date
from urllib.parse import urljoin


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
        results = self.get_cached_results()

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
            self.save_cached_results(results)

        return results

    def get_air_quality(self, station_id=None) -> dict:
        if station_id is None:
            station_id = self.station_id

        zones = self.load_air_quality()

        for zone in zones:
            for station in zone["Stations"]:
                if station["stationId"] == station_id:
                    return station

    def get_status(self) -> dict:
        air_station = self.get_air_quality()
        air_severity_label = "Good"
        air_quality_is_degraded = False

        for severity in sorted(self.air_severity.keys()):
            if air_station["aqiHighAggregate"]["value"] >= severity:
                air_severity_label = self.air_severity[severity]
                if severity > 0:
                    air_quality_is_degraded = True
                continue

        if air_quality_is_degraded:
            message = "ALERT!! Air quality is degraded:\n"
            message += f"  Name: {air_station['stationName']}\n"
            message += f"  Type: {air_station['aqiHighAggregate']['parameterName']}\n"
            message += f"  Value: {air_station['aqiHighAggregate']['value']}\n"
            message += f"  Status: {air_severity_label}\n"
            alerts = [air_station]
        else:
            message = "Air levels normal."
            alerts = []

        return {
            "message": message,
            "alerts": alerts,
        }


# Used only for testing
if __name__ == "__main__":
    air_monitor = baaqmd(
        authkey="JHRFBG84T548HBNFD38F0GIG05GJ48",
        zone="Santa Clara Valley",
        station_id=7032,
    )
    print(air_monitor.get_status()["message"])
