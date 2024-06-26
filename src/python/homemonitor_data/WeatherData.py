import json
from dataclasses import dataclass

@dataclass
class WeatherData:
    altimeter_inHg: float
    appTemp_F: float
    barometer_inHg: float
    cloudbase_foot: float
    daily_rain: float
    dateTime: float
    dayRain_in: float
    day_of_year: float
    dewpoint_F: float
    heatindex_F: float
    hourRain_in: float
    humidex_F: float
    inTemp_F: float
    minute_of_day: float
    outHumidity: float
    outTemp_F: float
    pressure_inHg: float
    rain24_in: float
    rainRate_inch_per_hour: float
    rain_in: float
    rain_total: float
    usUnits: float
    windDir: float
    windSpeed_mph: float
    wind_average: float
    windchill_F: float

    def load_from_json(self, json_message: str):
        json_data: dict = json.loads(json_message)
        for key, value in json_data.items():
            if key in self.__dict__:
                self.__dict__[key] = value
        return self
