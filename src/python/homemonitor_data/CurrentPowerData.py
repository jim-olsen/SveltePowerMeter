from dataclasses import dataclass


@dataclass
class CurrentPowerData:
    battery_load: float
    load_amps: float
    load_watts: float
    battery_voltage: float
    day_solar_wh: float
    day_load_wh: float
    battery_sense_voltage: float
    battery_voltage_slow: float
    battery_daily_minimum_voltage: float
    battery_daily_maximum_voltage: float
    target_regulation_voltage: float
    array_voltage: float
    array_charge_current: float
    battery_charge_current: float
    battery_charge_current_slow: float
    input_power: float
    solar_watts: float
    heatsink_temperature: float
    battery_temperature: float
    charge_state: str
    seconds_in_absorption_daily: int
    seconds_in_float_daily: int
    seconds_in_equalization_daily: int

