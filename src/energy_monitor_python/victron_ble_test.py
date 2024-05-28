import logging
import asyncio
import json
import time
from bleak import BleakScanner, BLEDevice, AdvertisementData
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Util.Padding import pad
from construct import Struct, FixedSized, GreedyBytes, Int16ul, Int8sl, Int8ul, Int16sl, Int24sl

VICTRON_ADDRESSES = ['FA:66:AD:B2:8C:E4', 'F2:5B:16:A1:15:77']
VICTRON_BLE_KEYS = {'FA:66:AD:B2:8C:E4': '932d4be6e50cb7f03148f8529b05f58b',
                    'F2:5B:16:A1:15:77': 'c926a1a391161e689bb9a804e8b982b9'}
logger = logging.getLogger('energy_monitor')


# When we receive a bluetooth advertising packet from the victron charger, decode the available data and post to the
# correct MQTT topic
def process_victron_data(device: BLEDevice, advertisement: AdvertisementData):
    global VICTRON_BLE_KEYS, MQTT_CLIENT, LAST_BEACON_RECEIVED

    LAST_BEACON_RECEIVED = time.time()
    # The structure of a victron packet
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
    logger.debug(container)
    logger.debug(hex(container.model_id))

    advertisement_key = bytes.fromhex(VICTRON_BLE_KEYS[device.address])

    # The first data byte is a key check byte
    if container.encrypted_data[0] != advertisement_key[0]:
        raise Exception("Incorrect advertisement key")

    ctr = Counter.new(128, initial_value=container.iv, little_endian=True)

    cipher = AES.new(
        advertisement_key,
        AES.MODE_CTR,
        counter=ctr,
    )

    # Victron BLE packets are encrypted with a key specific to your installation, so decrypt the data for processing
    decrypted_packet = cipher.decrypt(pad(container.encrypted_data[1:], 16))
    if container.model_id == 0xc030:
        dc_meter_parser = Struct(
            "meter_type" / Int16sl,
            # Voltage reading in 10mV increments
            "voltage" / Int16ul,
            # Alarm reason
            "alarm" / Int16ul,
            # Value of the auxillary input
            "aux" / Int16ul,
            # The upper 22 bits indicate the current in milliamps
            # The lower 2 bits identify the aux input mode:
            #   0 = Starter battery voltage
            #   1 = Midpoint voltage
            #   2 = Temperature
            #   3 = Disabled
            "current" / Int24sl,
        )
        dc_meter_data = dc_meter_parser.parse(decrypted_packet)
        logger.debug(dc_meter_data)
        amps = (dc_meter_data.current >> 2) / 1000
        volts = dc_meter_data.voltage / 100
        logger.debug(f"{amps}A {volts}V {amps * volts}W")
    else:
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

        # Now using the structure, parse the decrypted victron data
        charger_data = charger_parser.parse(decrypted_packet)
        logger.debug(charger_data)
        # Map the victron charge state number to our common enum style
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


#
# Connect to the BLE device and get the voltage from A0, and the loads from A1 and A2 pins.  See the circuit python
# code for how this is implemented
#
async def update_ble_values(device: BLEDevice, advertisement: AdvertisementData):
    global VICTRON_ADDRESSES

    # logger.info(f"Received packet from {device.name} - {device.address}")
    try:
        if advertisement and device.address in VICTRON_ADDRESSES:
            logger.debug("Received victron update")
            process_victron_data(device, advertisement)

    except Exception as e:
        logger.error(f"Failure inside of BLE beacon parsing: {e}")


async def monitor_victron():
    scanner = BleakScanner(detection_callback=update_ble_values)
    await scanner.start()
    while True:
        await asyncio.sleep(30)


def main():
    logging.basicConfig();
    logging.getLogger("energy_monitor").setLevel(logging.DEBUG)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(monitor_victron())

if __name__ == "__main__":
    main()
