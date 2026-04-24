import sqlite3
import time
from datetime import datetime, timedelta

def create_sql_tables_if_not_exist():
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

def update_sql_tables(current_data, weather_data, stats_data, batteries):
    sql_connection = sqlite3.connect("powerdata.db")
    with sql_connection:
        cursor = sql_connection.execute("SELECT record_date FROM daily_power_data where record_date = ?",
                                        [int(time.mktime(datetime.today().replace(hour=0, minute=0, second=0,
                                                                                  microsecond=0).timetuple()))])
        if cursor.fetchone() is None:
            stats_data.day_load_wh = 0
            stats_data.day_solar_wh = 0
            stats_data.day_batt_wh = 0

        sql_connection.execute('''INSERT OR REPLACE INTO daily_power_data (record_date, day_load_wh, day_solar_wh, 
                day_batt_wh, last_charge_state) VALUES (?,?,?,?,?);''',
                               (
                                   int(time.mktime(datetime.today().replace(hour=0, minute=0, second=0,
                                                                            microsecond=0).timetuple())),
                                   stats_data.day_load_wh, stats_data.day_solar_wh,
                                   stats_data.day_batt_wh, stats_data.last_charge_state))
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
                                   current_data.battery_load,
                                   current_data.load_amps,
                                   current_data.load_watts,
                                   current_data.battery_voltage,
                                   current_data.battery_voltage * current_data.battery_load if current_data.battery_voltage and current_data.battery_load else 0,
                                   current_data.day_solar_wh - current_data.day_load_wh if current_data.day_solar_wh and current_data.day_load_wh else 0,
                                   current_data.battery_sense_voltage,
                                   current_data.battery_voltage_slow,
                                   current_data.battery_daily_minimum_voltage,
                                   current_data.battery_daily_maximum_voltage,
                                   current_data.target_regulation_voltage,
                                   current_data.array_voltage,
                                   current_data.array_charge_current,
                                   current_data.battery_charge_current,
                                   current_data.battery_charge_current_slow,
                                   current_data.input_power,
                                   current_data.solar_watts,
                                   current_data.heatsink_temperature,
                                   current_data.battery_temperature,
                                   current_data.charge_state,
                                   current_data.seconds_in_absorption_daily,
                                   current_data.seconds_in_float_daily,
                                   current_data.seconds_in_equalization_daily
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
                      weather_data.altimeter_inHg,
                      weather_data.barometer_inHg,
                      weather_data.cloudbase_foot,
                      weather_data.daily_rain,
                      weather_data.dayRain_in,
                      weather_data.dewpoint_F,
                      weather_data.heatindex_F,
                      weather_data.hourRain_in,
                      weather_data.humidex_F,
                      weather_data.inTemp_F,
                      weather_data.outHumidity,
                      weather_data.outTemp_F,
                      weather_data.pressure_inHg,
                      weather_data.rain24_in,
                      weather_data.rainRate_inch_per_hour,
                      weather_data.rain_in,
                      weather_data.rain_total,
                      weather_data.windSpeed_mph,
                      weather_data.wind_average,
                      weather_data.windchill_F))

    battery_sql_connection = sqlite3.connect("battery.db")
    for battery_name, battery in batteries.items():
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
                  next(iter(battery.get("battery_temps_f", [None, None, None])[1:2]), None),
                  next(iter(battery.get("battery_temps_f", [None, None, None])[2:3]), None),
                  battery.get("cell_block_voltages", [None, None, None, None])[0],
                  battery.get("cell_block_voltages", [None, None, None, None])[1],
                  battery.get("cell_block_voltages", [None, None, None, None])[2],
                  battery.get("cell_block_voltages", [None, None, None, None])[3]
                  ))

def update_stats_data_from_db(stats_data):
    sql_connection = sqlite3.connect("powerdata.db")
    sql_connection.row_factory = sqlite3.Row
    with sql_connection:
        cursor = sql_connection.execute('''SELECT avg(day_batt_wh) AS avg_net, avg(day_load_wh) AS avg_load, 
            avg(day_solar_wh) AS avg_solar, sum(day_load_wh) AS total_load_wh, sum(day_solar_wh) AS total_solar_wh 
            FROM daily_power_data
            ''')
        summary_data = cursor.fetchone()
        stats_data.avg_net = summary_data['avg_net']
        stats_data.avg_load = summary_data['avg_load']
        stats_data.avg_solar = summary_data['avg_solar']
        stats_data.total_load_wh = summary_data['total_load_wh']
        stats_data.total_solar_wh = summary_data['total_solar_wh']

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
            stats_data.yesterday_batt_wh = yesterdays_data['yesterday_batt_wh']
            stats_data.yesterday_load_wh = yesterdays_data['yesterday_load_wh']
            stats_data.yesterday_net_wh = yesterdays_data['yesterday_net_wh']

        cursor = sql_connection.execute('''
            SELECT sum(day_solar_wh - day_load_wh) AS five_day_net FROM daily_power_data WHERE record_date >= ?
                ''',
                                [int(time.mktime(
                                    (datetime.today().replace(hour=0, minute=0, second=0,
                                                              microsecond=0) - timedelta(days=5)).timetuple()))
                                ])
        net_data = cursor.fetchone()
        if net_data is not None:
            stats_data.five_day_net = net_data['five_day_net']

        cursor = sql_connection.execute('''
            SELECT sum(day_solar_wh - day_load_wh) AS ten_day_net FROM daily_power_data WHERE record_date >= ?
            ''',
                                [int(time.mktime(
                                    (datetime.today().replace(hour=0, minute=0, second=0,
                                                              microsecond=0) - timedelta(days=10)).timetuple()))
                                ])
        net_data = cursor.fetchone()
        if net_data is not None:
            stats_data.ten_day_net = net_data['ten_day_net']

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
            stats_data.five_min_load_watts = net_data['five_min_load_watts']
            stats_data.five_min_battery_watts = net_data['five_min_battery_watts']
            stats_data.five_min_solar_watts = net_data['five_min_solar_watts']
            stats_data.five_min_battery_voltage = net_data['five_min_battery_voltage']

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
            stats_data.battery_min_percent = row['battery_min_percent']
            stats_data.battery_max_percent = row['battery_max_percent']
        cursor = battery_sql_connection.execute(
                '''
                SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                    (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                        WHERE record_time >= ? AND record_time < ? GROUP BY name)
                ''',
                [
                    int(time.mktime((datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).timetuple())),
                    int(time.mktime((datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))
                ])
        row = cursor.fetchone()
        if row is not None:
            stats_data.battery_min_percent_one_day_ago = row['battery_min_percent']
            stats_data.battery_max_percent_one_day_ago = row['battery_max_percent']
        cursor = battery_sql_connection.execute(
                '''
                SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                    (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                        WHERE record_time >= ? AND record_time < ? GROUP BY name)
                ''',
                [
                    int(time.mktime((datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)).timetuple())),
                    int(time.mktime((datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).timetuple()))
                ])
        row = cursor.fetchone()
        if row is not None:
            stats_data.battery_min_percent_two_days_ago = row['battery_min_percent']
            stats_data.battery_max_percent_two_days_ago = row['battery_max_percent']
        cursor = battery_sql_connection.execute(
                '''
                SELECT AVG(min_capacity) AS battery_min_percent, AVG(max_capacity) AS battery_max_percent FROM 
                    (SELECT name, MAX(capacity_percent) AS max_capacity, MIN(capacity_percent) AS min_capacity FROM battery_data 
                        WHERE record_time >= ? AND record_time < ? GROUP BY name)
                ''',
                [
                    int(time.mktime((datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)).timetuple())),
                    int(time.mktime((datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)).timetuple()))
                ])
        row = cursor.fetchone()
        if row is not None:
            stats_data.battery_min_percent_three_days_ago = row['battery_min_percent']
            stats_data.battery_max_percent_three_days_ago = row['battery_max_percent']

def get_graph_data(days, data_fields):
    graph_data = {'time': []}
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
            graph_data['time'].append(datetime.fromtimestamp(rowdict.get('record_time', 0)))
            for field in data_fields:
                graph_data[field].append(rowdict.get(field, 0))
    return graph_data

def get_battery_graph_data(days, data_fields, battery_name):
    graph_data = {'time': []}
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
            graph_data['time'].append(datetime.fromtimestamp(rowdict.get('record_time', 0)))
            for field in data_fields:
                graph_data[field].append(rowdict.get(field, 0))
    return graph_data

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
                                               (datetime.today().replace(hour=0, minute=0, second=0,
                                                                         microsecond=0)).timetuple()))
                                           ])
        return cursor.fetchone()

def get_weather_graph_data(days, data_fields):
    graph_data = {'time': []}
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
            graph_data['time'].append(datetime.fromtimestamp(rowdict.get('record_time', 0)))
            for field in data_fields:
                graph_data[field].append(rowdict.get(field, 0))
    return graph_data

def get_lightning_data():
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

def add_lightning_event(record_time, event, distance, intensity):
    sql_connection = sqlite3.connect("lightning.db")
    with sql_connection:
        sql_connection.execute("INSERT INTO lightning_data(record_time, event, distance, intensity) VALUES (?,?,?,?)",
                               (record_time, event, distance, intensity))

def refresh_daily_data(stats_data):
    sql_connection = sqlite3.connect("powerdata.db")
    sql_connection.row_factory = sqlite3.Row
    with sql_connection:
        cursor = sql_connection.execute('''SELECT * FROM daily_power_data WHERE record_date = ?''',
                                        [int(time.mktime(datetime.today().replace(hour=0, minute=0, second=0,
                                                                                  microsecond=0).timetuple()))])
        row = cursor.fetchone()
        if row is not None:
            stats_data.day_load_wh = row['day_load_wh']
            stats_data.day_solar_wh = row['day_solar_wh']
            stats_data.day_batt_wh = row['day_batt_wh']
            stats_data.last_charge_state = row['last_charge_state']
