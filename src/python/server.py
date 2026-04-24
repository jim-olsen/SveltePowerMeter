import copy
import os
import pickle
from flask import Flask, send_from_directory, send_file, request
import time
import threading
import io
import json
import numpy as np
import logging
import paho.mqtt.client as mqtt
import uuid
from datetime import datetime, timedelta
from PIL import Image
from flask_socketio import SocketIO
from homemonitor_data import CurrentPowerData, StatsData, WeatherData
import sql_manager

logging.basicConfig()
logging.getLogger('power_meter').setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logger = logging.getLogger('power_meter')

CURRENT_DATA: CurrentPowerData = CurrentPowerData(battery_load=None, load_amps=None, load_watts=None,
                                                  battery_voltage=None, day_solar_wh=0,
                                                  day_load_wh=0, battery_sense_voltage=None,
                                                  battery_voltage_slow=None, battery_daily_minimum_voltage=None,
                                                  battery_daily_maximum_voltage=None, target_regulation_voltage=None,
                                                  array_voltage=None, array_charge_current=None,
                                                  battery_charge_current=None, battery_charge_current_slow=None,
                                                  input_power=None, solar_watts=None, heatsink_temperature=None,
                                                  battery_temperature=None, charge_state='NIGHT',
                                                  seconds_in_absorption_daily=0, seconds_in_float_daily=0,
                                                  seconds_in_equalization_daily=0)

STATS_DATA = StatsData(current_date=datetime.today().date(), total_load_wh=0, day_load_wh=0, total_solar_wh=0,
    day_solar_wh=0, day_batt_wh=0, last_charge_state='MPPT', avg_load=0.0, avg_net=0.0, avg_solar=0.0,
    yesterday_batt_wh=None, yesterday_load_wh=None, yesterday_net_wh=None, five_day_net=None, ten_day_net=None,
    five_min_load_watts=None, five_min_battery_watts=None, five_min_solar_watts=None, five_min_battery_voltage=None,
    battery_min_percent=None, battery_max_percent=None, battery_min_percent_one_day_ago=None,
    battery_max_percent_one_day_ago=None, battery_min_percent_two_days_ago=None, battery_max_percent_two_days_ago=None,
    battery_min_percent_three_days_ago=None, battery_max_percent_three_days_ago=None)

WEATHER_DATA: WeatherData = WeatherData(altimeter_inHg=None, appTemp_F=None, barometer_inHg=None, cloudbase_foot=None,
                                        daily_rain=None, dateTime=None, dayRain_in=None, day_of_year=None,
                                        dewpoint_F=None, heatindex_F=None, hourRain_in=None, humidex_F=None,
                                        inTemp_F=None, minute_of_day=None, outHumidity=None, outTemp_F=None,
                                        pressure_inHg=None, rain24_in=None, rainRate_inch_per_hour=None, rain_in=None,
                                        rain_total=None, usUnits=None, windDir=None, windSpeed_mph=None,
                                        wind_average=None, windchill_F=None)
BLUEIRIS_ALERT = {}
ADSB_DATA = {}
BATTERIES = {}
STARLINK = { 'status': {}, 'history': {}, 'obstruction_map': [] }

# List of valid fields for querying battery graph data.  This protects against sql injection using a dynamic field.
VALID_BATTERY_FIELDS = ["name", "voltage", "current", "residual_capacity", "nominal_capacity", "cycles",
                        "balance_status_cell_one", "balance_status_cell_two", "balance_status_cell_three",
                        "balance_status_cell_four", "protection_status", "version", "capacity_percent",
                        "control_status",
                        "num_cells", "battery_temp_one", "battery_temp_two", "battery_temp_three", "cell_voltage_one",
                        "cell_voltage_two", "cell_voltage_three", "cell_voltage_four"]

# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
MQTT_CLIENT = None

AVAILABLE_SHELLEYS = []

app = Flask(__name__)
socketio = SocketIO(app, debug=True, cors_allowed_origins='*', async_mode='threading')


# Update all the sql tables with the latest current data into the database for future processing and analysis
#
def update_sql_tables():
    sql_manager.update_sql_tables(CURRENT_DATA, WEATHER_DATA, STATS_DATA, BATTERIES)


#
# Update the running stats with the latest data by looping
#
def update_running_stats():
    global STATS_DATA
    last_update = datetime.today()
    current_day_of_year = datetime.today().timetuple().tm_yday
    while True:
        try:
            if CURRENT_DATA.load_amps is not None and CURRENT_DATA.battery_voltage is not None:
                STATS_DATA.day_load_wh += 0.00139 * (
                    CURRENT_DATA.load_watts if CURRENT_DATA.load_watts else 0)
                # Now comes from the victron....
                # stats_data['day_solar_wh'] += 0.00139 * current_data.get('solar_watts', 0)
                STATS_DATA.day_batt_wh += 0.00139 * CURRENT_DATA.battery_load if CURRENT_DATA.battery_load else 0 * \
                                                                                                                   CURRENT_DATA.battery_voltage if CURRENT_DATA.battery_voltage else 0
                STATS_DATA.last_charge_state = CURRENT_DATA.charge_state if CURRENT_DATA.charge_state else 'NIGHT'

            if datetime.today() > last_update + timedelta(minutes=1):
                update_sql_tables()
                last_update = datetime.today()

            if datetime.today().timetuple().tm_yday != current_day_of_year:
                current_day_of_year = datetime.today().timetuple().tm_yday
                STATS_DATA.day_load_wh = 0
                STATS_DATA.day_batt_wh = 0
                STATS_DATA.day_solar_wh = 0

            sql_manager.update_stats_data_from_db(STATS_DATA)

            # We serialize then deserialize to get around datetime not being serializable by socketio
            socketio.emit('stats_data', json.loads(json.dumps(STATS_DATA.__dict__, default=str)))
            socketio.emit('starlink_status', STARLINK["status"])
            history = copy.deepcopy(STARLINK["history"])
            history.pop('ping_drop_rate', None)
            history.pop('ping_latency', None)
            history.pop('downlink_bps', None)
            history.pop('uplink_bps', None)
            socketio.emit('starlink_history', history)
            time.sleep(5)
        except Exception as e:
            logger.error('Failure in updating stats: ' + str(e))

#
# Serve up the svelte application
#
@app.route("/")
def base():
    return send_from_directory('../svelte/public', 'index.html')


#
# Handle generic svelte application requests
#
@app.route("/<path:path>")
def home(path):
    return send_from_directory('../svelte/public', path)


#
# Take the requested field and requested number of days, and create graph data for that fields values over the specified
# time period.
#
# PARAMETERS
#   days - The number of days to fetch all of the data for
#   dataField - the name of the data field to fetch data for.  Note that this must be one of the acceptable and defined
#               acceptable data fields contained in the global variable for it to be allowed as a query, or you will get
#               back empty results
# RETURN VALUE
#   An object containing multiple lists.  One list will be the time the value was recorded, and the other lists will be
#   the corresponding values at the recorded time.  This can be easily utilized to graph the values over time
#
@app.route("/graphData")
def get_graph_data():
    global CURRENT_DATA

    days = int(request.args.get('days', 4))
    data_fields = request.args.getlist('dataField')
    if data_fields and all(field in list(CURRENT_DATA.__dict__.keys()) for field in data_fields):
        return sql_manager.get_graph_data(days, data_fields)

    return {'time': []}


@app.route("/currentData")
def get_current_data():
    global CURRENT_DATA

    return CURRENT_DATA.__dict__


@app.route("/batteryData")
def get_battery_data():
    global BATTERIES

    return list(BATTERIES.values())


#
# Take the requested field and requested number of days, and create graph data for that fields values over the specified
# time period.
#
# PARAMETERS
#   days - The number of days to fetch all of the data for
#   dataField - the name of the data field to fetch data for.  Note that this must be one of the acceptable and defined
#               acceptable data fields contained in the global variable for it to be allowed as a query, or you will get
#               back empty results
#   batteryName - The name of the battery to fetch the data for
# RETURN VALUE
#   An object containing multiple lists.  One list will be the time the value was recorded, and the other lists will be
#   the corresponding values at the recorded time.  This can be easily utilized to graph the values over time
#
@app.route("/graphBatteryData")
def get_battery_graph_data():
    global VALID_BATTERY_FIELDS

    days = int(request.args.get('days', 4))
    data_fields = request.args.getlist('dataField')
    battery_name = request.args.get('batteryName', '')
    if data_fields and all(field in VALID_BATTERY_FIELDS for field in data_fields):
        return sql_manager.get_battery_graph_data(days, data_fields, battery_name)

    return {'time': []}


@app.route("/weatherData")
def get_weather_data():
    global WEATHER_DATA

    return WEATHER_DATA.__dict__


@app.route("/weatherDailyMinMax")
def get_weather_max_min():
    min_max_data = sql_manager.get_weather_max_min()
    if min_max_data is None:
        min_max_data = {}

    return dict(min_max_data)


#
# Take the requested field and requested number of days, and create graph data for that fields values over the specified
# time period.
#
# PARAMETERS
#   days - The number of days to fetch all of the data for
#   dataField - the name of the data field to fetch data for.  Note that this must be one of the acceptable and defined
#               acceptable data fields contained in the global variable for it to be allowed as a query, or you will get
#               back empty results
# RETURN VALUE
#   An object containing two lists.  One list will be the time the value was recorded, and the second list will be the
#   corresponding value at the recorded time.  This can be easily utilized to graph the values over time
#
@app.route("/graphWxData")
def graph_wx_data():
    global WEATHER_DATA

    days = int(request.args.get('days', 1))
    data_fields = request.args.getlist('dataField')
    if data_fields and all(field in list(WEATHER_DATA.__dict__.keys()) for field in data_fields):
        return sql_manager.get_weather_graph_data(days, data_fields)

    return {'time': []}


#
# Get the last blue iris alert that we received from MQTT
#
@app.route("/blueIrisAlert")
def get_blueiris_alert():
    global BLUEIRIS_ALERT

    no_image = request.args.get('noImage', 'False').lower() == 'true'

    return_value = BLUEIRIS_ALERT.copy()

    if no_image:
        return_value.pop('alertImage', None)

    return return_value


#
# Get the last in range ADSB packet we received
#
@app.route("/adsbData")
def get_adsb_data():
    global ADSB_DATA

    no_image = request.args.get('noImage', 'False').lower() == 'true'

    return_value = ADSB_DATA.copy()

    if no_image:
        return_value.pop('picture', None)

    return return_value


#
# Return both the last lightning event seen, as well as summary data for the day
#
@app.route("/lightningData")
def get_lightning_data():
    return sql_manager.get_lightning_data()


@app.route("/statsData")
def get_stats_data():
    global STATS_DATA

    return STATS_DATA.__dict__


#
# provide the generic dishy status data through REST
#
@app.route("/starlink/status")
def starlink_status():
    return json.dumps(STARLINK['status'], indent=3)


#
# provide the dishy historical data through REST
#
@app.route("/starlink/history")
def starlink_history():
    skip_graphs = request.args.get('skipGraphs', "False").lower() == 'true'
    history = copy.deepcopy(STARLINK['history'])
    if skip_graphs:
        history.pop('ping_drop_rate', None)
        history.pop('ping_latency', None)
        history.pop('downlink_bps', None)
        history.pop('uplink_bps', None)
        history.pop('power_in', None)
    return json.dumps(history, indent=3)


#
# Get the obstruction image data, and transform into a png file and return through the get request
#
@app.route("/starlink/obstruction_image")
def starlink_obstruction_image():
    obstruction_image = STARLINK['obstruction_map']
    numpy_image = np.array(obstruction_image).astype('uint8')
    img = Image.fromarray(numpy_image)
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)
    return send_file(file_object, mimetype='image/PNG')

#
# Get the shelly object instance matching the name.  Return none if no matching Shelly
#
def get_shelly_by_name(name):
    global AVAILABLE_SHELLEYS

    for shelly in AVAILABLE_SHELLEYS:
        if shelly.get("name", None) == name:
            return shelly
    return None


#
# Get the list of available shellys
#
@app.route("/shelly")
def get_all_shellys():
    global AVAILABLE_SHELLEYS

    return json.dumps(AVAILABLE_SHELLEYS)


#
# Get the current relay status of a given device
#
@app.route("/shelly/relay/status", methods=['GET'])
def relay_status():
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        return shelly
    return {}


#
# turn the relay off of a given device
#
@app.route("/shelly/relay/off", methods=['GET'])
def turn_relay_off():
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        MQTT_CLIENT.publish('lights/' + shelly['id'] + '/command', 'off')
        return shelly
    return {}


#
# turn the relay on of a given device
#
@app.route("/shelly/relay/on", methods=['GET'])
def turn_relay_on():
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        MQTT_CLIENT.publish('lights/' + shelly['id'] + '/command', 'on')
        return shelly
    return {}


#
# power cycle the relay of a given device
#
@app.route("/shelly/relay/cycle", methods=['GET'])
def power_cycle_relay():
    delay = request.args.get("delay", default=5, type=int)
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        MQTT_CLIENT.publish('lights/' + shelly['id'] + '/command', 'cycle ' + delay)
        return shelly

    return {}

#
# Update the day accumulated data from the daily table for today.  If none is present for today, just skip updating
#
def refresh_daily_data():
    sql_manager.refresh_daily_data(STATS_DATA)


#
# update lightning information in the in memory object and in the sql database
#
def update_lightning_data(lightning_event: dict):
    try:
        sql_manager.add_lightning_event(
            int(time.time()),
            lightning_event.get("event", "unknown"),
            lightning_event.get("distance", None),
            lightning_event.get("intensity", None)
        )
    except Exception as e:
        logger.error(e)


#
# Connect to the mqtt service and subscribe to the blue iris and weewx weather topics.
#
def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        global MQTT_CLIENT

        logger.info("MQTT Client Connected, subscribing...")
        MQTT_CLIENT = c
        c.subscribe("weather/loop")
        c.subscribe("blueiris")
        c.subscribe("battery_status")
        c.subscribe("load_data")
        c.subscribe("lightning_data")
        c.subscribe("solar_charger_data")
        c.subscribe("adsb")
        c.subscribe("dc_meter_data")
        c.subscribe("battery_monitor_data")
        c.subscribe("starlink")
        c.subscribe("lights")

    def on_message(c, userdata, msg):
        global WEATHER_DATA, BLUEIRIS_ALERT, BATTERIES, ADSB_DATA

        logger.debug(f"Recieved MQTT: {msg.topic}->{msg.payload}")
        try:
            if msg.topic == "weather/loop":
                WEATHER_DATA = WEATHER_DATA.load_from_json(msg.payload)
                socketio.emit('weather_data', WEATHER_DATA.__dict__)
            elif msg.topic == "blueiris":
                BLUEIRIS_ALERT = json.loads(msg.payload)
                BLUEIRIS_ALERT['time'] = int(time.time() * 1000)
                BLUEIRIS_ALERT['id'] = str(uuid.uuid4())
                socketio.emit('blueiris_alert', BLUEIRIS_ALERT)
                file = open(b"last_blue_iris_alert.pkl", "wb")
                pickle.dump(BLUEIRIS_ALERT, file)
                file.close()
            elif msg.topic == "adsb":
                ADSB_DATA = json.loads(msg.payload)
                ADSB_DATA['id'] = str(uuid.uuid4())
                socketio.emit('adsb_data', ADSB_DATA)
                file = open(b"last_adsb_data.pkl", "wb")
                pickle.dump(ADSB_DATA, file)
                file.close()
            elif msg.topic == "battery_status":
                logger.debug("Received Battery Status")
                battery_info = json.loads(msg.payload)
                BATTERIES[battery_info["name"]] = battery_info
                total_percent = 0
                for battery_name, battery in BATTERIES.items():
                    total_percent += battery.get("capacity_percent", 0)
                CURRENT_DATA.battery_percent = total_percent / len(BATTERIES.items())
                socketio.emit("battery_data", list(BATTERIES.values()));
            elif msg.topic == "lightning_data":
                logger.debug("Received lightning data")
                lightning_data = json.loads(msg.payload)
                update_lightning_data(lightning_data)
                socketio.emit('lightning_data', lightning_data)
            elif msg.topic == "solar_charger_data":
                charger_data = json.loads(msg.payload)
                CURRENT_DATA.solar_watts = charger_data.get("solar_watts", 0)
                CURRENT_DATA.battery_charge_current = charger_data.get("battery_charge_current", 0)
                CURRENT_DATA.charge_state = charger_data.get("charge_state", "OTHER")
                CURRENT_DATA.battery_voltage = charger_data.get("battery_voltage", 0)
                socketio.emit('current_data', CURRENT_DATA.__dict__)
                # We need to protect against the charge controller resetting this running stat before we increment the day,
                # so only capture it if it went up as it should never decrement.  We reset this elsewhere to zero when we
                # recognize a day has passed
                if STATS_DATA.day_solar_wh < charger_data.get("day_solar_wh", 0):
                    STATS_DATA.day_solar_wh = charger_data.get("day_solar_wh", 0)
            elif msg.topic == "dc_meter_data":
                meter_data = json.loads(msg.payload)
                if meter_data['device_name'] == "Cabin Load":
                    CURRENT_DATA.load_amps = meter_data['amps']
                    CURRENT_DATA.load_watts = meter_data['watts']
                    CURRENT_DATA.load_volts = meter_data['volts']
                    socketio.emit('current_data', CURRENT_DATA.__dict__)
            elif msg.topic == "battery_monitor_data":
                meter_data = json.loads(msg.payload)
                if meter_data['device_name'] == "Battery Load":
                    CURRENT_DATA.battery_load = meter_data['amps']
            elif msg.topic == "starlink":
                starlink_data = json.loads(msg.payload)
                STARLINK['status'] = starlink_data.get('status', None)
                STARLINK['history'] = starlink_data.get('history', None)
                STARLINK['obstruction_map'] = starlink_data.get('obstruction_map', [])
            elif msg.topic == "lights":
                update = json.loads(msg.payload)
                device = next((d for d in AVAILABLE_SHELLEYS if d['id'] == update['id']), None)
                if device:
                    device['ison'] = update['ison']
                else:
                    AVAILABLE_SHELLEYS.append(update)
        except Exception as e:
            logger.error(f"Failed to process mqtt message: {e}")
            logger.error(f"Payload of message: {msg.payload}")

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
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()


def create_sql_tables_if_not_exist():
    sql_manager.create_sql_tables_if_not_exist()


def main(proxy=None):
    global BLUEIRIS_ALERT, AVAILABLE_SHELLEYS, SHELLY_DEVICE_ADDRESSES, ADSB_DATA

    create_sql_tables_if_not_exist()

    try:
        if os.path.exists("last_blue_iris_alert.pkl"):
            BLUEIRIS_ALERT = pickle.load(open("last_blue_iris_alert.pkl", "rb"))
    except Exception as e:
        print("Failed to load last blue iris alert: " + str(e))

    try:
        if os.path.exists("last_adsb_data.pkl"):
            ADSB_DATA = pickle.load(open("last_adsb_data.pkl", "rb"))
    except Exception as e:
        print("Failed to load last adsb data: " + str(e))

    refresh_daily_data()

    stats_thread = threading.Thread(target=update_running_stats, args=())
    stats_thread.daemon = True
    stats_thread.start()

    mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
    mqtt_thread.daemon = True
    mqtt_thread.start()

    app.run(port=8050, host='0.0.0.0')


#
# Startup the flask server on port 9999.  Change the port here if you want it listening somewhere else, and simply
# execute this python file to startup your server and serve the svelte app
#
if __name__ == "__main__":
    main()
