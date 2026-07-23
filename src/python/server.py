import copy
import os
import pickle
from pathlib import Path

from quart import Quart, send_from_directory, send_file, request
import time
import threading
import asyncio
import io
import json
import numpy as np
import logging
import paho.mqtt.client as mqtt
import uuid
import socketio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from datetime import datetime, timedelta
from PIL import Image
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
BIRDS_DETECTED = {}

# List of valid fields for querying battery graph data.  This protects against sql injection using a dynamic field.
VALID_BATTERY_FIELDS = ["name", "voltage", "current", "residual_capacity", "nominal_capacity", "cycles",
                        "balance_status_cell_one", "balance_status_cell_two", "balance_status_cell_three",
                        "balance_status_cell_four", "protection_status", "version", "capacity_percent",
                        "control_status",
                        "num_cells", "battery_temp_one", "battery_temp_two", "battery_temp_three", "cell_voltage_one",
                        "cell_voltage_two", "cell_voltage_three", "cell_voltage_four"]

# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
MQTT_CLIENT : mqtt.Client

AVAILABLE_SHELLEYS = []

# The main asyncio event loop that runs the Quart/hypercorn server. This is set in main() and is used to safely
# schedule socketio emissions from background threads (mqtt client, stats updater) that are not running as part
# of the asyncio event loop.
MAIN_EVENT_LOOP: asyncio.AbstractEventLoop = None

# Resolves the absolute path to Svelte's public build folder relative to this file
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "svelte" / "public"

app = Quart(__name__)
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
asgi_app = socketio.ASGIApp(sio, app)


def emit(event, data):
    """Schedules a socketio emit call to run on the main event loop. This is safe to call from any thread,
    including background threads that are not running as part of the asyncio event loop.

    Args:
        event: The name of the socketio event to emit.
        data: The data to emit alongside the event.
    """
    if MAIN_EVENT_LOOP is not None:
        asyncio.run_coroutine_threadsafe(sio.emit(event, data), MAIN_EVENT_LOOP)


def update_sql_tables():
    """Updates all the sql tables with the latest current data into the database for future processing and analysis."""
    sql_manager.update_sql_tables(CURRENT_DATA, WEATHER_DATA, STATS_DATA, BATTERIES)


def update_running_stats():
    """Updates the running stats with the latest data by looping indefinitely."""
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
            emit('stats_data', json.loads(json.dumps(STATS_DATA.__dict__, default=str)))
            emit('starlink_status', STARLINK["status"])
            history = copy.deepcopy(STARLINK["history"])
            history.pop('ping_drop_rate', None)
            history.pop('ping_latency', None)
            history.pop('downlink_bps', None)
            history.pop('uplink_bps', None)
            emit('starlink_history', history)
            time.sleep(5)
        except Exception as e:
            logger.error('Failure in updating stats: ' + str(e))

@app.route("/")
async def base():
    """Serves up the svelte application.

    Returns:
        quart.Response: The svelte application's index.html file.
    """
    global PUBLIC_DIR

    return await send_from_directory(PUBLIC_DIR, 'index.html')


@app.route("/<path:path>")
async def home(path):
    """Handles generic svelte application requests.

    Args:
        path: The path of the static file being requested.

    Returns:
        quart.Response: The requested static file from the svelte application.
    """
    global PUBLIC_DIR

    return await send_from_directory(PUBLIC_DIR, path)


@app.route("/graphData")
async def get_graph_data():
    """Takes the requested field and requested number of days, and creates graph data for that field's values
    over the specified time period.

    Args:
        days: The number of days to fetch all of the data for.
        dataField: The name of the data field to fetch data for. Note that this must be one of the acceptable and
            defined data fields contained in the current data global variable to be allowed as a query, or you
            will get back empty results.

    Returns:
        dict: An object containing multiple lists. One list will be the time the value was recorded, and the other
        lists will be the corresponding values at the recorded time. This can be easily utilized to graph the
        values over time.
    """
    global CURRENT_DATA

    days = int(request.args.get('days', 4))
    data_fields = request.args.getlist('dataField')
    if data_fields and all(field in list(CURRENT_DATA.__dict__.keys()) for field in data_fields):
        return sql_manager.get_graph_data(days, data_fields)

    return {'time': []}


@app.route("/currentData")
async def get_current_data():
    """Gets the current power meter data.

    Returns:
        dict: The current power data attributes.
    """
    global CURRENT_DATA

    return CURRENT_DATA.__dict__


@app.route("/batteryData")
async def get_battery_data():
    """Gets the current data for all known batteries.

    Returns:
        list: The list of battery data objects currently tracked.
    """
    global BATTERIES

    return list(BATTERIES.values())


@app.route("/graphBatteryData")
async def get_battery_graph_data():
    """Takes the requested field and requested number of days, and creates graph data for that field's values
    over the specified time period.

    Args:
        days: The number of days to fetch all of the data for.
        dataField: The name of the data field to fetch data for. Note that this must be one of the acceptable and
            defined acceptable data fields contained in the global variable for it to be allowed as a query, or
            you will get back empty results.
        batteryName: The name of the battery to fetch the data for.

    Returns:
        dict: An object containing multiple lists. One list will be the time the value was recorded, and the other
        lists will be the corresponding values at the recorded time. This can be easily utilized to graph the
        values over time.
    """
    global VALID_BATTERY_FIELDS

    days = int(request.args.get('days', 4))
    data_fields = request.args.getlist('dataField')
    battery_name = request.args.get('batteryName', '')
    if data_fields and all(field in VALID_BATTERY_FIELDS for field in data_fields):
        return sql_manager.get_battery_graph_data(days, data_fields, battery_name)

    return {'time': []}


@app.route("/weatherData")
async def get_weather_data():
    """Gets the current weather data.

    Returns:
        dict: The current weather data attributes.
    """
    global WEATHER_DATA

    return WEATHER_DATA.__dict__


@app.route("/weatherDailyMinMax")
async def get_weather_max_min():
    """Gets the daily minimum and maximum weather values recorded so far today.

    Returns:
        dict: The daily minimum and maximum weather values, or an empty dict if none are available.
    """
    min_max_data = sql_manager.get_weather_max_min()
    if min_max_data is None:
        min_max_data = {}

    return dict(min_max_data)


@app.route("/graphWxData")
async def graph_wx_data():
    """Takes the requested field and requested number of days, and creates graph data for that field's values
    over the specified time period.

    Args:
        days: The number of days to fetch all of the data for.
        dataField: The name of the data field to fetch data for. Note that this must be one of the acceptable and
            defined acceptable data fields contained in the global variable for it to be allowed as a query, or
            you will get back empty results.

    Returns:
        dict: An object containing two lists. One list will be the time the value was recorded, and the second
        list will be the corresponding value at the recorded time. This can be easily utilized to graph the
        values over time.
    """
    global WEATHER_DATA

    days = int(request.args.get('days', 1))
    data_fields = request.args.getlist('dataField')
    if data_fields and all(field in list(WEATHER_DATA.__dict__.keys()) for field in data_fields):
        return sql_manager.get_weather_graph_data(days, data_fields)

    return {'time': []}


@app.route("/blueIrisAlert")
async def get_blueiris_alert():
    """Gets the last blue iris alert that we received from MQTT.

    Args:
        noImage: If 'true', the alert image will be excluded from the returned data.

    Returns:
        dict: The last blue iris alert data.
    """
    global BLUEIRIS_ALERT

    no_image = request.args.get('noImage', 'False').lower() == 'true'

    return_value = BLUEIRIS_ALERT.copy()

    if no_image:
        return_value.pop('alertImage', None)

    return return_value


@app.route("/adsbData")
async def get_adsb_data():
    """Gets the last in range ADSB packet we received.

    Args:
        noImage: If 'true', the picture will be excluded from the returned data.

    Returns:
        dict: The last ADSB data received.
    """
    global ADSB_DATA

    no_image = request.args.get('noImage', 'False').lower() == 'true'

    return_value = ADSB_DATA.copy()

    if no_image:
        return_value.pop('picture', None)

    return return_value


@app.route("/lightningData")
async def get_lightning_data():
    """Returns both the last lightning event seen, as well as summary data for the day.

    Returns:
        dict: The last lightning event and the day's summary data.
    """
    return sql_manager.get_lightning_data()


@app.route("/birdData")
async def get_bird_data():
    """Gets the current bird data information stored in the global variable, keyed by scientific name.

    Returns:
        dict: The currently detected birds, keyed by scientific name.
    """
    global BIRDS_DETECTED

    return BIRDS_DETECTED


@app.route("/birdHistory", methods=["GET", "DELETE"])
async def get_bird_history():
    """Gets the full history of birds ever seen, as recorded in the sql database, or deletes a bird's history.

    Each entry contains the scientific name, common name, the time the bird was most recently heard, and the
    total number of times it has been heard. The list is ordered by the time most recently heard, descending.
    When the request method is DELETE, removes the bird matching scientificName from the database and from the
    in-memory store.

    Args:
        scientificName: (DELETE only) The scientific name of the bird whose history should be deleted.

    Returns:
        dict or tuple: The bird history list on GET, or a success/error dict (with a 400 status on error) on
        DELETE.
    """
    global BIRDS_DETECTED

    if request.method == "DELETE":
        scientific_name = request.args.get('scientificName', None)

        if not scientific_name:
            return {"success": False, "error": "scientificName is required"}, 400

        sql_manager.delete_bird_data(scientific_name)
        BIRDS_DETECTED.pop(scientific_name, None)

        return {"success": True}

    return sql_manager.get_bird_history()


@app.route("/birdDetails")
async def get_bird_details():
    """Gets the details (most recent sighting and total count) of a single bird, keyed by scientific name, as
    recorded in the sql database. This is used to display bird details for birds that are no longer held in the
    in-memory BIRDS_DETECTED store.

    Args:
        scientificName: The scientific name of the bird to fetch details for.

    Returns:
        dict: The bird's details, or an empty dict if scientificName is missing or no bird is found.
    """
    scientific_name = request.args.get('scientificName', None)

    if not scientific_name:
        return {}

    bird = sql_manager.get_bird_details(scientific_name)

    return bird or {}


@app.route("/birdPicture")
async def get_bird_picture():
    """Gets the picture of a bird stored in the database, keyed by scientific name.

    Args:
        scientificName: The scientific name of the bird to fetch the picture for.

    Returns:
        dict: The scientific name and image data, or an empty dict if scientificName is missing.
    """
    scientific_name = request.args.get('scientificName', None)

    if not scientific_name:
        return {}

    image = sql_manager.get_bird_picture(scientific_name)

    return {'scientific_name': scientific_name, 'image': image}


@app.route("/statsData")
async def get_stats_data():
    """Gets the current accumulated stats data.

    Returns:
        dict: The current stats data attributes.
    """
    global STATS_DATA

    return STATS_DATA.__dict__


@app.route("/starlink/status")
async def starlink_status():
    """Provides the generic dishy status data through REST.

    Returns:
        str: The JSON serialized Starlink status data.
    """
    return json.dumps(STARLINK['status'], indent=3)


@app.route("/starlink/history")
async def starlink_history():
    """Provides the dishy historical data through REST.

    Args:
        skipGraphs: If 'true', the graph-heavy history fields (ping drop rate, ping latency, downlink/uplink bps,
            and power in) will be excluded from the returned data.

    Returns:
        str: The JSON serialized Starlink history data.
    """
    skip_graphs = request.args.get('skipGraphs', "False").lower() == 'true'
    history = copy.deepcopy(STARLINK['history'])
    if skip_graphs:
        history.pop('ping_drop_rate', None)
        history.pop('ping_latency', None)
        history.pop('downlink_bps', None)
        history.pop('uplink_bps', None)
        history.pop('power_in', None)
    return json.dumps(history, indent=3)


@app.route("/starlink/obstruction_image")
async def starlink_obstruction_image():
    """Gets the obstruction image data, and transforms it into a png file and returns it through the get request.

    Returns:
        quart.Response: The obstruction map rendered as a PNG image.
    """
    obstruction_image = STARLINK['obstruction_map']
    numpy_image = np.array(obstruction_image).astype('uint8')
    img = Image.fromarray(numpy_image)
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)
    return await send_file(file_object, mimetype='image/PNG')

def get_shelly_by_name(name):
    """Gets the shelly object instance matching the name.

    Args:
        name: The name of the shelly device to find.

    Returns:
        dict or None: The matching shelly device, or None if no matching Shelly is found.
    """
    global AVAILABLE_SHELLEYS

    for shelly in AVAILABLE_SHELLEYS:
        if shelly.get("name", None) == name:
            return shelly
    return None


@app.route("/shelly")
async def get_all_shellys():
    """Gets the list of available shellys.

    Returns:
        str: The JSON serialized list of available Shelly devices.
    """
    global AVAILABLE_SHELLEYS

    return json.dumps(AVAILABLE_SHELLEYS)


@app.route("/shelly/relay/status", methods=['GET'])
async def relay_status():
    """Gets the current relay status of a given device.

    Args:
        name: The name of the shelly device to fetch the status for.

    Returns:
        dict: The shelly device data, or an empty dict if no matching device is found.
    """
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        return shelly
    return {}


@app.route("/shelly/relay/off", methods=['GET'])
async def turn_relay_off():
    """Turns the relay off of a given device.

    Args:
        name: The name of the shelly device to turn off.

    Returns:
        dict: The shelly device data, or an empty dict if no matching device is found.
    """
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        MQTT_CLIENT.publish('lights/' + shelly['id'] + '/command', 'off')
        return shelly
    return {}


@app.route("/shelly/relay/on", methods=['GET'])
async def turn_relay_on():
    """Turns the relay on of a given device.

    Args:
        name: The name of the shelly device to turn on.

    Returns:
        dict: The shelly device data, or an empty dict if no matching device is found.
    """
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        MQTT_CLIENT.publish('lights/' + shelly['id'] + '/command', 'on')
        return shelly
    return {}


@app.route("/shelly/relay/cycle", methods=['GET'])
async def power_cycle_relay():
    """Power cycles the relay of a given device.

    Args:
        name: The name of the shelly device to power cycle.
        delay: The number of seconds to wait before turning the relay back on. Defaults to 5.

    Returns:
        dict: The shelly device data, or an empty dict if no matching device is found.
    """
    delay : int = request.args.get("delay", default=5, type=int)
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        MQTT_CLIENT.publish('lights/' + shelly['id'] + '/command', 'cycle ' + str(delay))
        return shelly

    return {}

def refresh_daily_data():
    """Updates the day accumulated data from the daily table for today. If none is present for today, just skips
    updating.
    """
    sql_manager.refresh_daily_data(STATS_DATA)


def update_lightning_data(lightning_event: dict):
    """Updates lightning information in the in memory object and in the sql database.

    Args:
        lightning_event: The lightning event data containing event type, distance, and intensity.
    """
    try:
        sql_manager.add_lightning_event(
            int(time.time()),
            lightning_event.get("event", "unknown"),
            lightning_event.get("distance", None),
            lightning_event.get("intensity", None)
        )
    except Exception as e:
        logger.error(e)


def start_mqtt_client():
    """Connects to the mqtt service and subscribes to the blue iris and weewx weather topics."""
    def on_connect(c, userdata, flags, rc):
        """Handles the MQTT client connect event by subscribing to all required topics.

        Args:
            c: The MQTT client instance that connected.
            userdata: The private user data as set in the client constructor.
            flags: Response flags sent by the broker.
            rc: The connection result code.
        """
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
        c.subscribe("birdnet")

    def handle_weather_loop(c, userdata, msg):
        """Handles incoming weather loop MQTT messages by updating the weather data and emitting it via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the weather loop JSON payload.
        """
        global WEATHER_DATA

        try:
            WEATHER_DATA = WEATHER_DATA.load_from_json(msg.payload)
            emit('weather_data', WEATHER_DATA.__dict__)
        except Exception as e:
            logger.error(f"Error handling weather loop message: {e}")

    def handle_blueiris(c, userdata, msg):
        """Handles incoming blue iris alert MQTT messages by updating and persisting the alert data and emitting
        it via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the blue iris alert JSON payload.
        """
        global BLUEIRIS_ALERT

        try:
            BLUEIRIS_ALERT = json.loads(msg.payload)
            BLUEIRIS_ALERT['time'] = int(time.time() * 1000)
            BLUEIRIS_ALERT['id'] = str(uuid.uuid4())
            emit('blueiris_alert', BLUEIRIS_ALERT)
            file = open(b"last_blue_iris_alert.pkl", "wb")
            pickle.dump(BLUEIRIS_ALERT, file)
            file.close()
        except Exception as e:
            logger.error(f"Error handling blueiris message: {e}")
            logger.error(f"Invalid json: {msg.payload}")

    def handle_birdnet(c, userdata, msg):
        """Handles incoming birdnet detection MQTT messages by updating the in-memory bird store, persisting new
        or refreshed detections to the sql database, and emitting the detection via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the birdnet detection JSON payload.
        """
        global BIRDS_DETECTED

        try:
            bird_data = json.loads(msg.payload)
            bird_data['time'] = int(time.time() * 1000)
            bird_data['id'] = str(uuid.uuid4())
            image = bird_data.pop('image', None)
            scientific_name = bird_data.get('scientific_name')

            now = int(time.time() * 1000)
            bird_persist_threshold_ms = 5 * 60 * 1000

            if scientific_name in BIRDS_DETECTED:
                # Keep the new indicator active for the rest of the day (until the daily reboot clears
                # BIRDS_DETECTED), rather than clearing it on subsequent detections of the same bird.
                bird_data['is_new'] = BIRDS_DETECTED[scientific_name]['bird'].get('is_new', False)
                BIRDS_DETECTED[scientific_name]['count'] += 1
                BIRDS_DETECTED[scientific_name]['bird'] = bird_data
                last_persisted = BIRDS_DETECTED[scientific_name].get('last_persisted', 0)
            else:
                bird_data['is_new'] = not sql_manager.bird_seen_before(scientific_name)
                BIRDS_DETECTED[scientific_name] = {'count': 1, 'bird': bird_data}
                last_persisted = 0
                emit('newbird', bird_data)

            if now - last_persisted >= bird_persist_threshold_ms:
                sql_manager.add_bird_data(bird_data)
                BIRDS_DETECTED[scientific_name]['last_persisted'] = now

            if image and scientific_name and not sql_manager.bird_picture_exists(scientific_name):
                sql_manager.add_bird_picture(scientific_name, image)

            emit('birdnet', bird_data)
        except Exception as e:
            logger.error(f"Error handling birdnet message: {e}")

    def handle_adsb(c, userdata, msg):
        """Handles incoming ADSB MQTT messages by updating and persisting the ADSB data and emitting it via
        socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the ADSB JSON payload.
        """
        global ADSB_DATA

        try:
            ADSB_DATA = json.loads(msg.payload)
            ADSB_DATA['id'] = str(uuid.uuid4())
            emit('adsb_data', ADSB_DATA)
            file = open(b"last_adsb_data.pkl", "wb")
            pickle.dump(ADSB_DATA, file)
            file.close()
        except Exception as e:
            logger.error(f"Error handling adsb message: {e}")

    def handle_battery_status(c, userdata, msg):
        """Handles incoming battery status MQTT messages by updating the batteries store, recomputing the overall
        battery percentage, and emitting the updated battery data via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the battery status JSON payload.
        """
        try:
            logger.debug("Received Battery Status")
            battery_info = json.loads(msg.payload)
            BATTERIES[battery_info["name"]] = battery_info
            total_percent = 0
            for battery_name, battery in BATTERIES.items():
                total_percent += battery.get("capacity_percent", 0)
            CURRENT_DATA.battery_percent = total_percent / len(BATTERIES.items())
            emit("battery_data", list(BATTERIES.values()))
        except Exception as e:
            logger.error(f"Error handling battery status message: {e}")

    def handle_lightning_data(c, userdata, msg):
        """Handles incoming lightning data MQTT messages by persisting the event and emitting it via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the lightning data JSON payload.
        """
        try:
            logger.debug("Received lightning data")
            lightning_data = json.loads(msg.payload)
            update_lightning_data(lightning_data)
            emit('lightning_data', lightning_data)
        except Exception as e:
            logger.error(f"Error handling lightning data message: {e}")

    def handle_solar_charger_data(c, userdata, msg):
        """Handles incoming solar charger data MQTT messages by updating the current and stats data with the
        latest charger readings, and emitting the current data via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the solar charger data JSON payload.
        """
        try:
            charger_data = json.loads(msg.payload)
            CURRENT_DATA.solar_watts = charger_data.get("solar_watts", 0)
            CURRENT_DATA.battery_charge_current = charger_data.get("battery_charge_current", 0)
            CURRENT_DATA.charge_state = charger_data.get("charge_state", "OTHER")
            CURRENT_DATA.battery_voltage = charger_data.get("battery_voltage", 0)
            CURRENT_DATA.day_solar_wh = charger_data.get("day_solar_wh", 0)
            emit('current_data', CURRENT_DATA.__dict__)
            # We need to protect against the charge controller resetting this running stat before we increment the day,
            # so only capture it if it went up as it should never decrement.  We reset this elsewhere to zero when we
            # recognize a day has passed
            if STATS_DATA.day_solar_wh < charger_data.get("day_solar_wh", 0):
                STATS_DATA.day_solar_wh = charger_data.get("day_solar_wh", 0)
        except Exception as e:
            logger.error(f"Error handling solar charger data message: {e}")

    def handle_dc_meter_data(c, userdata, msg):
        """Handles incoming DC meter data MQTT messages by updating the current cabin load data and emitting it
        via socketio.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the DC meter data JSON payload.
        """
        try:
            meter_data = json.loads(msg.payload)
            if meter_data['device_name'] == "Cabin Load":
                CURRENT_DATA.load_amps = meter_data['amps']
                CURRENT_DATA.load_watts = meter_data['watts']
                CURRENT_DATA.load_volts = meter_data['volts']
                emit('current_data', CURRENT_DATA.__dict__)
        except Exception as e:
            logger.error(f"Error handling DC meter data message: {e}")

    def handle_battery_monitor_data(c, userdata, msg):
        """Handles incoming battery monitor data MQTT messages by updating the current battery load data.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the battery monitor data JSON payload.
        """
        try:
            meter_data = json.loads(msg.payload)
            if meter_data['device_name'] == "Battery Load":
                CURRENT_DATA.battery_load = meter_data['amps']
        except Exception as e:
            logger.error(f"Error handling DC meter data message: {e}")

    def handle_starlink(c, userdata, msg):
        """Handles incoming Starlink MQTT messages by updating the Starlink status, history, and obstruction map.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the Starlink data JSON payload.
        """
        try:
            starlink_data = json.loads(msg.payload)
            STARLINK['status'] = starlink_data.get('status', None)
            STARLINK['history'] = starlink_data.get('history', None)
            STARLINK['obstruction_map'] = starlink_data.get('obstruction_map', [])
        except Exception as e:
            logger.error(f"Error handling Starlink data message: {e}")

    def handle_lights(c, userdata, msg):
        """Handles incoming lights MQTT messages by updating an existing Shelly device's state or adding it to
        the list of available Shellys if it is not already known.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message containing the lights JSON payload.
        """
        try:
            update = json.loads(msg.payload)
            device = next((d for d in AVAILABLE_SHELLEYS if d['id'] == update['id']), None)
            if device:
                device['ison'] = update['ison']
            else:
                AVAILABLE_SHELLEYS.append(update)
        except Exception as e:
            logger.error(f"Error handling lights data message: {e}")

    def on_message(c, userdata, msg):
        """Handles any MQTT message that does not have a specific callback registered for its topic.

        Args:
            c: The MQTT client instance that received the message.
            userdata: The private user data as set in the client constructor.
            msg: The MQTT message that has no registered callback.
        """
        logger.debug(f"Recieved MQTT: {msg.topic}->{msg.payload}")
        logger.warning(f"No callback registered for topic: {msg.topic}")

    def on_disconnect(c, userdata, rc):
        """Handles the MQTT client disconnect event by continually attempting to reconnect until successful.

        Args:
            c: The MQTT client instance that disconnected.
            userdata: The private user data as set in the client constructor.
            rc: The disconnection result code.
        """
        logger.info(f"MQTT Client Disconnected due to {rc}, retrying....")
        while True:
            try:
                c.reconnect()
                break
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}, will retry....")
            time.sleep(30)

    client = mqtt.Client()
    client.message_callback_add("weather/loop", handle_weather_loop)
    client.message_callback_add("blueiris", handle_blueiris)
    client.message_callback_add("birdnet", handle_birdnet)
    client.message_callback_add("adsb", handle_adsb)
    client.message_callback_add("battery_status", handle_battery_status)
    client.message_callback_add("lightning_data", handle_lightning_data)
    client.message_callback_add("solar_charger_data", handle_solar_charger_data)
    client.message_callback_add("dc_meter_data", handle_dc_meter_data)
    client.message_callback_add("battery_monitor_data", handle_battery_monitor_data)
    client.message_callback_add("starlink", handle_starlink)
    client.message_callback_add("lights", handle_lights)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    retries = 5
    while retries > 0:
        try:
            client.connect(MQTT_SERVER_ADDR, 1883, 60)
            break
        except:
            logger.error(f"Failed to connect to MQTT server, retries remaining: {retries}")
            retries -= 1
            time.sleep(10)
    if retries <= 0:
        logger.error("Failed to connect to MQTT server, exiting....")
        os._exit(1)
    client.loop_forever()


def create_sql_tables_if_not_exist():
    """Creates all required sql tables in the database if they do not already exist."""
    sql_manager.create_sql_tables_if_not_exist()


def main(proxy=None):
    """Starts up the power meter server: initializes the database, restores last-known blue iris and ADSB data,
    refreshes daily stats, starts the background stats and MQTT threads, and runs the Quart application.

    Args:
        proxy: Unused, reserved for future proxy configuration support.
    """
    global BLUEIRIS_ALERT, AVAILABLE_SHELLEYS, SHELLY_DEVICE_ADDRESSES, ADSB_DATA, MAIN_EVENT_LOOP

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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    MAIN_EVENT_LOOP = loop

    config = Config()
    config.bind = ['0.0.0.0:8050']

    loop.run_until_complete(serve(asgi_app, config))


if __name__ == "__main__":
    # Startup the quart server on port 8050.  Change the port here if you want it listening somewhere else, and
    # simply execute this python file to startup your server and serve the svelte app
    main()
