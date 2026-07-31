import serial
import threading
import time
import logging
import os
import json
import paho.mqtt.client as mqtt
from typing import Optional

MQTT_SERVER_ADDR = '10.0.10.31'
MQTT_CLIENT: Optional[mqtt.Client] = None

logging.basicConfig()
logger = logging.getLogger('ve_network_smartshunt')
logger.setLevel(logging.DEBUG)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# History Field Mapping based on Victron VE.Direct Protocol specification
HISTORY_MAP = {
    "H1": ("Deepest Discharge", "Ah", lambda x: float(x) / 1000.0),
    "H2": ("Last Discharge", "Ah", lambda x: float(x) / 1000.0),
    "H3": ("Average Discharge", "Ah", lambda x: float(x) / 1000.0),
    "H4": ("Number of Charge Cycles", "", lambda x: int(x)),
    "H5": ("Number of Full Discharges", "", lambda x: int(x)),
    "H6": ("Cumulative Amp Hours Drawn", "Ah", lambda x: float(x) / 1000.0),
    "H7": ("Minimum Battery Voltage", "V", lambda x: float(x) / 1000.0),
    "H8": ("Maximum Battery Voltage", "V", lambda x: float(x) / 1000.0),
    "H9": ("Time Since Last Full Charge", "Hours", lambda x: round(float(x) / 3600.0, 1)),
    "H10": ("Automatic Synchronizations", "", lambda x: int(x)),
    "H11": ("Low Voltage Alarms", "", lambda x: int(x)),
    "H12": ("High Voltage Alarms", "", lambda x: int(x)),
    "H17": ("Total Discharged Energy", "Wh", lambda x: float(x)),
    "H18": ("Total Charged Energy", "Wh", lambda x: float(x)),
}

# Key real-time fields for context
REALTIME_MAP = {
    "V": ("Battery Voltage", "V", lambda x: float(x) / 1000.0),
    "I": ("Current", "A", lambda x: float(x) / 1000.0),
    "P": ("Power", "W", lambda x: float(x)),
    "SOC": ("State of Charge", "%", lambda x: float(x) / 10.0),
    "TTG": ("Time To Go", "Mins", lambda x: int(x) if int(x) > 0 else "N/A"),
}


class VEDirectReader:
    def __init__(self, port="/dev/ttyUSB0", baudrate=19200):
        self.ser = serial.Serial(port, baudrate, timeout=2)
        self.buffer = {}

    def read_frame(self):
        """Reads one full VE.Direct frame ending with Checksum."""
        frame = {}
        while True:
            line = self.ser.readline().decode("latin-1", errors="ignore").strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) == 2:
                key, val = parts[0], parts[1]
                frame[key] = val
                if key == "Checksum":
                    return frame

def publish_data(frame):
    global MQTT_CLIENT
    if MQTT_CLIENT is None:
        return
    packet: dict = {}
    for key, (label, unit, conv) in REALTIME_MAP.items():
        if key in frame:
            try:
                val = conv(frame[key])
                logger.debug(f" {key}-{label:<28}: {val} {unit}")
                packet[key] = val
            except ValueError:
                pass
    for key, (label, unit, conv) in HISTORY_MAP.items():
        if key in frame:
            try:
                val = conv(frame[key])
                logger.debug(f" {key}-{label:<28}: {val} {unit}")
                packet[key] = val
            except ValueError:
                pass
    MQTT_CLIENT.publish("ve_smart_shunt", json.dumps(packet))

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

    client = mqtt.Client()
    client.on_connect = on_connect
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


def main():
    # USB serial port on Raspberry Pi (adjust if using /dev/ttyUSB1 or /dev/ttyAMA0)
    serial_port = "/dev/ttyUSB0"

    logger.warning(f"Connecting to Victron SmartShunt on {serial_port}...")
    reader = VEDirectReader(port=serial_port)
    logger.warning("Connected to Victron SmartShunt.")

    mqtt_thread = threading.Thread(target=start_mqtt_client, args=())
    mqtt_thread.daemon = True
    mqtt_thread.start()

    try:
        while True:
            frame = reader.read_frame()
            if frame:
                publish_data(frame)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("\nStopping reader.")
    finally:
        reader.ser.close()


if __name__ == "__main__":
    main()