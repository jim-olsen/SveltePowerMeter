import os
import pickle
from flask import Flask, send_from_directory, send_file, request
import time
import threading
from datetime import datetime, timedelta
from PIL import Image
from Starlink import Starlink
from Shelly import Shelly
import io
import json
import numpy as np
import sqlite3
import logging
import paho.mqtt.client as mqtt
import uuid

logging.basicConfig()
logging.getLogger('power_meter').setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logger = logging.getLogger('power_meter')

current_data = {}
stats_data = {
    'current_date': datetime.today().date(),
    'total_load_wh': 0,
    'total_net': [],
    'day_load_wh': 0,
    'total_solar_wh': 0,
    'day_solar_wh': 0,
    'day_batt_wh': 0,
    'last_charge_state': 'MPPT',
    'avg_load': 0.0,
    'avg_net': 0.0,
    'avg_solar': 0.0
}
WEATHER_DATA = {}
LIGHTNING_DATA = {}
BLUEIRIS_ALERT = {}
BATTERIES = {}
LAST_BEACON_RECEIVED = time.time()

# List of valid fields for querying for weather graph data.  This protects against sql injection using a dynamic field
# based request
VALID_WX_FIELDS = ["altimeter_inHg", "appTemp_F", "barometer_inHg", "cloudbase_foot", "daily_rain", "dateTime",
                   "dayRain_in", "day_of_year", "dewpoint_F", "heatindex_F", "hourRain_in", "humidex_F", "inTemp_F",
                   "minute_of_day", "outHumidity", "outTemp_F", "pressure_inHg", "rain24_in", "rainRate_inch_per_hour",
                   "rain_in", "rain_total", "usUnits", "windDir", "windSpeed_mph", "wind_average", "windchill_F"]

# List of valid fields for querying power graph data.  This protects against sql injection using a dynamic field
# based request
VALID_POWER_FIELDS = ["battery_load", "load_amps", "load_watts", "battery_voltage", "battery_watts", "net_production",
                      "battery_sense_voltage", "battery_voltage_slow", "battery_daily_minimum_voltage",
                      "battery_daily_maximum_voltage", "target_regulation_voltage", "array_voltage",
                      "array_charge_current", "battery_charge_current", "battery_charge_current_slow", "input_power",
                      "solar_watts", "heatsink_temperature", "battery_temperature", "charge_state",
                      "seconds_in_absorption_daily", "seconds_in_float_daily", "seconds_in_equalization_daily"]

# List of valid fields for querying battery graph data.  This protects against sql injection using a dynamic field.
VALID_BATTERY_FIELDS = ["name", "voltage", "current", "residual_capacity", "nominal_capacity", "cycles",
                        "balance_status_cell_one", "balance_status_cell_two", "balance_status_cell_three",
                        "balance_status_cell_four", "protection_status", "version", "capacity_percent", "control_status",
                        "num_cells", "battery_temp_one", "battery_temp_two", "battery_temp_three", "cell_voltage_one",
                        "cell_voltage_two", "cell_voltage_three", "cell_voltage_four"]

# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'

# For now I have shelly devices manually listed.  There is not a great discovery mechanism built in but am exploring
# options
SHELLY_DEVICE_ADDRESSES = ['http://10.0.10.40', 'http://10.0.10.41', 'http://10.0.10.42', 'http://10.0.10.43',
                           'http://10.0.10.44', 'http://10.0.10.45', 'http://10.0.10.46']

AVAILABLE_SHELLEYS = []

app = Flask(__name__)
dishy = Starlink()


#
# Update all the sql tables with the latest current data into the database for future processing and analysis
#
def update_sql_tables():
    global current_data
    global WEATHER_DATA
    global stats_data

    sql_connection = sqlite3.connect("powerdata.db")
    with sql_connection:
        cursor = sql_connection.execute("SELECT record_date FROM daily_power_data where record_date = ?",
                                        [int(time.mktime(datetime.today().replace(hour=0, minute=0, second=0,
                                                                                  microsecond=0).timetuple()))])
        if cursor.fetchone() is None:
            stats_data['day_load_wh'] = 0
            stats_data['day_solar_wh'] = 0
            stats_data['day_batt_wh'] = 0

        sql_connection.execute('''INSERT OR REPLACE INTO daily_power_data (record_date, day_load_wh, day_solar_wh, 
                day_batt_wh, last_charge_state) VALUES (?,?,?,?,?);''',
                               (
                                   int(time.mktime(datetime.today().replace(hour=0, minute=0, second=0,
                                                                            microsecond=0).timetuple())),
                                   stats_data.get('day_load_wh', None), stats_data.get('day_solar_wh', None),
                                   stats_data.get('day_batt_wh', None), stats_data.get('last_charge_state', None)))
        sql_connection.execute('''INSERT OR REPLACE INTO power_data (record_time, battery_load, load_amps,
                                load_watts, battery_voltage, battery_watts, net_production, battery_sense_voltage, 
                                battery_voltage_slow, battery_daily_minimum_voltage, battery_daily_maximum_voltage,
                                target_regulation_voltage, array_voltage, array_charge_current, battery_charge_current,
                                battery_charge_current_slow, input_power, solar_watts, heatsink_temperature,
                                battery_temperature, charge_state, seconds_in_absorption_daily,
                                seconds_in_float_daily, seconds_in_equalization_daily) VALUES 
                                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
                               (
                                   int(time.time()),
                                   current_data.get('battery_load', None),
                                   current_data.get('load_amps', None),
                                   current_data.get('load_amps', 0) * current_data.get('battery_voltage', 0),
                                   current_data.get('battery_voltage', None),
                                   current_data.get('battery_voltage', 0) * current_data.get('battery_load', 0),
                                   current_data.get('day_solar_wh', 0) - current_data.get('day_load_wh', 0),
                                   current_data.get('battery_sense_voltage', None),
                                   current_data.get('battery_voltage_slow', None),
                                   current_data.get('battery_daily_minimum_voltage', None),
                                   current_data.get('battery_daily_maximum_voltage', None),
                                   current_data.get('target_regulation_voltage', None),
                                   current_data.get('array_voltage', None),
                                   current_data.get('array_charge_current', None),
                                   current_data.get('battery_charge_current', None),
                                   current_data.get('battery_charge_current_slow', None),
                                   current_data.get('input_power', None),
                                   current_data.get('solar_watts', None),
                                   current_data.get('heatsink_temperature', None),
                                   current_data.get('battery_temperature', None),
                                   current_data.get('charge_state', None),
                                   current_data.get('seconds_in_absorption_daily', None),
                                   current_data.get('seconds_in_float_daily', None),
                                   current_data.get('seconds_in_equalization_daily', None)
                               ))

    wx_sql_connection = sqlite3.connect("wxdata.db")
    with wx_sql_connection:
        wx_sql_connection.execute('''INSERT OR REPLACE INTO wx_data (record_time,
                altimeter_inHg,
                barometer_inHg,
                cloudbase_foot,
                daily_rain,
                dayRain_in,
                dewpoint_F,
                heatindex_F,
                hourRain_in,
                humidex_F,
                inTemp_F,
                outHumidity,
                outTemp_F,
                pressure_inHg,
                rain24_in,
                rainRate_inch_per_hour,
                rain_in,
                rain_total,
                windSpeed_mph,
                wind_average,
                windchill_F
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (int(time.time()),
                      WEATHER_DATA.get("altimeter_inHg", None),
                      WEATHER_DATA.get("barometer_inHg", None),
                      WEATHER_DATA.get("cloudbase_foot", None),
                      WEATHER_DATA.get("daily_rain", None),
                      WEATHER_DATA.get("dayRain_in", None),
                      WEATHER_DATA.get("dewpoint_F", None),
                      WEATHER_DATA.get("heatindex_F", None),
                      WEATHER_DATA.get("hourRain_in", None),
                      WEATHER_DATA.get("humidex_F", None),
                      WEATHER_DATA.get("inTemp_F", None),
                      WEATHER_DATA.get("outHumidity", None),
                      WEATHER_DATA.get("outTemp_F", None),
                      WEATHER_DATA.get("pressure_inHg", None),
                      WEATHER_DATA.get("rain24_in", None),
                      WEATHER_DATA.get("rainRate_inch_per_hour", None),
                      WEATHER_DATA.get("rain_in", None),
                      WEATHER_DATA.get("rain_total", None),
                      WEATHER_DATA.get("windSpeed_mph", None),
                      WEATHER_DATA.get("wind_average", None),
                      WEATHER_DATA.get("windchill_F", None)))

        battery_sql_connection = sqlite3.connect("battery.db")
        for battery_name, battery in BATTERIES.items():
            with battery_sql_connection:
                battery_sql_connection.execute('''INSERT OR REPLACE INTO battery_data (
                    record_time,
                    name,
                    voltage,
                    current,
                    residual_capacity,
                    nominal_capacity,
                    cycles,
                    balance_status_cell_one,
                    balance_status_cell_two,
                    balance_status_cell_three,
                    balance_status_cell_four,
                    protection_status,
                    version,
                    capacity_percent,
                    control_status,
                    num_cells,
                    battery_temp_one,
                    battery_temp_two,
                    battery_temp_three,
                    cell_voltage_one,
                    cell_voltage_two,
                    cell_voltage_three,
                    cell_voltage_four
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (int(time.time()),
                      battery.get("name", None),
                      battery.get("voltage", None),
                      battery.get("current", None),
                      battery.get("residual_capacity", None),
                      battery.get("nominal_capacity", None),
                      battery.get("cycles", None),
                      1 if battery.get("balance_status", [False, False, False, False])[0] else 0,
                      1 if battery.get("balance_status", [False, False, False, False])[1] else 0,
                      1 if battery.get("balance_status", [False, False, False, False])[2] else 0,
                      1 if battery.get("balance_status", [False, False, False, False])[3] else 0,
                      ','.join(battery.get("protection_status", [])),
                      battery.get("version", None),
                      battery.get("capacity_percent", None),
                      battery.get("control_status", None),
                      battery.get("num_cells", None),
                      battery.get("battery_temps_f", [None, None, None])[0],
                      battery.get("battery_temps_f", [None, None, None])[1],
                      battery.get("battery_temps_f", [None, None, None])[2],
                      battery.get("cell_block_voltages", [None, None, None, None])[0],
                      battery.get("cell_block_voltages", [None, None, None, None])[1],
                      battery.get("cell_block_voltages", [None, None, None, None])[2],
                      battery.get("cell_block_voltages", [None, None, None, None])[3]
                      ))


#
# Update the running stats with the latest data by looping blu
#
def update_running_stats():
    global stats_data
    last_update = datetime.today()
    current_day_of_year = datetime.today().timetuple().tm_yday
    while True:
        try:
            if ('load_amps' in current_data) & ('battery_voltage' in current_data):
                stats_data['day_load_wh'] += 0.00139 * (
                        current_data.get('load_amps', 0) * current_data.get('battery_voltage', 0))
                # Now comes from the victron....
                # stats_data['day_solar_wh'] += 0.00139 * current_data.get('solar_watts', 0)
                stats_data['day_batt_wh'] += 0.00139 * current_data.get('battery_load', 0) * \
                                             current_data.get('battery_voltage', 0)
                stats_data['last_charge_state'] = current_data.get('charge_state', 'NIGHT')

            if datetime.today() > last_update + timedelta(minutes=1):
                update_sql_tables()
                last_update = datetime.today()

            if datetime.today().timetuple().tm_yday != current_day_of_year:
                current_day_of_year = datetime.today().timetuple().tm_yday
                stats_data['day_load_wh'] = 0
                stats_data['day_batt_wh'] = 0
                stats_data['day_solar_wh'] = 0

            time.sleep(5)
        except Exception as e:
            logger.error('Failure in updating stats: ' + str(e))


#
# Monitor the starlink for multiple potential problem situations.  First, make sure that the starlink is responding
# correctly.  If the starlink unit is not available, eventually we want to try a power cycle on it.  Also check to see
# if the unit has been stowed.  If it has been stowed for over 10 minutes, then we want to unstow it.
#
def manage_starlink():
    global AVAILABLE_SHELLEYS

    start_stow_time = 0
    start_not_connected_time = 0
    start_power_off_time = 0

    while True:
        try:
            if not dishy.is_connected():
                if start_not_connected_time == 0:
                    logger.info("Detected that dishy is not connected, starting countdown")
                    start_not_connected_time = time.time()
                elif time.time() - start_not_connected_time > 28800:
                    logger.warning("Dishy not connected for over 8 hours, trying a power cycle")
                    for shelly in AVAILABLE_SHELLEYS:
                        if shelly.name.casefold() == "dishy".casefold():
                            logger.warning(
                                "Found shelly dishy device, power cycling dishy due to disconnected state...")
                            status = shelly.get_relay_status(0)
                            if status["ison"] is False:
                                shelly.turn_relay_on(0)
                            else:
                                shelly.power_cycle_relay(0, 10)
                            start_not_connected_time = time.time()
            else:
                start_not_connected_time = 0

            for shelly in AVAILABLE_SHELLEYS:
                if shelly.name.casefold() == "dishy".casefold():
                    status = shelly.get_relay_status(0)
                    if status["ison"] is False:
                        if start_power_off_time == 0:
                            logger.info("Found dishy powered off, starting counter")
                            start_power_off_time = time.time()
                        elif time.time() - start_power_off_time > 600:
                            logger.warning("Dishy off for over 10 minutes, turning back on")
                            shelly.turn_relay_on(0)
                            start_power_off_time = 0
                    else:
                        start_power_off_time = 0

            if dishy.is_stowed():
                logger.info("Dishy is currently stowed")
                if start_stow_time == 0:
                    start_stow_time = time.time()
                elif time.time() - start_stow_time > 600:
                    logger.warning("Dishy stowed too long, unstowing dish")
                    dishy.dish_unstow()
            else:
                start_stow_time = 0
        except Exception as e:
            logger.error("Failure in starlink monitoring: " + str(e))
        time.sleep(60)


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
    global VALID_POWER_FIELDS

    days = int(request.args.get('days', 4))
    data_fields = request.args.getlist('dataField')
    graph_data = {'time': []}
    if data_fields and all( field in VALID_POWER_FIELDS for field in data_fields):
        for field in data_fields:
            graph_data[field] = []
        sql_connection = sqlite3.connect("powerdata.db")
        sql_connection.row_factory = sqlite3.Row
        with sql_connection:
            sql_statement = "SELECT record_time"
            for field in data_fields:
                sql_statement += ", " + field
            sql_statement += " FROM power_data WHERE record_time >= ? ORDER BY record_time ASC"
            cursor = sql_connection.execute(sql_statement,
                                        [int(time.mktime((datetime.today() - timedelta(days=days)).timetuple()))])
            for row in cursor.fetchall():
                rowdict = dict(row)
                graph_data['time'].append(datetime.fromtimestamp(rowdict.get('record_time')))
                for field in data_fields:
                    graph_data[field].append(rowdict.get(field, 0))

    return graph_data


@app.route("/currentData")
def get_current_data():
    global current_data

    return current_data


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
    graph_data = {'time': []}
    if data_fields and all( field in VALID_BATTERY_FIELDS for field in data_fields):
        for field in data_fields:
            graph_data[field] = []
        sql_connection = sqlite3.connect("battery.db")
        sql_connection.row_factory = sqlite3.Row
        with sql_connection:
            sql_statement = "SELECT record_time"
            for field in data_fields:
                sql_statement += ", " + field
            sql_statement += " FROM battery_data WHERE record_time >= ?"
            if battery_name:
                sql_statement += " AND name == ?"
            sql_statement += " ORDER BY record_time ASC"
            parameters = [int(time.mktime((datetime.today() - timedelta(days=days)).timetuple()))]
            if battery_name:
                parameters.append(battery_name)
            cursor = sql_connection.execute(sql_statement, parameters)
            for row in cursor.fetchall():
                rowdict = dict(row)
                graph_data['time'].append(datetime.fromtimestamp(rowdict.get('record_time')))
                for field in data_fields:
                    graph_data[field].append(rowdict.get(field, 0))

    return graph_data

@app.route("/weatherData")
def get_weather_data():
    global WEATHER_DATA

    return WEATHER_DATA


@app.route("/weatherDailyMinMax")
def get_weather_max_min():
    wx_sql_connection = sqlite3.connect("wxdata.db")
    wx_sql_connection.row_factory = sqlite3.Row
    with wx_sql_connection:
        cursor = wx_sql_connection.execute('''
            SELECT min(dewpoint_F) AS dewpoint_F_min, max(dewpoint_F) AS dewpoint_F_max,
            min(heatindex_F) AS heatindex_F_min, max(heatindex_F) AS heatindex_F_max,
            min(inTemp_F) AS inTemp_F_min, max(inTemp_F) AS inTemp_F_max,
            min(outHumidity) AS outHumidity_min, max(outHumidity) AS outHumidity_max,
            min(outTemp_F) AS outTemp_F_min, max(outTemp_F) AS outTemp_F_max,
            min(pressure_inHg) AS pressure_inHg_min, max(pressure_inHg) AS pressure_inHg_max,
            min(rainRate_inch_per_hour) AS rainRate_inch_per_hour_min, max(rainRate_inch_per_hour) AS rainRate_inder_per_hour_max,
            min(windSpeed_mph) AS windSpeed_mph_min, max(windSpeed_mph) AS windSpeed_mph_max,
            min(wind_average) AS wind_average_min, max(wind_average) AS wind_average_max,
            min(windchill_F) AS windchill_F_min, max(windchill_F) AS windchill_F_max
            FROM wx_data WHERE record_time >= ? 
            ''',
                        [int(time.mktime(
                            (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))
                        ])
        min_max_data = cursor.fetchone()
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
    global VALID_WX_FIELDS

    days = int(request.args.get('days', 1))
    data_fields = request.args.getlist('dataField')
    graph_data = {'time': []}
    if data_fields and all(field in VALID_WX_FIELDS for field in data_fields):
        for field in data_fields:
            graph_data[field] = []
        sql_connection = sqlite3.connect("wxdata.db")
        sql_connection.row_factory = sqlite3.Row
        with sql_connection:
            sql_statement = "SELECT record_time"
            for field in data_fields:
                sql_statement += ", " + field
            sql_statement += " FROM wx_data WHERE record_time >= ? ORDER BY record_time ASC"
            cursor = sql_connection.execute(sql_statement,
                                            [int(time.mktime((datetime.today() - timedelta(days=days)).timetuple()))])
            for row in cursor.fetchall():
                rowdict = dict(row)
                graph_data['time'].append(datetime.fromtimestamp(rowdict.get('record_time')))
                for field in data_fields:
                    graph_data[field].append(rowdict.get(field, 0))

    return graph_data


@app.route("/blueIrisAlert")
def get_blueiris_alert():
    global BLUEIRIS_ALERT

    no_image = request.args.get('noImage', 'False').lower() == 'true'

    return_value = BLUEIRIS_ALERT.copy()

    if no_image:
        return_value.pop('alertImage', None)

    return return_value


#
# Return both the last lightning event seen, as well as summary data for the day
#
@app.route("/lightningData")
def get_lightning_data():
    global LIGHTNING_DATA
    response = {}
    sql_connection = sqlite3.connect("lightning.db")
    sql_connection.row_factory = sqlite3.Row
    with sql_connection:
        cursor = sql_connection.execute('''
            SELECT COUNT(CASE when event='lightning' THEN 1 END) as total_strikes,
            COUNT(CASE when event='disturber' THEN 1 END) as total_disturbers,
            COUNT(CASE when event='noise' THEN 1 END) as total_noise,
            MIN(distance) as closest_strike,
            MAX(intensity) as strongest_strike
            FROM lightning_data
            WHERE record_time >= ?
        ''', [int(time.mktime((datetime.today() - timedelta(days=1)).timetuple()))])
        row = cursor.fetchone()
        if row is None:
            response.update({"summary": {}})
        else:
            response.update({"summary": dict(row)})

        response.update({"events": []})
        cursor = sql_connection.execute('''
            SELECT * FROM lightning_data WHERE record_time >= ? ORDER BY record_time ASC
        ''', [int(time.mktime((datetime.today() - timedelta(days=1)).timetuple()))])
        for row in cursor.fetchall():
            response.get("events", []).append(dict(row))

        cursor = sql_connection.execute('''
            SELECT * FROM lightning_data WHERE event='lightning' AND record_time >= ? ORDER BY record_time DESC LIMIT 1
            ''', [int(time.mktime((datetime.today() - timedelta(days=1)).timetuple()))])
        row = cursor.fetchone()
        if row is None:
            response.update({"last_strike_24hr": {}})
        else:
            response.update({"last_strike_24hr": dict(row)})

        cursor = sql_connection.execute('''
            SELECT * FROM lightning_data ORDER BY record_time DESC LIMIT 1
            ''')
        row = cursor.fetchone()
        if row is None:
            response.update({"last_event": {}})
        else:
            response.update({"last_event": dict(row)})
    return response


@app.route("/statsData")
def get_stats_data():
    global stats_data
    sql_connection = sqlite3.connect("powerdata.db")
    sql_connection.row_factory = sqlite3.Row
    with sql_connection:
        cursor = sql_connection.execute('''SELECT avg(day_batt_wh) AS avg_net, avg(day_load_wh) AS avg_load, 
        avg(day_solar_wh) AS avg_solar, sum(day_load_wh) AS total_load_wh, sum(day_solar_wh) AS total_solar_wh 
        FROM daily_power_data
        ''')
        summary_data = cursor.fetchone()
        stats_data['avg_net'] = summary_data['avg_net']
        stats_data['avg_load'] = summary_data['avg_load']
        stats_data['avg_solar'] = summary_data['avg_solar']
        stats_data['total_load_wh'] = summary_data['total_load_wh']
        stats_data['total_solar_wh'] = summary_data['total_solar_wh']

        cursor = sql_connection.execute(
            '''
            SELECT day_batt_wh AS yesterday_batt_wh, day_load_wh AS yesterday_load_wh, 
                day_solar_wh - day_load_wh as yesterday_net_wh FROM daily_power_data WHERE record_date = ?
            ''',
            [int(time.mktime(
                (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).timetuple()))
            ])
        yesterdays_data = cursor.fetchone()
        if yesterdays_data is not None:
            stats_data['yesterday_batt_wh'] = yesterdays_data['yesterday_batt_wh']
            stats_data['yesterday_load_wh'] = yesterdays_data['yesterday_load_wh']
            stats_data['yesterday_net_wh'] = yesterdays_data['yesterday_net_wh']

        cursor = sql_connection.execute('''
            SELECT sum(day_solar_wh - day_load_wh) AS five_day_net FROM daily_power_data WHERE record_date >= ?
            ''',
                                        [int(time.mktime(
                                            (datetime.today().replace(hour=0, minute=0, second=0,
                                                                      microsecond=0) - timedelta(days=5)).timetuple()))
                                        ])
        net_data = cursor.fetchone()
        if net_data is not None:
            stats_data['five_day_net'] = net_data['five_day_net']

        cursor = sql_connection.execute('''
            SELECT sum(day_solar_wh - day_load_wh) AS ten_day_net FROM daily_power_data WHERE record_date >= ?
            ''',
                                        [int(time.mktime(
                                            (datetime.today().replace(hour=0, minute=0, second=0,
                                                                      microsecond=0) - timedelta(days=10)).timetuple()))
                                        ])
        net_data = cursor.fetchone()
        if net_data is not None:
            stats_data['ten_day_net'] = net_data['ten_day_net']

        cursor = sql_connection.execute('''
            SELECT avg(load_watts) AS five_min_load_watts, avg(battery_watts) AS five_min_battery_watts, 
            avg(solar_watts) AS five_min_solar_watts, avg(battery_voltage) AS five_min_battery_voltage 
            FROM power_data WHERE record_time >= ? 
            ''',
                                        [int(time.mktime(
                                            (datetime.today() -
                                             timedelta(minutes=5)).timetuple()))
                                        ])
        net_data = cursor.fetchone()
        if net_data is not None:
            stats_data['five_min_load_watts'] = net_data['five_min_load_watts']
            stats_data['five_min_battery_watts'] = net_data['five_min_battery_watts']
            stats_data['five_min_solar_watts'] = net_data['five_min_solar_watts']
            stats_data['five_min_battery_voltage'] = net_data['five_min_battery_voltage']

    battery_sql_connection = sqlite3.connect("battery.db")
    battery_sql_connection.row_factory = sqlite3.Row
    with battery_sql_connection:
        cursor = battery_sql_connection.execute(
            '''
            SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                    WHERE record_time >= ? GROUP BY name)
            ''',
            [int(time.mktime(
                (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))
            ])
        row = cursor.fetchone()
        if row is not None:
            stats_data['battery_min_percent'] = row['battery_min_percent']
            stats_data['battery_max_percent'] = row['battery_max_percent']
        cursor = battery_sql_connection.execute(
            '''
            SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                    WHERE record_time <= ? AND record_time >= ? GROUP BY name)
            ''',
            (int(time.mktime(
                (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).timetuple())),
                int(time.mktime(
                    (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).timetuple()))
            ))
        row = cursor.fetchone()
        if row is not None:
            stats_data['battery_min_percent_one_day_ago'] = row['battery_min_percent']
            stats_data['battery_max_percent_one_day_ago'] = row['battery_max_percent']
        cursor = battery_sql_connection.execute(
            '''
            SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                    WHERE record_time <= ? AND record_time >= ? GROUP BY name)
            ''',
            (int(time.mktime(
                (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).timetuple())),
             int(time.mktime(
                 (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)).timetuple()))
            ))
        row = cursor.fetchone()
        if row is not None:
            stats_data['battery_min_percent_two_days_ago'] = row['battery_min_percent']
            stats_data['battery_max_percent_two_days_ago'] = row['battery_max_percent']
        cursor = battery_sql_connection.execute(
            '''
            SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                    WHERE record_time <= ? AND record_time >= ? GROUP BY name)
            ''',
            (int(time.mktime(
                (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)).timetuple())),
             int(time.mktime(
                 (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)).timetuple()))
            ))
        row = cursor.fetchone()
        if row is not None:
            stats_data['battery_min_percent_three_days_ago'] = row['battery_min_percent']
            stats_data['battery_max_percent_three_days_ago'] = row['battery_max_percent']


    return stats_data


#
# provide the generic dishy status data through REST
#
@app.route("/starlink/status")
def starlink_status():
    status = dishy.get_status()

    return json.dumps(status, indent=3)


#
# provide the dishy historical data through REST
#
@app.route("/starlink/history")
def starlink_history():
    skip_graphs = request.args.get('skipGraphs', "False").lower() == 'true'
    history = dishy.get_history()
    if skip_graphs:
        history.pop('ping_drop_rate')
        history.pop('ping_latency')
        history.pop('downlink_bps')
        history.pop('uplink_bps')
    return json.dumps(history, indent=3)


#
# Get the obstruction image data, and transform into a png file and return through the get request
#
@app.route("/starlink/obstruction_image")
def starlink_obstruction_image():
    obstruction_image = dishy.get_obstruction_map()
    numpy_image = np.array(obstruction_image).astype('uint8')
    img = Image.fromarray(numpy_image)
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)
    return send_file(file_object, mimetype='image/PNG')


#
# Issue a request to the disk to stow itself
#
@app.route("/starlink/stow", methods=['POST'])
def stow_dish():
    dishy.dish_stow()


#
# Issue a request to the dish to unstow itself
#
@app.route("/starlink/unstow", methods=['POST'])
def unstow_dish():
    dishy.dish_unstow()


#
# Issue a request for the dish to reboot itself
#
@app.route("/starlink/reboot", methods=['POST'])
def reboot_dish():
    dishy.dish_reboot()


#
# Get the shelly object instance matching the name.  Return none if no matching Shelly
#
def get_shelly_by_name(name):
    global AVAILABLE_SHELLEYS

    for shelly in AVAILABLE_SHELLEYS:
        if shelly.get_settings().get("name", None) == name:
            return shelly
    return None


#
# Get the list of available shellys
#
@app.route("/shelly")
def get_all_shellys():
    global AVAILABLE_SHELLEYS

    return json.dumps([shelly.__dict__ for shelly in AVAILABLE_SHELLEYS])


#
# Get the current relay status of a given device
#
@app.route("/shelly/relay/status", methods=['GET'])
def relay_status():
    relay_number = request.args.get("relay", default=0, type=int)
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        return shelly.get_relay_status(relay_number)
    return {}


#
# turn the relay off of a given device
#
@app.route("/shelly/relay/off", methods=['GET'])
def turn_relay_off():
    relay_number = request.args.get("relay", default=0, type=int)
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        return shelly.turn_relay_off(relay_number)
    return {}


#
# turn the relay on of a given device
#
@app.route("/shelly/relay/on", methods=['GET'])
def turn_relay_on():
    relay_number = request.args.get("relay", default=0, type=int)
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        return shelly.turn_relay_on(relay_number)
    return {}


#
# power cycle the relay of a given device
#
@app.route("/shelly/relay/cycle", methods=['GET'])
def power_cycle_relay():
    relay_number = request.args.get("relay", default=0, type=int)
    delay = request.args.get("delay", default=5, type=int)
    shelly_name = request.args.get("name", default="", type=str)
    shelly = get_shelly_by_name(shelly_name)
    if shelly is not None:
        return shelly.power_cycle_relay(relay=relay_number, delay=delay)

    return {}


#
# Update the day accumulated data from the daily table for today.  If none is present for today, just skip updating
#
def refresh_daily_data():
    sql_connection = sqlite3.connect("powerdata.db")
    sql_connection.row_factory = sqlite3.Row
    with sql_connection:
        cursor = sql_connection.execute("SELECT * FROM daily_power_data WHERE record_date = ?",

                                        [int(time.mktime(datetime.today().replace(hour=0, minute=0, second=0,
                                                                                  microsecond=0).timetuple()))])
        row = cursor.fetchone()
        if row is not None:
            rowdict = dict(row)
            stats_data['day_load_wh'] = rowdict['day_load_wh']
            stats_data['day_solar_wh'] = rowdict['day_solar_wh']
            stats_data['day_batt_wh'] = rowdict['day_batt_wh']
            stats_data['last_charge_state'] = rowdict['last_charge_state']


#
# update lightning information in the in memory object and in the sql database
#
def update_lightning_data(lightning_event: dict):
    global LIGHTNING_DATA

    LIGHTNING_DATA = lightning_event
    sql_connection = sqlite3.connect("lightning.db")
    with sql_connection:
        try:
            result = sql_connection.execute('''INSERT OR REPLACE INTO lightning_data (
                record_time, 
                event, 
                distance,
                intensity
                ) VALUES (?, ?, ?, ?)
            ''',
                               (int(time.time()),
                                lightning_event.get("event", "unknown"),
                                lightning_event.get("distance", None),
                                lightning_event.get("intensity", None)
                                ))
        except Exception as e:
            logger.error(e)


#
# Connect to the mqtt service and subscribe to the blue iris and weewx weather topics.
#
def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        logger.info("MQTT Client Connected, subscribing...")
        c.subscribe("weather/loop")
        c.subscribe("blueiris")
        c.subscribe("battery_status")
        c.subscribe("load_data")
        c.subscribe("lightning_data")
        c.subscribe("solar_charger_data")

    def on_message(c, userdata, msg):
        global WEATHER_DATA, BLUEIRIS_ALERT, BATTERIES

        logger.debug(f"Recieved MQTT: {msg.topic}->{msg.payload}")
        if msg.topic == "weather/loop":
            WEATHER_DATA = json.loads(msg.payload)
        elif msg.topic == "blueiris":
            BLUEIRIS_ALERT = json.loads(msg.payload)
            BLUEIRIS_ALERT['time'] = int(time.time() * 1000)
            BLUEIRIS_ALERT['id'] = str(uuid.uuid4())
            file = open(b"last_blue_iris_alert.pkl", "wb")
            pickle.dump(BLUEIRIS_ALERT, file)
            file.close()
        elif msg.topic == "battery_status":
            logger.debug("Received Battery Status")
            battery_info = json.loads(msg.payload)
            BATTERIES[battery_info["name"]] = battery_info
            total_percent = 0
            for battery_name, battery in BATTERIES.items():
                total_percent += battery.get("capacity_percent", 0)
            current_data["battery_percent"] = total_percent / len(BATTERIES.items())
        elif msg.topic == "load_data":
            logger.debug("Received load data")
            load_info = json.loads(msg.payload)
            current_data["battery_load"] = load_info["battery_load"]
            current_data["load_amps"] = load_info["load_amps"]
        elif msg.topic == "lightning_data":
            logger.debug("Received lightning data")
            update_lightning_data(json.loads(msg.payload))
        elif msg.topic == "solar_charger_data":
            charger_data = json.loads(msg.payload)
            current_data["solar_watts"] = charger_data.get("solar_watts", 0)
            current_data["battery_charge_current"] = charger_data.get("battery_charge_current", 0)
            current_data["charge_state"] = charger_data.get("charge_state", "OTHER")
            current_data["battery_voltage"] = charger_data.get("battery_voltage", 0)
            # We need to protect against the charge controller resetting this running stat before we increment the day,
            # so only capture it if it went up as it should never decrement.  We reset this elsewhere to zero when we
            # recognize a day has passed
            if stats_data['day_solar_wh'] < charger_data.get("day_solar_wh", 0):
                stats_data['day_solar_wh'] = charger_data.get("day_solar_wh", 0)

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


def main(proxy=None):
    global BLUEIRIS_ALERT, AVAILABLE_SHELLEYS, SHELLY_DEVICE_ADDRESSES

    sql_connection = sqlite3.connect("powerdata.db")
    sql_connection.execute('''CREATE TABLE IF NOT EXISTS power_data (record_time INTEGER PRIMARY KEY,
                battery_load REAL,
                load_amps REAL,
                load_watts REAL,
                battery_voltage REAL,
                battery_watts REAL,
                net_production REAL,
                battery_sense_voltage REAL,
                battery_voltage_slow REAL,
                battery_daily_minimum_voltage REAL,
                battery_daily_maximum_voltage REAL,
                target_regulation_voltage REAL,
                array_voltage REAL,
                array_charge_current REAL,
                battery_charge_current REAL,
                battery_charge_current_slow REAL,
                input_power REAL,
                solar_watts REAL,
                heatsink_temperature REAL,
                battery_temperature REAL,
                charge_state TEXT,
                seconds_in_absorption_daily INTEGER,
                seconds_in_float_daily INTEGER,
                seconds_in_equalization_daily INTEGER)
                ''')
    sql_connection.execute('''CREATE TABLE IF NOT EXISTS daily_power_data (record_date INTEGER PRIMARY KEY,
                day_load_wh REAL,
                day_solar_wh REAL,
                day_batt_wh REAL,
                last_charge_state TEXT
                )
                ''')
    wx_sql_connection = sqlite3.connect("wxdata.db")
    wx_sql_connection.execute('''CREATE TABLE IF NOT EXISTS wx_data (record_time INTEGER PRIMARY KEY,
                altimeter_inHg REAL,
                barometer_inHg REAL,
                cloudbase_foot REAL,
                daily_rain REAL,
                dayRain_in REAL,
                dewpoint_F REAL,
                heatindex_F REAL,
                hourRain_in REAL,
                humidex_F REAL,
                inTemp_F REAL,
                outHumidity REAL,
                outTemp_F REAL,
                pressure_inHg REAL,
                rain24_in REAL,
                rainRate_inch_per_hour REAL,
                rain_in REAL,
                rain_total REAL,
                windSpeed_mph REAL,
                wind_average REAL,
                windchill_F REAL
                )
                ''')

    battery_sql_connection = sqlite3.connect("battery.db")
    battery_sql_connection.execute('''CREATE TABLE IF NOT EXISTS battery_data(record_time INTEGER,
                name TEXT,
                voltage REAL,
                current REAL,
                residual_capacity REAL,
                nominal_capacity READ,
                cycles INTEGER,
                balance_status_cell_one INTEGER,
                balance_status_cell_two INTEGER,
                balance_status_cell_three INTEGER,
                balance_status_cell_four INTEGER,
                protection_status TEXT,
                version TEXT,
                capacity_percent INTEGER,
                control_status TEXT,
                num_cells INTEGER,
                battery_temp_one REAL,
                battery_temp_two REAL,
                battery_temp_three REAL,
                cell_voltage_one REAL,
                cell_voltage_two REAL,
                cell_voltage_three REAL,
                cell_voltage_four REAL,
                PRIMARY KEY (record_time, name)
                )
    ''')

    lightning_sql_connection = sqlite3.connect("lightning.db")
    lightning_sql_connection.execute('''CREATE TABLE IF NOT EXISTS lightning_data(record_time INTEGER,
                event TEXT,
                distance INTEGER,
                intensity REAL,
                PRIMARY KEY (record_time))
    ''')

    try:
        if os.path.exists("last_blue_iris_alert.pkl"):
            BLUEIRIS_ALERT = pickle.load(open("last_blue_iris_alert.pkl", "rb"))
    except Exception as e:
        print("Failed to load last blue iris alert: " + str(e))

    refresh_daily_data()

    starlink_thread = threading.Thread(target=manage_starlink, args=())
    starlink_thread.daemon = True
    starlink_thread.start()

    for shelley_addr in SHELLY_DEVICE_ADDRESSES:
        retry_count = 0
        while True:
            try:
                AVAILABLE_SHELLEYS.append(Shelly(shelley_addr))
                logger.info("Shelly device" +  shelley_addr + " successfully added")
                break
            except Exception as e:
                retry_count += 1
                logger.error("Failed to add shelly device" + shelley_addr + ": " + str(e))
                if retry_count > 5:
                    break
                time.sleep(15)

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
