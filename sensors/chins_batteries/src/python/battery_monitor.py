import logging
import time
import asyncio
import paho.mqtt.client as mqtt
import json

from lead_yo_battery import find_all_batteries, SmartBattery
from typing import List

logger = logging.getLogger('energy_monitor')
# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
LAST_BEACON_RECEIVED = time.time()
MQTT_CLIENT: mqtt.Client

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

def main():
    logging.basicConfig()
    logging.getLogger('battery_monitor').setLevel(logging.DEBUG)

    logger.info("Finding all batteries in range")
    batteries = sorted(find_all_batteries(10), key=lambda x: x.name())

    logger.info(f"Found batteries {batteries}")

    monitor_batteries(batteries)


if __name__ == "__main__":
    main()
