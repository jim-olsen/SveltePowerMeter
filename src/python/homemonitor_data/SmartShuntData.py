import json
from dataclasses import dataclass

# Maps the short field names used by ve_network_smartshunt.py (matching the Victron VE.Direct protocol field
# names) to more descriptive attribute names used on this class.
FIELD_MAP = {
    "V": "battery_voltage",
    "I": "current",
    "P": "power",
    "SOC": "state_of_charge",
    "TTG": "time_to_go",
    "H1": "deepest_discharge",
    "H2": "last_discharge",
    "H3": "average_discharge",
    "H4": "number_of_charge_cycles",
    "H5": "number_of_full_discharges",
    "H6": "cumulative_amp_hours_drawn",
    "H7": "minimum_battery_voltage",
    "H8": "maximum_battery_voltage",
    "H9": "time_since_last_full_charge",
    "H10": "automatic_synchronizations",
    "H11": "low_voltage_alarms",
    "H12": "high_voltage_alarms",
    "H17": "total_discharged_energy",
    "H18": "total_charged_energy",
}


@dataclass
class SmartShuntData:
    battery_voltage: float
    current: float
    power: float
    state_of_charge: float
    time_to_go: float
    deepest_discharge: float
    last_discharge: float
    average_discharge: float
    number_of_charge_cycles: int
    number_of_full_discharges: int
    cumulative_amp_hours_drawn: float
    minimum_battery_voltage: float
    maximum_battery_voltage: float
    time_since_last_full_charge: float
    automatic_synchronizations: int
    low_voltage_alarms: int
    high_voltage_alarms: int
    total_discharged_energy: float
    total_charged_energy: float

    def load_from_json(self, json_message: str):
        """Updates only the fields present in the given json message, leaving all other fields untouched. This
        is needed because the real time and history portions of the data are published as two separate chunks.

        Args:
            json_message: The JSON message received from the battery_load mqtt topic.

        Returns:
            SmartShuntData: This instance, updated with the fields present in the json message.
        """
        json_data: dict = json.loads(json_message)
        for key, value in json_data.items():
            field_name = FIELD_MAP.get(key, key)
            if field_name in self.__dict__:
                self.__dict__[field_name] = value
        return self
