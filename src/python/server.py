from flask import Flask, send_from_directory, send_file, request
import time
import threading
import os
import requests
import pickle
from datetime import datetime
import shutil
from pymodbus.client.sync import ModbusTcpClient
from os import path
from PIL import Image
from Starlink import Starlink
from Shelly import Shelly
import io
import json
import numpy as np
import logging

graph_data = {
    'battload': [],
    'time': [],
    'battvoltage': [],
    'battwatts': [],
    'solarwatts': [],
    'targetbattvoltage': [],
    'net_production': [],
    'load_watts': []
}
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
    'thirty_days_net': [0] * 30,
    'thirty_days_load': [0] * 30,
    'thirty_days_solar': [0] * 30,
    'thirty_days_batt_wh': [0] * 30
}
# Set this value to the ip of your tristar charge controller
tristar_addr = '10.0.10.10'
# Set this value to the base url of your arduino running the acs758 monitoring
arduino_addr = 'http://10.0.10.31/sensor/'

available_shellys = []

app = Flask(__name__)
dishy = Starlink()

#
# Fetch the data from the arduino and populate our central dictionary of values
#
def update_arduino_values():
    while True:
        try:
            resp = requests.get(arduino_addr + '/A0')
            current_load = 'N/A'
            resp_dict = {}
            if resp.status_code == 200:
                resp_dict = resp.json()
                current_data["battery_load"] = resp_dict['A0']
            else:
                print('Failed to communicate to arduino: ' + str(resp.status_code))
                current_data["battery_load"] = 0
        except Exception as e:
            print('Failed to communicate to arduino: ' + str(e))

        try:
            resp = requests.get(arduino_addr + '/A1')
            current_load = 'N/A'
            resp_dict = {}
            if resp.status_code == 200:
                resp_dict = resp.json()
                current_data["load_amps"] = resp_dict['A1']
            else:
                print('Failed to communicate to arduino: ' + str(resp.status_code))
                current_data["load_amps"] = 0
        except Exception as e:
            print('Failed to communicate to arduino: ' + str(e))
        time.sleep(5)


#
# Update the running stats with the latest data
#
def update_running_stats():
    global stats_data
    while True:
        try:
            if ('load_amps' in current_data) & ('battery_voltage' in current_data):
                stats_data['day_load_wh'] += 0.00139 * (current_data['load_amps'] * current_data['battery_voltage'])
                stats_data['day_solar_wh'] += 0.00139 * current_data['solar_watts']
                stats_data['day_batt_wh'] += 0.00139 * current_data['battery_load'] * current_data['battery_voltage']
                stats_data['total_load_wh'] += 0.00139 * (current_data['load_amps'] * current_data['battery_voltage'])
                stats_data['total_solar_wh'] += 0.00139 * current_data['solar_watts']
                if stats_data['current_date'] != datetime.today().date():
                    print('Start of new day : ' + str(stats_data['current_date']) + ' ---> ' + str(datetime.today().date()))
                    stats_data['current_date'] = datetime.today().date()
                    stats_data['thirty_days_batt_wh'].pop(0)
                    stats_data['thirty_days_batt_wh'].append(stats_data['day_batt_wh'])

                    stats_data['thirty_days_net'].pop(0)
                    stats_data['thirty_days_net'].append(stats_data['day_solar_wh'] - stats_data['day_load_wh'])
                    num_valid_entries = 0.0
                    avg_sum = 0.0
                    for val in stats_data['thirty_days_net']:
                        if val != 0:
                            avg_sum += val
                            num_valid_entries += 1
                    if num_valid_entries > 0:
                        stats_data['avg_net'] = avg_sum / num_valid_entries

                    stats_data['thirty_days_load'].pop(0)
                    stats_data['thirty_days_load'].append(stats_data['day_load_wh'])
                    num_valid_entries = 0.0
                    avg_sum = 0.0
                    for val in stats_data['thirty_days_load']:
                        if val != 0:
                            avg_sum += val
                            num_valid_entries += 1
                    if num_valid_entries > 0:
                        stats_data['avg_load'] = avg_sum / num_valid_entries

                    stats_data['thirty_days_solar'].pop(0)
                    stats_data['thirty_days_solar'].append(stats_data['day_solar_wh'])
                    num_valid_entries = 0.0
                    avg_sum = 0.0
                    for val in stats_data['thirty_days_solar']:
                        if val != 0:
                            avg_sum += val
                            num_valid_entries += 1
                    if num_valid_entries > 0:
                        stats_data['avg_solar'] = avg_sum / num_valid_entries

                    stats_data['total_net'].append(stats_data['day_solar_wh'] - stats_data['day_load_wh'])
                    stats_data['day_load_wh'] = 0
                    stats_data['day_solar_wh'] = 0
                    stats_data['day_batt_wh'] = 0

                stats_data['last_charge_state'] = current_data['charge_state']
            # persist the latest into a file to handle restarts
            with open('monitor_stats_data.pkl.tmp', 'wb') as f:
                pickle.dump(stats_data, f)
            shutil.move(os.path.join(os.getcwd(), 'monitor_stats_data.pkl.tmp'), os.path.join(os.getcwd(), 'monitor_stats_data.pkl'))
            time.sleep(5)
        except Exception as e:
            print('Failure in updating stats: ' + str(e))


#
# Update the values from the tristar modbus protocol in the values dictionary
#
def update_tristar_values():
    while True:
        # Connect directly to the modbus interface on the tristar charge controller to get the current information about
        # the state of the solar array and battery charging
        modbus_client = ModbusTcpClient(tristar_addr, port=502)
        try:
            modbus_client.connect()
            rr = modbus_client.read_holding_registers(0, 91, unit=1)
            if rr is None:
                modbus_client.close()
                print("Failed to connect and read from tristar modbus")
            else:
                voltage_scaling_factor = (float(rr.registers[0]) + (float(rr.registers[1]) / 100))
                amperage_scaling_factor = (float(rr.registers[2]) + (float(rr.registers[3]) / 100))

                # Voltage Related Statistics
                current_data["battery_voltage"] = float(rr.registers[24]) * voltage_scaling_factor * 2 ** (-15)
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
            print("Failed to connect to tristar modbus")
            modbus_client.close()
        time.sleep(5)


#
# Update the graph values in the background
#
def update_graph_values():
    while True:
        try:
            global graph_data
            graph_data['time'].append(datetime.now())
            graph_data['battload'].append(current_data["battery_load"])
            graph_data['battvoltage'].append(current_data["battery_voltage"])
            graph_data['battwatts'].append(current_data["battery_voltage"] * current_data["battery_load"])
            # At night this value plummets to zero and screws up the graph, so let's follow the voltage
            # for night time mode
            if current_data["target_regulation_voltage"] == 0:
                graph_data['targetbattvoltage'].append(current_data["battery_voltage"])
            else:
                graph_data['targetbattvoltage'].append(current_data["target_regulation_voltage"])
            graph_data['solarwatts'].append(current_data["solar_watts"])
            graph_data['net_production'].append(stats_data['day_solar_wh'] - stats_data['day_load_wh'])
            graph_data['load_watts'].append(current_data["load_amps"] * current_data["battery_voltage"])

            # If we have more than a days worth of graph data, start rotating out the old data
            while len(graph_data['time']) > 2880:
                graph_data['time'].pop(0)
                graph_data['battload'].pop(0)
                graph_data['battvoltage'].pop(0)
                graph_data['battwatts'].pop(0)
                graph_data['solarwatts'].pop(0)
                graph_data['targetbattvoltage'].pop(0)
                graph_data['net_production'].pop(0)
                graph_data['load_watts'].pop(0)

            # persist the latest into a file to handle restarts
            with open('monitor_data.pkl.tmp', 'wb') as f:
                pickle.dump(graph_data, f)
            shutil.move(os.path.join(os.getcwd(), 'monitor_data.pkl.tmp'), os.path.join(os.getcwd(), 'monitor_data.pkl'))
        except Exception as e:
            print("Failed to update graph statistics: " + str(e))
        time.sleep(60)


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
                    print("Detected that dishy is not connected, starting countdown")
                    start_not_connected_time = time.time()
                elif time.time() - start_not_connected_time > 28800:
                    print("Dishy not connected for over 8 hours, trying a power cycle")
                    for shelly in available_shellys:
                        if shelly.name.casefold() == "dishy".casefold():
                            print("Found shelly dishy device, power cycling dishy due to disconnected state...")
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
                            print("Found dishy powered off, starting counter")
                            start_power_off_time = time.time()
                        elif time.time() - start_power_off_time > 600:
                            print("Dishy off for over 10 minutes, turning back on")
                            shelly.turn_relay_on(0)
                            start_power_off_time = 0
                    else:
                        start_power_off_time = 0

            if dishy.is_stowed():
                print("Dishy is currently stowed")
                if start_stow_time == 0:
                    start_stow_time = time.time()
                elif time.time() - start_stow_time > 600:
                    print("Dishy stowed too long, unstowing dish")
                    dishy.dish_unstow()
            else:
                start_stow_time = 0
        except Exception as e:
            print("Failure in starlink monitoring: " + str(e))
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
# Handle a request for the graph data
#
@app.route("/graphData")
def get_graph_data():
    global graph_data

    return graph_data

@app.route("/currentData")
def get_current_data():
    global current_data

    return current_data

@app.route("/statsData")
def get_stats_data():
    global stats_data

    return stats_data

#
# provide the generic dishy status data through REST
#
@app.route("/starlink/status/")
def starlink_status():
    status = dishy.get_status()

    return json.dumps(status, indent=3)


#
# provide the dishy historical data through REST
#
@app.route("/starlink/history/")
def starlink_history():
    history = dishy.get_history()
    return json.dumps(history, indent=3)


#
# Get the obstruction image data, and transform into a png file and return through the get request
#
@app.route("/starlink/obstruction_image/")
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
def get_shelly_by_name(name) -> Shelly:
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


#
# Copy the graph data into place, initializing all arrays to the length indicated by the time array.  This protects
# against empty or missing values from getting things out of whack
#
def copy_graph_data(loaded_graph_data):
    graph_length = 0
    if 'time' in loaded_graph_data:
        graph_length = len(loaded_graph_data['time'])
    if graph_length > 0:
        graph_data['time'] = [0] * graph_length
        if 'time' in loaded_graph_data:
            for i in range(len(loaded_graph_data['time'])):
                graph_data['time'][i] = loaded_graph_data['time'][i]
        graph_data['battload'] = [0] * graph_length
        if 'battload' in loaded_graph_data:
            for i in range(len(loaded_graph_data['battload'])):
                graph_data['battload'].append(loaded_graph_data['battload'][i])
                graph_data['battload'].pop(0)
        graph_data['battvoltage'] = [23] * graph_length
        if 'battvoltage' in loaded_graph_data:
            for i in range(len(loaded_graph_data['battvoltage'])):
                graph_data['battvoltage'].append(loaded_graph_data['battvoltage'][i])
                graph_data['battvoltage'].pop(0)
        graph_data['battwatts'] = [0] * graph_length
        if 'battwatts' in loaded_graph_data:
            for i in range(len(loaded_graph_data['battwatts'])):
                graph_data['battwatts'].append(loaded_graph_data['battwatts'][i])
                graph_data['battwatts'].pop(0)
        graph_data['solarwatts'] = [0] * graph_length
        if 'solarwatts' in loaded_graph_data:
            for i in range(len(loaded_graph_data['solarwatts'])):
                graph_data['solarwatts'].append(loaded_graph_data['solarwatts'][i])
                graph_data['solarwatts'].pop(0)
        graph_data['targetbattvoltage'] = [23] * graph_length
        if 'targetbattvoltage' in loaded_graph_data:
            for i in range(len(loaded_graph_data['targetbattvoltage'])):
                graph_data['targetbattvoltage'].append(loaded_graph_data['targetbattvoltage'][i])
                graph_data['targetbattvoltage'].pop(0)
        graph_data['net_production'] = [0] * graph_length
        if 'net_production' in loaded_graph_data:
            for i in range(len(loaded_graph_data['net_production'])):
                graph_data['net_production'].append(loaded_graph_data['net_production'][i])
                graph_data['net_production'].pop(0)
        graph_data['load_watts'] = [0] * graph_length
        if 'load_watts' in loaded_graph_data:
            for i in range(len(loaded_graph_data['load_watts'])):
                graph_data['load_watts'].append(loaded_graph_data['load_watts'][i])
                graph_data['load_watts'].pop(0)


def main():
    global graph_data
    global stats_data
    if path.exists('monitor_data.pkl'):
        try:
            with open('monitor_data.pkl', 'rb') as f:
                # Load into a temp variable so if it fails we stick with initial values
                print("loading graph data from pkl file")
                loaded_graph_data = pickle.loads(f.read())
                copy_graph_data(loaded_graph_data)
        except Exception as e:
            print("Failed to load monitor pkl data: " + str(e))
    if path.exists('monitor_stats_data.pkl'):
        try:
            with open('monitor_stats_data.pkl', 'rb') as f:
                # Load into a temp variale so if it fails we stick with the initial values
                print("Loading stats data from pkl file")
                load_stats_data = pickle.loads(f.read())
                for key, value in load_stats_data.items():
                    stats_data[key] = value
        except Exception as e:
            print("Failed to load stats monitor pkl data: " + str(e))
    arduino_thread = threading.Thread(target=update_arduino_values, args=())
    arduino_thread.daemon = True
    arduino_thread.start()

    tristar_thread = threading.Thread(target=update_tristar_values, args=())
    tristar_thread.daemon = True
    tristar_thread.start()

    stats_thread = threading.Thread(target=update_running_stats, args=())
    stats_thread.daemon = True
    stats_thread.start()

    graph_thread = threading.Thread(target=update_graph_values, args=())
    graph_thread.daemon = True
    graph_thread.start()

    starlink_thread = threading.Thread(target=manage_starlink, args=())
    starlink_thread.daemon = True
    starlink_thread.start()

    logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

    retry_count = 0
    while True:
        try:
            available_shellys.append(Shelly("http://10.0.10.41"))
            print("Shelly device 10.0.10.41 successfully added")
            break
        except Exception as e:
            retry_count += 1
            print("Failed to add shelly device 10.0.10.41: " + str(e))
            if retry_count > 5:
                break
            time.sleep(15)

    retry_count = 0
    while True:
        try:
            available_shellys.append(Shelly("http://10.0.10.40"))
            print("Shelly device 10.0.10.40 successfully added")
            break
        except Exception as e:
            retry_count += 1
            print("Failed to add shelly device 10.0.10.40: " + str(e))
            if retry_count > 5:
                break
            time.sleep(15)


    app.run(port=8050, host='0.0.0.0')


#
# Startup the flask server on port 9999.  Change the port here if you want it listening somewhere else, and simply
# execute this python file to startup your server and serve the svelte app
#
if __name__ == "__main__":
    main()
