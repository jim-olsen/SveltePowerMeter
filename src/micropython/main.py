import utime
import machine
from ubluepy import Peripheral
from LoadAdvertisement import LoadAdvertisement

CURRENT_SENSOR_FACTOR = 74

def main():
    adc_battery_voltage = machine.ADC(machine.Pin('D0_A0'))
    adc_battery_load = machine.ADC(machine.Pin('D1_A1'))
    adc_load = machine.ADC(machine.Pin('D2_A2'))
    ble = Peripheral()
    advertisement = LoadAdvertisement("load")
    ble.advertise(data=advertisement.advertise_data("initializing"), connectable=False)

    while True:
        try:
            current_battery_voltage = (adc_battery_voltage.read_u16() / ((3.273 / 3.3) * 65535)) * 36

            current_battery_voltage = (adc_battery_voltage.read_u16() / ((3.273 / 3.3) * 65535)) * 36
            current_battery_voltage += (adc_battery_voltage.read_u16() / ((3.273 / 3.3) * 65535)) * 36
            current_battery_voltage += (adc_battery_voltage.read_u16() / ((3.273 / 3.3) * 65535)) * 36
            current_battery_voltage /= 3
            print("Battery Voltage:", current_battery_voltage)
            current_battery_load = (((adc_battery_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR

            # I am using an ACS758 current sensor that has a range of +/- 100 amps.  It outputs 5v, so I step it down with
            # a standard voltage divider circuit utilizing a 10/20k voltage divider circuit with a capacitor to reduce noise

            current_battery_load = (((adc_battery_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR
            current_battery_load += (((adc_battery_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR
            current_battery_load += (((adc_battery_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR
            current_battery_load /= 3
            print("Battery Load:", current_battery_load, "A")
            current_load = (((adc_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR

            current_load = (((adc_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR
            current_load += (((adc_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR
            current_load += (((adc_load.read_u16() / 65535) * 3.3) - 1.65) * CURRENT_SENSOR_FACTOR
            current_load /= 3
            print("Current Load:", current_load, "A")
            ble.advertise_stop()
            ble.advertise(data=advertisement.advertise_data("{:.1f}".format(current_battery_voltage) + ":" +
                                     "{:.1f}".format(current_battery_load) + ":" + "{:.1f}".format(current_load)),
                      connectable=False)
        except Exception as e:
            print("Error reading values and advertising: ", e)
        utime.sleep_ms(10000)


if __name__ == "__main__":
    main()
