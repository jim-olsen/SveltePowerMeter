import time
import logging
import threading
import json
import paho.mqtt.client as mqtt
from Starlink import Starlink

LOG = logging.getLogger(__name__)

# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
MQTT_CLIENT: mqtt.Client = None

#
# Startup the mqtt client and register callbacks to reconnect on any client disconnections
#
def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        global MQTT_CLIENT

        LOG.info("MQTT Client Connected")
        MQTT_CLIENT = c

    def on_disconnect(c, userdata, rc):
        LOG.info(f"MQTT Client Disconnected due to {rc}, retrying....")
        while True:
            try:
                c.reconnect()
                break
            except Exception as e:
                LOG.error(f"Failed to reconnect: {e}, will retry....")
            time.sleep(30)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()

def publish_starlink_data(dishy):
    while True:
        if MQTT_CLIENT:

            current_starlink_data = {
                'status' : dishy.get_status(),
                'history' : dishy.get_history(),
                'obstruction_map': dishy.get_obstruction_map()
            }
            MQTT_CLIENT.publish('starlink', json.dumps(current_starlink_data))
        time.sleep(1)

def main():
    dishy = Starlink()

    mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
    mqtt_thread.daemon = True
    mqtt_thread.start()

    publish_starlink_data(dishy)

if __name__ == "__main__":
    main()