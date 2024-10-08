import logging
import time
import json
import paho.mqtt.client as mqtt

MQTT_SERVER_ADDR = '10.0.10.31'
logger = logging.getLogger('test_mqtt')


def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        global MQTT_CLIENT

        logger.info("MQTT Client Connected")
        MQTT_CLIENT = c
#        c.subscribe('battery_status')
#        c.subscribe('solar_charger_data')
#        c.subscribe('load_data')
#        c.subscribe('lightning_data')
#        c.subscribe('blueiris')
        c.subscribe('weather/loop')
#        c.subscribe('#')
#        c.subscribe('adsb')
#        c.subscribe('dc_meter_data')

    def on_disconnect(c, userdata, rc):
        logger.info(f"MQTT Client Disconnected due to {rc}, retrying....")
        while True:
            try:
                c.reconnect()
                break
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}, will retry....")
            time.sleep(30)

    def on_message(c, userdata, msg):
        logger.info(f"Received message for topic {msg.topic}: {msg.payload}")
        try:
            logger.info(f"Received message for topic {msg.topic}: {json.loads(msg.payload)}")
        except Exception as e:
            logger.debug("Not valid json")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()

def main():
    logging.basicConfig()
    logging.getLogger('test_mqtt').setLevel(logging.INFO)
    start_mqtt_client()

if __name__ == "__main__":
    main()
