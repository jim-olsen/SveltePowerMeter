import json
import logging
import os
import threading
import time

import paho.mqtt.client as mqtt
from flask import Flask, request

MQTT_SERVER_ADDR = '10.0.10.31'
MQTT_CLIENT: mqtt.Client = None
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logger = logging.getLogger('ecowitt_to_mqtt')

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

    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.connect(MQTT_SERVER_ADDR, 1883, 60)
        client.loop_forever()
    except Exception as e:
        logging.error(f"Failed to connect to MQTT server: {e}")
        os._exit(1)


@app.route("/wxData")
def wxData():
    try:
        weatherData = {
            'windSpeed_mph' : request.args.get('windgustmph', 0),
            'outTemp_F': request.args.get('tempf', 0),
            'rain_total': request.args.get('yearlyrainin', 0),
            'barometer_inHg': request.args.get('baromin', 0),
            'inTemp_F': request.args.get('indoortempf', 0),
            'outHumidity': request.args.get('humidity', 0),
            'daily_rain': request.args.get('dailyrainin', 0),
            'wind_average': request.args.get('windspeedmph', 0),
            'rain_in': request.args.get('rainin', 0),
            'pressure_inHg': request.args.get('baromin', 0),
            'windchill_F': request.args.get('windchillf', 0),
            'dewpoint_F': request.args.get('dewptf', 0),
            'hourRain_in': request.args.get('rainin', 0),
            'rain24_in': request.args.get('dailyrainin', 0),
            'dayRain_in': request.args.get('dailyrainin', 0),
            'weekRain_in': request.args.get('weeklyrainin', 0),
            'solarRadiation': request.args.get('solarradiation', 0),
            'inHumidity': request.args.get('indoorhumidity', 0),
            'windDir': request.args.get('winddir', 0)
        }
        MQTT_CLIENT.publish('weather/loop', json.dumps(weatherData))
        logger.debug('Responding with: ' + json.dumps(weatherData))
        return weatherData
    except Exception as e:
        logger.error(f"Failed to get weather data: {e}")
        return "Failed to fetch data: " + str(e), 500

def main():
    try:
        mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
        mqtt_thread.daemon = True
        mqtt_thread.start()

        app.run(port=8090, host='0.0.0.0')
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        os._exit(1)


if __name__ == "__main__":
    main()