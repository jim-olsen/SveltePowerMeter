import logging
import threading
import time
import asyncio
import paho.mqtt.client as mqtt
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import RPi.GPIO as GPIO

from lead_yo_battery import find_all_batteries, SmartBattery
from typing import List
from adafruit_ads1x15.analog_in import AnalogIn
from DFRobot_AS3935_Lib import DFRobot_AS3935

logger = logging.getLogger('energy_monitor')
# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
LAST_BEACON_RECEIVED = time.time()
MQTT_CLIENT: mqtt.Client = None
AS3935_I2C_ADDR = 0x03
AS3935_CAPACITANCE = 96
AS3935_IRQ_PIN = 4
LIGHTNING_SENSOR: DFRobot_AS3935 = None


#
# Startup the mqtt client and register callbacks to reconnect on any client disconnections
#
def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        global MQTT_CLIENT

        logger.info("MQTT Client Connected")
        MQTT_CLIENT = c

    def on_disconnect(c, userdata, rc):
        logger.info(f"MQTT Client Disconnected due to {rc}, retrying....")
        while True:
            try:
                c.reconnect()
                break
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}, will retry....")
            time.sleep(30)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()


#
# Monitor all connected batteries by connecting one by one and pulling all current info.  Do this in a cycle with a
# pause in it.
#
async def async_monitor_batteries(batteries: List[SmartBattery]):
    global LAST_BEACON_RECEIVED
    global MQTT_CLIENT
    failure_count = 0

    # Capture the last time we received a packet, as sometimes Bluez hangs and we want to exit and restart to recover
    LAST_BEACON_RECEIVED = time.time()
    while failure_count < 10 and time.time() - LAST_BEACON_RECEIVED < 120:
        # Connect to all of the batteries in turn
        for idx, battery in enumerate(batteries):
            # Filter for our bank of batteries
            if (battery.name().startswith('BANK1') or battery.name().startswith('BANK2') or
                    battery.name().startswith('BANK3') or battery.name().startswith('BANK4')):
                try:
                    logger.info(f"Connecting to battery {battery.name()}")
                    logger.info(f'Battery {battery.name()} percent charged {await battery.capacity_percent()}%')
                    cell_balance_status = []
                    for i in range(await battery.num_cells()):
                        cell_balance_status.append(await battery.balance_status(i + 1))
                    MQTT_CLIENT.publish('battery_status', json.dumps({
                        'name': battery.name(),
                        'voltage': await battery.voltage(),
                        'current': await battery.current(),
                        'residual_capacity': await battery.residual_capacity(),
                        'nominal_capacity': await battery.nominal_capacity(),
                        'cycles': await battery.cycles(),
                        'balance_status': cell_balance_status,
                        'protection_status': await battery.protection_status(),
                        'version': await battery.version(),
                        'capacity_percent': await battery.capacity_percent(),
                        'control_status': await battery.control_status(),
                        'num_cells': await battery.num_cells(),
                        'battery_temps_f': await battery.battery_temps_f(),
                        'cell_block_voltages': await battery.cell_block_voltages()
                    }))
                    failure_count = 0
                    LAST_BEACON_RECEIVED = time.time()
                except Exception as e:
                    logger.error(f"Failed to read from battery {battery.name()}: {e}")
                    failure_count += 1
                    await asyncio.sleep(1)

        await asyncio.sleep(20)

    # Bluez goes out to left field on occasion, so if we aren't getting any valid data out of it, exit to reset
    logger.error("Too many failures in a row, exiting to allow restart of bluetooth....")
    raise SystemExit('Too many failures in a row, existing to allow restart of bluetooth')


#
# Start monitoring the batteries.  This is a synchronous entry point to the async function
#
def monitor_batteries(batteries: List[SmartBattery]):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_monitor_batteries(batteries))


#
# This process handles reading values from a directly connected ADS 1115 A/D chip.  This chip is used to read values
# from connected load sensors that provide +/- 100amp readings to sense load in the system.  In this case the direct
# consumption load sensor is on pin A0, and the battery monitor (both input and output) is connected to pin A1.  Pin
# A2 is grounded to provide a zero reference, since it seems to vary slightly and can be used for correction
#
def read_analog_values_thread():
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.gain = 2/3

    while True:
        # reference from an empty pin tells us about how much it is off
        reference = AnalogIn(ads, ADS.P2).voltage
        # 2.5 is zero amps, -0.5 is -100, 4.5 is +100
        load_amps = ((AnalogIn(ads, ADS.P0).voltage + (reference / 1.4) - 2.5) / 2) * 100
        battery_amps = ((AnalogIn(ads, ADS.P1).voltage + (reference / 1.4) - 2.5) / 2) * 100
        logger.debug(f"Load: {load_amps}A, battery_load: {battery_amps}A")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('load_data', json.dumps({
                'battery_load': battery_amps,
                'load_amps':  load_amps
            }))
        time.sleep(5)

    logger.error("Fell out of analog reader loop that should never end, allow restart of service")
    raise SystemExit("Fell out of analog reader loop that should never end, allow restart of service")


def lightning_sensor_callback_handler(channel):
    global LIGHTNING_SENSOR, MQTT_CLIENT

    time.sleep(0.005)
    interrupt_source = LIGHTNING_SENSOR.get_interrupt_src()
    if interrupt_source == 1:
        logger.warning(f"Detected lightning at {LIGHTNING_SENSOR.get_lightning_distKm()}km and intensity  {LIGHTNING_SENSOR.get_strike_energy_raw()}")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('lightning_data', json.dumps({
                'event': 'lightning',
                'distance': LIGHTNING_SENSOR.get_lightning_distKm(),
                'intensity': LIGHTNING_SENSOR.get_strike_energy_raw()
            }))
    elif interrupt_source == 2:
        logger.error("Lightning sensor detected a disturber")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('lightning_data', json.dumps({
                'event': 'disturber'
            }))
    elif interrupt_source == 3:
        logger.error("Lightning sensor is detecting too much noise")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('lightning_data', json.dumps({
                'event': 'noise'
            }))


def main():
    global AS3935_IRQ_PIN, AS3935_CAPACITANCE, AS3935_I2C_ADDR, LIGHTNING_SENSOR

    logging.basicConfig()
    logging.getLogger('energy_monitor').setLevel(logging.WARNING)

    logger.info("Finding all batteries in range")
    batteries = sorted(find_all_batteries(10), key=lambda x: x.name())

    logger.info(f"Found batteries {batteries}")

    logger.warning("Initializing AS3935")
    lightning_sensor = DFRobot_AS3935(AS3935_I2C_ADDR, bus=1)
    if lightning_sensor.reset():
        logger.warning("Lightning detector successfully initialized")
        lightning_sensor.power_up()
        lightning_sensor.set_outdoors()
        lightning_sensor.disturber_en()
        lightning_sensor.set_irq_output_source(0)
        time.sleep(0.5)
        lightning_sensor.set_tuning_caps(AS3935_CAPACITANCE)
        lightning_sensor.set_noise_floor_lv1(1)
        lightning_sensor.set_watchdog_threshold(2)
        lightning_sensor.set_spike_rejection(2)
        LIGHTNING_SENSOR = lightning_sensor
        GPIO.setup(AS3935_IRQ_PIN, GPIO.IN)
        GPIO.add_event_detect(AS3935_IRQ_PIN, GPIO.RISING, callback=lightning_sensor_callback_handler)
    else:
        logger.error("Lightning detector failed to initialize")

    mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
    mqtt_thread.daemon = True
    mqtt_thread.start()

    analog_thread = threading.Thread(target=read_analog_values_thread, args=())
    analog_thread.daemon = True
    analog_thread.start()

    monitor_batteries(batteries)


if __name__ == "__main__":
    main()
