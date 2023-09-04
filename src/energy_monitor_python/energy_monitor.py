import logging
import threading
import time
import asyncio
import paho.mqtt.client as mqtt
import re
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS

from bleak import BleakScanner, BLEDevice, AdvertisementData
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Util.Padding import pad
from construct import Struct, FixedSized, GreedyBytes, Int16ul, Int8sl, Int8ul, Int16sl
from lead_yo_battery import find_all_batteries, SmartBattery
from typing import List
from adafruit_ads1x15.analog_in import AnalogIn

logger = logging.getLogger('energy_monitor')
# The bluetooth address and encryption key of the victron solar charger
VICTRON_ADDRESS = 'FA:66:AD:B2:8C:E4'
VICTRON_BLE_KEY = '932d4be6e50cb7f03148f8529b05f58b'
# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
LAST_BEACON_RECEIVED = time.time()
MQTT_CLIENT: mqtt.Client = None


def process_victron_data(advertisement: AdvertisementData):
    global VICTRON_BLE_KEY, MQTT_CLIENT, LAST_BEACON_RECEIVED

    LAST_BEACON_RECEIVED = time.time()
    parser = Struct(
        "prefix" / FixedSized(2, GreedyBytes),
        # Model ID
        "model_id" / Int16ul,
        # Packet type
        "readout_type" / Int8sl,
        # IV for encryption
        "iv" / Int16ul,
        "encrypted_data" / GreedyBytes,
        )
    container = parser.parse(advertisement.manufacturer_data[737])

    advertisement_key = bytes.fromhex(VICTRON_BLE_KEY)

    # The first data byte is a key check byte
    if container.encrypted_data[0] != advertisement_key[0]:
        raise Exception("Incorrect advertisement key")

    ctr = Counter.new(128, initial_value=container.iv, little_endian=True)

    cipher = AES.new(
        advertisement_key,
        AES.MODE_CTR,
        counter=ctr,
    )

    decrypted_packet = cipher.decrypt(pad(container.encrypted_data[1:], 16))
    charger_parser = Struct(
        "charge_state" / Int8ul,
        "charger_error" / Int8ul,
        # Battery voltage reading in 0.01V increments
        "battery_voltage" / Int16sl,
        # Battery charging Current reading in 0.1A increments
        "battery_charging_current" / Int16sl,
        # Todays solar power yield in 10Wh increments
        "yield_today" / Int16ul,
        # Current power from solar in 1W increments
        "solar_power" / Int16ul,
        # External device load in 0.1A increments
        "external_device_load" / Int16ul,
        )

    charger_data = charger_parser.parse(decrypted_packet)
    logger.debug(charger_data)
    charge_states = ["NIGHT", "LOW_POWER", "FAULT", "MPPT", "ABSORB", "FLOAT", "STORAGE", "EQUALIZE_MANUAL"]

    if MQTT_CLIENT:
        MQTT_CLIENT.publish('solar_charger_data', json.dumps({
            'solar_watts': charger_data.solar_power,
            'battery_charge_current': float(charger_data.battery_charging_current) / 10,
            'charge_state': charge_states[charger_data.charge_state] if charger_data.charge_state <= 7 else "OTHER",
            'battery_voltage': float(charger_data.battery_voltage) / 100,
            'day_solar_wh': charger_data.yield_today * 10
        }))
    else:
        logger.error('Received solar charger data, but MQTT not connected')


def process_circuit_python_ble(advertisement: AdvertisementData):
    global LAST_BEACON_RECEIVED

    LAST_BEACON_RECEIVED = time.time()
    logger.debug("Received load data: " + str(advertisement.service_data))
    load_data = advertisement.service_data.get(list(advertisement.service_data.keys())[0], "").decode()[2:]
    sensor_values = re.findall("([0-9-]*\\.[0-9])", load_data)

    if MQTT_CLIENT:
        MQTT_CLIENT.publish('load_sensor_data', json.dumps({
            'battery_voltage': float(sensor_values[0]),
            'battery_load': float(sensor_values[1]),
            'load_amps':  float(sensor_values[2].replace("*", ""))
        }))

#
# Connect to the BLE device and get the voltage from A0, and the loads from A1 and A2 pins.  See the circuit python
# code for how this is implemented
#
async def update_ble_values(device: BLEDevice, advertisement: AdvertisementData):
    global VICTRON_ADDRESS

    try:
        if advertisement and advertisement.local_name == 'load':
            process_circuit_python_ble(advertisement)
        elif advertisement and device.address == VICTRON_ADDRESS:
            logger.debug("Received victron update")
            process_victron_data(advertisement)

    except Exception as e:
        logger.error(f"Failure inside of BLE beacon parsing: {e}")


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


def monitor_batteries(batteries: List[SmartBattery]):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_monitor_batteries(batteries))


async def async_monitor_batteries(batteries: List[SmartBattery]):
    global LAST_BEACON_RECEIVED
    global MQTT_CLIENT
    failure_count = 0

    LAST_BEACON_RECEIVED = time.time()
    scanner = BleakScanner(detection_callback=update_ble_values)
    while failure_count < 10 and time.time() - LAST_BEACON_RECEIVED < 60:
        for battery in batteries:
            if battery.name().startswith('BANK1') or battery.name().startswith('BANK2') or battery.name().startswith('BANK3'):
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
                except Exception as e:
                    logger.error(f"Failed to read from battery {battery.name()}: {e}")
                    failure_count += 1
                await asyncio.sleep(1)

        await scanner.start()
        await asyncio.sleep(30)
        await scanner.stop()

    logger.error("Too many failures in a row, exiting to allow restart of bluetooth....")
    raise SystemExit('Too many failures in a row, existing to allow restart of bluetooth')


def read_analog_values_thread():
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.gain = 2/3

    while True:
        # reference from an empty pin tells us about how much it is off
        reference = AnalogIn(ads, ADS.P2).voltage
        # 2.5 is zero amps, -0.5 is -100, 4.5 is +100
        load_amps = ((AnalogIn(ads, ADS.P0).voltage + (reference / 1.25) - 2.5) / 2) * 100
        battery_amps = ((AnalogIn(ads, ADS.P1).voltage + (reference / 1.25) - 2.5) / 2) * 100
        logger.debug(f"Load: {load_amps}A, battery_load: {battery_amps}A")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('load_data', json.dumps({
                'battery_load': battery_amps,
                'load_amps':  load_amps
            }))
        time.sleep(5)
    logger.error("Fell out of analog reader loop that should never end, allow restart of service")
    raise SystemExit("Fell out of analog reader loop that should never end, allow restart of service")

def main():
    logging.basicConfig()
    logging.getLogger('energy_monitor').setLevel(logging.WARNING)

    logger.info("Finding all batteries in range")
    batteries = find_all_batteries()

    logger.info(f"Found batteries {batteries}")

    mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
    mqtt_thread.daemon = True
    mqtt_thread.start()

    analog_thread = threading.Thread(target=read_analog_values_thread, args=())
    analog_thread.daemon = True
    analog_thread.start()

    monitor_batteries(batteries)


if __name__ == "__main__":
    main()
