import json
import logging
import os
import threading
import time
import math

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

def calculate_wind_chill(temp_f, wind_speed_mph):
    """
    Calculate the wind chill index given the temperature in Fahrenheit and wind speed in mph.
    The formula is valid for temperatures at or below 50°F and wind speeds above 3 mph.
    """
    if temp_f > 50 or wind_speed_mph <= 3:
        return temp_f  # Wind chill formula is not valid in this range

    wind_chill = 35.74 + 0.6215 * temp_f - 35.75 * (wind_speed_mph ** 0.16) + 0.4275 * temp_f * (wind_speed_mph ** 0.16)
    return wind_chill


def calculate_dew_point(temp_f, humidity):
    # Convert temperature from Fahrenheit to Celsius
    temp_c = (temp_f - 32) * 5.0 / 9.0

    # Calculate the dew point in Celsius
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)

    # Convert dew point back to Fahrenheit
    dew_point_f = (dew_point_c * 9.0 / 5.0) + 32
    return dew_point_f


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

@app.route("/data/report", methods=['POST'])
def dataReport():
    try:
        weatherData = request.form.copy()
        weatherData.update({
            'windSpeed_mph' : request.form.get('windgustmph', 0),
            'outTemp_F': request.form.get('tempf', 0),
            'rain_total': request.form.get('yrain_piezo', 0),
            'barometer_inHg': request.form.get('baromrelin', 0),
            'inTemp_F': request.form.get('tempinf', 0),
            'outHumidity': request.form.get('humidity', 0),
            'daily_rain': request.form.get('drain_piezo', 0),
            'wind_average': request.form.get('windspeedmph', 0),
            'rain_in': request.form.get('erain_piezo', 0),
            'pressure_inHg': request.form.get('baromrelin', 0),
            'windchill_F': str(calculate_wind_chill(float(request.form.get('tempf', 0)), float(request.form.get('windspeedmph', 0)))),
            'dewpoint_F': str(calculate_dew_point(float(request.form.get('tempf', 0)), float(request.form.get('humidity', 0)))),
            'hourRain_in': request.form.get('hrain_piezo', 0),
            'rain24_in': request.form.get('drain_piezo', 0),
            'dayRain_in': request.form.get('drain_piezo', 0),
            'weekRain_in': request.form.get('wrain_piezo', 0),
            'solarRadiation': request.form.get('solarradiation', 0),
            'inHumidity': request.form.get('humidityin', 0),
            'windDir': request.form.get('winddir', 0)
        })
        MQTT_CLIENT.publish('weather/loop', json.dumps(weatherData))
        logger.debug('Responding with: ' + json.dumps(weatherData))

        return weatherData
    except Exception as e:
        logger.error(f"Failure in responding to post: {e}")
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