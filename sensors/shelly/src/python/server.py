import logging
import re
import threading
import time
import json
import paho.mqtt.client as mqtt
import requests

MQTT_SERVER_ADDR = '10.0.10.31'
SHELLY_DEVICES = {}

logger = logging.getLogger('test_mqtt')

def turn_relay_on(shelly_device, relay=0):
    r = requests.get(shelly_device['ip_address'] + '/relay/' + str(relay) + '?turn=on')
    if r.status_code == 200:
        return r.json()
    else:
        logger.error(f"Failed to turn relay on for Shelly+ {r.status_code}")
        return {}

def turn_relay_off(shelly_device, relay=0):
    r = requests.get(shelly_device['ip_address'] + '/relay/' + str(relay) + '?turn=off')
    if r.status_code == 200:
        return r.json()
    else:
        logger.error(f"Failed to turn relay off for Shelly+ {r.status_code}")
        return {}

def power_cycle_relay(shelly_device, relay=0, delay=5):
    r = requests.get(shelly_device['ip_address'] + '/relay/' + str(relay) + '?turn=off&timer=' + str(delay))
    if r.status_code == 200:
        while True:
            current_status = self.get_relay_status(relay)
            if "ison" in current_status:
                if current_status["ison"]:
                    break
            else:
                logger.error(f"Received a status response on power cycle with no relay status, aborting... {current_status}")
                break
        return r.json()
    else:
        logger.error(f"Failed to turn relay off for Shelly+ {r.status_code}")
        return {}

def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        global MQTT_CLIENT

        logger.info("MQTT Client Connected")
        MQTT_CLIENT = c
        c.subscribe('shellies/announce')
        c.subscribe('shelly/+/status/wifi')
        c.subscribe('shelly/+/status/switch:0')

        c.message_callback_add('shellies/announce', on_shelly_announce)
        c.message_callback_add('shelly/+/status/wifi', on_wifi_status_update)
        c.message_callback_add('shelly/+/status/switch:0', on_switch_status_update)

    def on_disconnect(c, userdata, rc):
        logger.warning(f"MQTT Client Disconnected due to {rc}, retrying....")
        while True:
            try:
                c.reconnect()
                break
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}, will retry....")
            time.sleep(30)

    def on_shelly_announce(c, userdata, msg):
        logger.debug(f"Received shelly announcement {json.loads(msg.payload)}")
        announcement = json.loads(msg.payload)
        if not announcement['id'] in SHELLY_DEVICES:
            SHELLY_DEVICES[announcement['id']] = { 'id': announcement['id']}
        shelly_device = SHELLY_DEVICES[announcement['id']]
        shelly_device['name'] = announcement['name']

        c.publish('shelly/' + announcement.get('id') + '/command', 'status_update')

    def on_wifi_status_update(c, userdata, msg):
        logger.debug(f"Received wifi update on {msg.topic}: {json.loads(msg.payload)}")
        match = re.match(r"^shelly/([^/]+)/status/.+$", msg.topic)
        wifi_status = json.loads(msg.payload)
        if match:
            shelly_id = match.group(1)
            logger.debug(f"Shelly id is {shelly_id}")
            if not shelly_id in SHELLY_DEVICES:
                SHELLY_DEVICES[shelly_id] = { 'id': shelly_id }
            shelly_device = SHELLY_DEVICES[shelly_id]
            shelly_device['ip_address'] = wifi_status['sta_ip']
        else:
            logger.error(f"Failed to parse shelly id from topic {msg.topic}")

    def on_switch_status_update(c, userdata, msg):
        logger.debug(f"Received switch update on {msg.topic}: {json.loads(msg.payload)}")
        match = re.match(r"^shelly/([^/]+)/status/.+$", msg.topic)
        switch_status = json.loads(msg.payload)
        if match:
            shelly_id = match.group(1)
            logger.debug(f"Shelly id is {shelly_id}")
            if not shelly_id in SHELLY_DEVICES:
                SHELLY_DEVICES[shelly_id] = { 'id': shelly_id }
            shelly_device = SHELLY_DEVICES[shelly_id]
            shelly_device['ison'] = switch_status['output']
        else:
            logger.error(f"Failed to parse shelly id from topic {msg.topic}")

    def on_message(c, userdata, msg):
        logger.debug(f"Received message for topic {msg.topic}: {msg.payload}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()

def main():
    logging.basicConfig()
    logging.getLogger('test_mqtt').setLevel(logging.INFO)
    mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
    mqtt_thread.daemon = True
    mqtt_thread.start()

    time.sleep(3)
    while True:
        MQTT_CLIENT.publish('shellies/command', 'announce')
        time.sleep(5)
        for shelly_id in SHELLY_DEVICES:
            MQTT_CLIENT.publish('lights', json.dumps(SHELLY_DEVICES[shelly_id]))

if __name__ == "__main__":
    main()
