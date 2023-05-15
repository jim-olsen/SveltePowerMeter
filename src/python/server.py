import os
import pickle

from flask import Flask, send_from_directory, send_file, request
import time
import threading
from datetime import datetime, timedelta
import asyncio
from pymodbus.client import ModbusTcpClient
from asyncio.exceptions import CancelledError, TimeoutError
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakDeviceNotFoundError, BleakDBusError
from PIL import Image
from Starlink import Starlink
from Shelly import Shelly
import io
import json
import numpy as np
import sqlite3
import logging
import paho.mqtt.client as mqtt
import requests
import uuid

logging.basicConfig()
logging.getLogger('power_meter').setLevel(logging.INFO)
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
    'avg_solar': 0.0,
}
weather_data = {}
blueiris_alert = {}

UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # Nordic NUS characteristic for TX
UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # Nordic NUS characteristic for RX
# List of valid fields for querying for weather graph data.  This protects against sql injection using a dynamic field
# based request
VALID_WX_FIELDS = ["altimeter_inHg", "appTemp_F", "barometer_inHg", "cloudbase_foot", "daily_rain", "dateTime",
                   "dayRain_in", "day_of_year", "dewpoint_F", "heatindex_F", "hourRain_in", "humidex_F", "inTemp_F",
                   "minute_of_day", "outHumidity", "outTemp_F", "pressure_inHg", "rain24_in", "rainRate_inch_per_hour",
                   "rain_in", "rain_total", "usUnits", "windDir", "windSpeed_mph", "wind_average", "windchill_F"]
# List of valid fields for queryiing power graph data.  This protected against sql injection using a dynamic field
# based request
VALID_POWER_FIELDS = ["battery_load", "load_amps", "load_watts", "battery_voltage", "battery_watts", "net_production",
                      "battery_sense_voltage", "battery_voltage_slow", "battery_daily_minimum_voltage",
                      "battery_daily_maximum_voltage", "target_regulation_voltage", "array_voltage",
                      "array_charge_current", "battery_charge_current", "battery_charge_current_slow", "input_power",
                      "solar_watts", "heatsink_temperature", "battery_temperature", "charge_state",
                      "seconds_in_absorption_daily", "seconds_in_float_daily", "seconds_in_equalization_daily"]

# Set this value to the ip of your tristar charge controller
TRISTAR_ADDR = '10.0.10.10'
# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
# For now I have shelly devices manually listed.  There is not a great discovery mechanism built in but am exploring
# options
SHELLY_DEVICE_ADDRESSES = ['http://10.0.10.40', 'http://10.0.10.41']

available_shellys = []

app = Flask(__name__)
dishy = Starlink()


#
# Connect to the BLE device and get the voltage from A0, and the loads from A1 and A2 pins.  See the circuit python
# code for how this is implemented
#
async def update_ble_values(ble_address, loop):
    data_received = asyncio.Event()

    def notification_handler(sender, data):
        """Simple notification handler which prints the data received."""
        logger.debug("{0}: {1}".format(sender, data))
        sensor_values = data.decode("utf-8").split(':')
        current_data["battery_voltage"] = float(sensor_values[0])
        current_data["battery_load"] = float(sensor_values[1])
        current_data["load_amps"] = float(sensor_values[2].replace("*", ""))
        logger.debug(f"Voltage:{current_data['battery_voltage']}, Batt Load: {current_data['battery_load']}, "
                     f"Load: {current_data['load_amps']}")
        data_received.set()

    while True:
        try:
            logger.info(f"Trying to connect to sensor at {str(ble_address)}")
            async with BleakClient(ble_address, loop=loop) as client:

                # wait for BLE client to be connected
                while not client.is_connected():
                    await asyncio.sleep(1)
                logger.info("Connected to BLE Sensor")

                data_received.clear()
                # wait for data to be sent from client
                await client.start_notify(UART_RX_UUID, notification_handler)

                while client.is_connected():
                    await asyncio.wait_for(data_received.wait(), 20)
                    data_received.clear()

                logger.info("Client has disconnected from BLE Sensor")
                client.stop_notify()
        except (OSError, CancelledError, TimeoutError, BleakDeviceNotFoundError, BleakDBusError):
            logger.error("Client is disconnected by OS")
            pass

        logger.info("Disconnected, retrying connection....")


def update_sql_tables():
    global current_data
    global weather_data
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
                      weather_data.get("altimeter_inHg", None),
                      weather_data.get("barometer_inHg", None),
                      weather_data.get("cloudbase_foot", None),
                      weather_data.get("daily_rain", None),
                      weather_data.get("dayRain_in", None),
                      weather_data.get("dewpoint_F", None),
                      weather_data.get("heatindex_F", None),
                      weather_data.get("hourRain_in", None),
                      weather_data.get("humidex_F", None),
                      weather_data.get("inTemp_F", None),
                      weather_data.get("outHumidity", None),
                      weather_data.get("outTemp_F", None),
                      weather_data.get("pressure_inHg", None),
                      weather_data.get("rain24_in", None),
                      weather_data.get("rainRate_inch_per_hour", None),
                      weather_data.get("rain_in", None),
                      weather_data.get("rain_total", None),
                      weather_data.get("windSpeed_mph", None),
                      weather_data.get("wind_average", None),
                      weather_data.get("windchill_F", None)))


#
# Update the running stats with the latest data
#
def update_running_stats():
    global stats_data
    last_update = datetime.today()
    while True:
        try:
            if ('load_amps' in current_data) & ('battery_voltage' in current_data):
                stats_data['day_load_wh'] += 0.00139 * (
                        current_data.get('load_amps', 0) * current_data.get('battery_voltage', 0))
                stats_data['day_solar_wh'] += 0.00139 * current_data.get('solar_watts', 0)
                stats_data['day_batt_wh'] += 0.00139 * current_data.get('battery_load', 0) * \
                                             current_data.get('battery_voltage', 0)
                stats_data['last_charge_state'] = current_data.get('charge_state', 'NIGHT')

            if datetime.today() > last_update + timedelta(minutes=1):
                update_sql_tables()
                last_update = datetime.today()

            time.sleep(5)
        except Exception as e:
            logger.error('Failure in updating stats: ' + str(e))


#
# Update the values from the tristar modbus protocol in the values dictionary
#
def update_tristar_values():
    while True:
        # Connect directly to the modbus interface on the tristar charge controller to get the current information about
        # the state of the solar array and battery charging
        modbus_client = ModbusTcpClient(TRISTAR_ADDR, port=502)
        try:
            modbus_client.connect()
            rr = modbus_client.read_holding_registers(0, 91, unit=1)
            if rr is None:
                modbus_client.close()
                logger.error("Failed to connect and read from tristar modbus")
            else:
                voltage_scaling_factor = (float(rr.registers[0]) + (float(rr.registers[1]) / 100))
                amperage_scaling_factor = (float(rr.registers[2]) + (float(rr.registers[3]) / 100))

                # Voltage Related Statistics
                # current_data["battery_voltage"] = float(rr.registers[24]) * voltage_scaling_factor * 2 ** (-15)
                current_data["battery_sense_voltage"] = float(rr.registers[26]) * voltage_scaling_factor * 2 ** (-15)
                current_data["battery_voltage_slow"] = float(rr.registers[38]) * voltage_scaling_factor * 2 ** (-15)
                current_data["battery_daily_minimum_voltage"] = float(
                    rr.registers[64]) * voltage_scaling_factor * 2 ** (-15)
                current_data["battery_daily_maximum_voltage"] = float(
                    rr.registers[65]) * voltage_scaling_factor * 2 ** (-15)
                current_data["target_regulation_voltage"] = float(rr.registers[51]) * voltage_scaling_factor * 2 ** (
                    -15)
                current_data["array_voltage"] = float(rr.registers[27]) * voltage_scaling_factor * 2 ** (-15)
                # Current Related Statistics
                current_data["array_charge_current"] = float(rr.registers[29]) * amperage_scaling_factor * 2 ** (-15)
                current_data["battery_charge_current"] = float(rr.registers[28]) * amperage_scaling_factor * 2 ** (-15)
                current_data["battery_charge_current_slow"] = float(rr.registers[39]) * amperage_scaling_factor * 2 ** (
                    -15)
                # Wattage Related Statistics
                current_data["input_power"] = float(
                    rr.registers[59]) * voltage_scaling_factor * amperage_scaling_factor * 2 ** (-17)
                current_data["solar_watts"] = float(
                    rr.registers[58]) * voltage_scaling_factor * amperage_scaling_factor * 2 ** (-17)
                # Temperature Statistics
                current_data["heatsink_temperature"] = rr.registers[35]
                current_data["battery_temperature"] = rr.registers[36]
                # Misc Statistics
                charge_states = ["START", "NIGHT_CHECK", "DISCONNECT", "NIGHT", "FAULT", "MPPT", "ABSORB", "FLOAT",
                                 "EQUALIZE", "SLAVE"]
                current_data["charge_state"] = charge_states[rr.registers[50]]
                current_data["seconds_in_absorption_daily"] = rr.registers[77]
                current_data["seconds_in_float_daily"] = rr.registers[79]
                current_data["seconds_in_equalization_daily"] = rr.registers[78]
                modbus_client.close()
        except Exception as e:
            logger.error("Failed to connect to tristar modbus", e)
            modbus_client.close()
        time.sleep(5)


#
# For development purposes, allow collection of the live power data from an existing instance rather than going live
# to the bluetooth device.  This allows development to be done from a remote location.
#
def update_through_proxy(proxy):
    global current_data

    while True:
        try:
            r = requests.get(proxy + '/currentData')
            if r.status_code == 200:
                current_data = r.json()
        except Exception as e:
            logger.error(f"Failed to contact proxy: {e}")
        time.sleep(5)


#
# Monitor the starlink for multiple potential problem situations.  First, make sure that the starlink is responding
# correctly.  If the starlink unit is not available, eventually we want to try a power cycle on it.  Also check to see
# if the unit has been stowed.  If it has been stowed for over 10 minutes, then we want to unstow it.
#
def manage_starlink():
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
                    for shelly in available_shellys:
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

            for shelly in available_shellys:
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


@app.route("/weatherData")
def get_weather_data():
    global weather_data

    return weather_data


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
    global blueiris_alert

    no_image = request.args.get('noImage', 'False').lower() == 'true'

    return_value = blueiris_alert.copy()

    if no_image:
        return_value.pop('alertImage', None)

    return return_value


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
    for shelly in available_shellys:
        if shelly.get_settings().get("name", None) == name:
            return shelly
    return None


#
# Get the list of available shellys
#
@app.route("/shelly")
def get_all_shellys():
    return json.dumps([shelly.__dict__ for shelly in available_shellys])


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


def run_ble_thread(address, loop):
    loop.run_until_complete(update_ble_values(address, loop))


#
# Look through all available bluetooth devices and fine one with the name CabinSensor and get its address
#
# RETURNS:
#  Either None if no sensor was found, or the address of the bluetooth device representing the sensor
#
async def async_find_cabin_sensor():
    logger.info("Finding cabin sensor")
    devices = await BleakScanner.discover(timeout=10, return_adv=False)
    for d in devices:
        logger.info(f"{d.name} {d.address} {d.metadata} {d.rssi}")
        if d.name == 'CabinSensor':
            return d.address
    return None


#
# The synchronous version for async_find_cabin_sensor()
#
# RETURNS:
#  Either None if no sensor was found, or the address of the bluetooth device representing the sensor
#
def find_cabin_sensor():
    return asyncio.run(async_find_cabin_sensor())


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
# Connect to the mqtt service and subscribe to the blue iris and weewx weather topics.
#
def start_mqtt_client():
    def on_connect(client, userdata, flags, rc):
        logger.info("MQTT Client Connected, subscribing...")
        client.subscribe("weather/loop")
        client.subscribe("blueiris")

    def on_message(client, userdata, msg):
        global weather_data, blueiris_alert

        logger.debug(f"Recieved MQTT: {msg.topic}->{msg.payload}")
        if msg.topic == "weather/loop":
            weather_data = json.loads(msg.payload)
        elif msg.topic == "blueiris":
            blueiris_alert = json.loads(msg.payload)
            blueiris_alert['time'] = int(time.time() * 1000)
            blueiris_alert['id'] = str(uuid.uuid4())
            file = open(b"last_blue_iris_alert.pkl", "wb")
            pickle.dump(blueiris_alert, file)
            file.close()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()


def main(proxy=None):
    global blueiris_alert

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

    try:
        if os.path.exists("last_blue_iris_alert.pkl"):
            blueiris_alert = pickle.load(open("last_blue_iris_alert.pkl", "rb"))
    except Exception as e:
        print("Failed to load last blue iris alert: " + str(e))

    refresh_daily_data()

    starlink_thread = threading.Thread(target=manage_starlink, args=())
    starlink_thread.daemon = True
    starlink_thread.start()

    if proxy is None:
        tristar_thread = threading.Thread(target=update_tristar_values, args=())
        tristar_thread.daemon = True
        tristar_thread.start()

        loop = asyncio.get_event_loop()
        retry_count = 0
        while True:
            ble_address = loop.run_until_complete(async_find_cabin_sensor())
            retry_count += 1
            if ble_address is not None or retry_count > 5:
                break
        if ble_address is not None:
            ble_thread = threading.Thread(target=run_ble_thread, args=(ble_address, loop))
            ble_thread.daemon = True
            ble_thread.start()

        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
    else:
        proxy_thread = threading.Thread(target=update_through_proxy, args=(proxy,))
        proxy_thread.daemon = True
        proxy_thread.start()

    for shelley_addr in SHELLY_DEVICE_ADDRESSES:
        retry_count = 0
        while True:
            try:
                available_shellys.append(Shelly(shelley_addr))
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
    # main(proxy="http://10.0.10.32:8050")
    main()
