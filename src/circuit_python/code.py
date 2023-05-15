# Write your code here :-)
import board
import analogio
import time
from _bleio import adapter
from LoadAdvertisement import LoadAdvertisement


def main():
    advertisement = LoadAdvertisement("load")
    adc_battery_voltage = analogio.AnalogIn(board.A0)
    adc_battery_load = analogio.AnalogIn(board.A1)
    adc_load = analogio.AnalogIn(board.A2)
    current_sensor_factor = 74
    while True:
        # The 3.273 comes from the fact that the voltage divider circuit maxes out at 3.273 at 36v.  This is due to using
        # a 100k/10k resistor combo as a voltage divider to measure the voltage.  This combo should be place on input
        # A0

        # throw the first reading away
        current_battery_voltage = (adc_battery_voltage.value / ((3.273 / 3.3) * 65535)) * 36

        current_battery_voltage = (adc_battery_voltage.value / ((3.273 / 3.3) * 65535)) * 36
        current_battery_voltage += (adc_battery_voltage.value / ((3.273 / 3.3) * 65535)) * 36
        current_battery_voltage += (adc_battery_voltage.value / ((3.273 / 3.3) * 65535)) * 36
        current_battery_voltage /= 3
        print("Battery Voltage:", current_battery_voltage)
        current_battery_load = (((adc_battery_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor

        # I am using an ACS758 current sensor that has a range of +/- 100 amps.  It outputs 5v, so I step it down with
        # a standard voltage divider circuit utilizing a 10/20k voltage divider circuit with a capacitor to reduce noise

        current_battery_load = (((adc_battery_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor
        current_battery_load += (((adc_battery_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor
        current_battery_load += (((adc_battery_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor
        current_battery_load /= 3
        print("Battery Load:", current_battery_load, "A")
        current_load = (((adc_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor

        current_load = (((adc_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor
        current_load += (((adc_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor
        current_load += (((adc_load.value / 65535) * 3.3) - 1.65) * current_sensor_factor
        current_load /= 3
        print("Current Load:", current_load, "A")
        adapter.start_advertising(advertisement.advertise_data("{:.1f}".format(current_battery_voltage) +
                                                               "{:.1f}".format(current_battery_load) +
                                                               "{:.1f}".format(current_load)),
                                  scan_respone=None, connectable=False, interval=0.5)
        time.sleep(10)


if __name__ == "__main__":
    main()
