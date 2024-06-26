from dataclasses import dataclass
from datetime import date


@dataclass
class StatsData:
    current_date: date
    total_load_wh: float
    day_load_wh: float
    total_solar_wh: float
    day_solar_wh: float
    day_batt_wh: float
    last_charge_state: str
    avg_load: float
    avg_net: float
    avg_solar: float
    yesterday_batt_wh: float
    yesterday_load_wh: float
    yesterday_net_wh: float
    five_day_net: float
    ten_day_net: float
    five_min_load_watts: float
    five_min_battery_watts: float
    five_min_solar_watts: float
    five_min_battery_voltage: float
    battery_min_percent: float
    battery_max_percent: float
    battery_min_percent_one_day_ago: float
    battery_max_percent_one_day_ago: float
    battery_min_percent_two_days_ago: float
    battery_max_percent_two_days_ago: float
    battery_min_percent_three_days_ago: float
    battery_max_percent_three_days_ago: float

