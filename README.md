# SveltePowerMeter

SveltePowerMeter is a home monitoring platform for tracking solar/battery power, weather, lightning strikes, aircraft (ADS-B), bird activity, Starlink connectivity, Shelly smart relays, security camera alerts (Blue Iris), and more.

The system is built around a simple **hub-and-spoke** architecture:

- A collection of small, independent **sensor** programs (under [`sensors/`](sensors)) run on Raspberry Pis or other small devices near the hardware they monitor. Each one talks to its device/hardware and publishes readings to an **MQTT broker**.
- The **main server** (under [`src/python`](src/python)) subscribes to all of the relevant MQTT topics, stores incoming data in a SQLite database, and exposes it via a REST/WebSocket API.
- The **web UI** (under [`src/svelte`](src/svelte)) is a Svelte single-page application that is served by the main server and visualizes all of the collected data (dashboards, graphs, controls).
- [`tools/`](tools) contains small utility scripts (e.g. an MQTT test/monitoring client) useful for debugging the message bus.

All components communicate over a shared MQTT broker, so an MQTT broker (e.g. [Mosquitto](https://mosquitto.org/)) must be running and reachable by every component before anything else will work.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Main Server (`src/python`)](#main-server-srcpython)
- [Web UI (`src/svelte`)](#web-ui-srcsvelte)
- [Sensors (`sensors/`)](#sensors)
  - [Ecowitt Weather Station Bridge](#ecowitt-weather-station-bridge)
  - [Lightning Detector](#lightning-detector)
  - [Shelly Smart Relay Controller](#shelly-smart-relay-controller)
  - [Starlink Monitor](#starlink-monitor)
  - [Chins/Lead-Yo BLE Battery Monitor](#chinslead-yo-ble-battery-monitor)
  - [Victron BLE Energy Monitor](#victron-ble-energy-monitor)
- [Tools](#tools)

## Prerequisites

- Python 3.9+ (each Python component has its own `requirements.txt`).
- Node.js/npm (to build the Svelte UI).
- An MQTT broker (e.g. Mosquitto) reachable from the main server and every sensor.
- Each component defines `MQTT_SERVER_ADDR` at the top of its main script. **Update this value to the IP/hostname of your MQTT broker before running any component.**

## Main Server (`src/python`)

Location: [`src/python/server.py`](src/python/server.py)

This is the core of the project. It is a [Quart](https://quart.palletsprojects.com/) (async Flask-like) application that:

- Serves the built Svelte application (see [Web UI](#web-ui-srcsvelte)) as static files.
- Exposes REST endpoints such as `/currentData`, `/graphData`, `/batteryData`, `/graphBatteryData`, `/weatherData`, `/graphWxData`, `/blueirisAlert`, `/adsbData`, `/lightningData`, `/birdData`, `/birdHistory`, `/birdDetails/<id>`, `/birdPicture/<id>`, `/statsData`, `/starlinkStatus`, `/starlinkHistory`, `/starlinkObstructionImage`, `/shellyDevices`, `/relayStatus`, `/turnRelayOn`, `/turnRelayOff`, `/powerCycleRelay`.
- Emits real-time updates to the UI over Socket.IO.
- Connects to the MQTT broker and subscribes to topics published by the sensors (`weather/loop`, `blueiris`, `birdnet`, `adsb`, `battery_status`, `lightning_data`, `solar_charger_data`, `dc_meter_data`, `battery_monitor_data`, `starlink`, `lights`), persisting the data via `sql_manager` into a local SQLite database.
- Periodically recalculates running statistics (daily/weekly power totals, etc.) in a background thread.
- Listens on port **8050** by default.

### Setup & Configuration

1. Install dependencies:
   ```bash
   cd src/python
   pip install -r requirements.txt
   ```
2. Edit `MQTT_SERVER_ADDR` near the top of `server.py` to point at your MQTT broker.
3. Build the Svelte UI first (see below) so that `src/svelte/public` exists — the server serves the UI directly from that folder.
4. Run the server:
   ```bash
   python server.py
   ```
5. Browse to `http://<server-host>:8050`.

The server will automatically create any required SQLite tables on first run.

## Web UI (`src/svelte`)

Location: [`src/svelte`](src/svelte)

A [Svelte](https://svelte.dev/) single-page application providing the dashboards for all subsystems (power/battery, weather, lightning, birds, Starlink, Shelly relays, ADS-B, etc.). Components are organized by subsystem under `src/components/` (e.g. `powermeter`, `weather`, `lightning`, `starlink`, `shelly`, `bird`, `navigation`). Application state is centralized in `src/stores.svelte.js`, which talks to the main server's REST API and Socket.IO events.

### Setup & Usage

1. Install dependencies:
   ```bash
   cd src/svelte
   npm install
   ```
2. Development (watch/rebuild on change, served with live-reload):
   ```bash
   npm run dev
   ```
3. Production build (outputs static files into `public/`, which is what the main server serves):
   ```bash
   npm run build
   ```
4. Optionally, preview the built app standalone (without the Python server/API):
   ```bash
   npm run start
   ```

For the full application experience (real data, relay control, etc.), always run `npm run build` and then start the main Python server, since it is the server that serves the `public/` folder and provides the API/WebSocket backend.

## Sensors

Each sensor is a standalone Python program meant to be run close to its hardware (typically on a Raspberry Pi). All sensors connect to the same MQTT broker and publish JSON payloads to specific topics, which the main server consumes. Before running any sensor, install its dependencies and set `MQTT_SERVER_ADDR` at the top of its script to your broker's address.

### Ecowitt Weather Station Bridge

Location: [`sensors/ecowitt/src/python/server.py`](sensors/ecowitt/src/python/server.py)

A small Flask HTTP server that receives data pushed by an Ecowitt (or Weather Underground-compatible) weather station and republishes it as normalized JSON to the MQTT topic `weather/loop`. It also computes wind chill and dew point when not directly provided.

- Endpoints:
  - `GET /wxData` — accepts Weather Underground-style query parameters.
  - `POST /data/report` — accepts Ecowitt's native "Customized Server" form-post format.
- Listens on port **8090** by default.

**Setup:**
```bash
cd sensors/ecowitt/src/python
pip install flask paho-mqtt
python server.py
```
Configure your Ecowitt console/gateway's "Customized" upload settings to point at `http://<this-host>:8090/data/report`.

### Lightning Detector

Location: [`sensors/lightning_detector/src/python/lightning_detector.py`](sensors/lightning_detector/src/python/lightning_detector.py)

Reads a DFRobot AS3935 lightning sensor over I2C on a Raspberry Pi (via `DFRobot_AS3935_Lib.py`) and publishes detected lightning/disturber/noise events to the MQTT topic `lightning_data`.

- Requires I2C to be enabled on the Raspberry Pi.
- Default I2C address: `0x03`, tuning capacitance: `96`, IRQ GPIO pin: `4` (BCM numbering) — edit the constants at the top of the script if your wiring differs.

**Setup:**
```bash
cd sensors/lightning_detector/src/python
pip install -r requirements.txt
python lightning_detector.py
```

### Shelly Smart Relay Controller

Location: [`sensors/shelly/src/python/server.py`](sensors/shelly/src/python/server.py)

Bridges Shelly smart relay devices (Gen1/announce-based) to MQTT. It listens for `shellies/announce`, Wi-Fi and switch status updates, tracks known devices, and lets other components turn relays on/off or power-cycle them by publishing to `lights/<id>/command` with a payload of `on`, `off`, or `cycle <seconds>`. Device state is republished on the `lights` topic for the main server to consume.

**Setup:**
```bash
cd sensors/shelly/src/python
pip install -r requirements.txt
python server.py
```
Ensure your Shelly devices are configured to use the same MQTT broker (and, ideally, the "shellies/announce" MQTT integration).

### Starlink Monitor

Location: [`sensors/starlink/src/python/server.py`](sensors/starlink/src/python/server.py)

Polls a Starlink dish (via the `Starlink.py` gRPC client) for status, history, and obstruction map data once per second, and publishes it to the MQTT topic `starlink`.

**Setup:**
```bash
cd sensors/starlink/src/python
pip install grpcio grpcio-tools grpcio-reflection protobuf yagrc paho-mqtt
python server.py
```
Must run on a machine that has network access to the Starlink dish (normally `192.168.100.1`).

### Chins/Lead-Yo BLE Battery Monitor

Location: [`sensors/chins_batteries/src/python/battery_monitor.py`](sensors/chins_batteries/src/python/battery_monitor.py)

Discovers and connects (via Bluetooth LE, using the bundled `lead_yo_battery` package) to a bank of "Lead-Yo"/Chins-style smart LiFePO4 batteries, reads voltage, current, capacity, cell balance, temperatures, and protection status from each, and publishes the readings to the MQTT topic `battery_status`.

- Filters for battery names starting with `BANK1`–`BANK4` — adjust the filter in `async_monitor_batteries` if your battery names differ.
- Automatically exits (to allow a supervisor/systemd to restart it) if too many consecutive read failures occur, which works around occasional BlueZ hangs.

**Setup:**
```bash
cd sensors/chins_batteries/src/python
pip install -r requirements.txt
python battery_monitor.py
```
Run on a Raspberry Pi (or other Linux host) with Bluetooth within range of the batteries. It's recommended to run this under a process supervisor (e.g. systemd) since the script intentionally exits on repeated failures to reset Bluetooth state.

### Victron BLE Energy Monitor

Location: [`sensors/victron_ble/src/python/energy_monitor_ble_only.py`](sensors/victron_ble/src/python/energy_monitor_ble_only.py)

Passively scans for BLE advertisements from Victron devices (solar chargers / SmartShunts), decrypts the manufacturer data using each device's per-installation encryption key, and publishes the decoded readings to MQTT (`solar_charger_data` / `dc_meter_data`, consumed by the main server).

- Edit `VICTRON_ADDRESSES` and `VICTRON_BLE_KEYS` at the top of the script with your own device MAC addresses and encryption keys (obtainable once from the VictronConnect app).

**Setup:**
```bash
cd sensors/victron_ble/src/python
pip install -r requirements.txt
python energy_monitor_ble_only.py
```
Run on a Raspberry Pi (or other Linux host) with Bluetooth within range of the Victron devices.

## Tools

### MQTT Monitor / Test Client

Location: [`tools/mqtt monitor/src/python/mqtt_test_client.py`](tools/mqtt%20monitor/src/python/mqtt_test_client.py)

A simple diagnostic script that connects to the MQTT broker and logs incoming messages for one or more topics. Useful for verifying that a sensor is publishing data correctly. Edit the `c.subscribe(...)` calls to choose which topics to monitor, and update `MQTT_SERVER_ADDR` to point at your broker.

**Usage:**
```bash
cd "tools/mqtt monitor/src/python"
pip install paho-mqtt
python mqtt_test_client.py
```
