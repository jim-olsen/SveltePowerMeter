import serial
import time

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


def display_data(frame):
    print("\033[H\033[J", end="")  # Clear terminal screen
    print("============================================")
    print("     VICTRON SMARTSHUNT - REAL-TIME DATA    ")
    print("============================================")
    for key, (label, unit, conv) in REALTIME_MAP.items():
        if key in frame:
            try:
                val = conv(frame[key])
                print(f" {label:<28}: {val} {unit}")
            except ValueError:
                pass

    print("\n============================================")
    print("        VICTRON SMARTSHUNT - HISTORY        ")
    print("============================================")
    for key, (label, unit, conv) in HISTORY_MAP.items():
        if key in frame:
            try:
                val = conv(frame[key])
                print(f" {label:<28}: {val} {unit}")
            except ValueError:
                pass
    print("============================================\n")


def main():
    # USB serial port on Raspberry Pi (adjust if using /dev/ttyUSB1 or /dev/ttyAMA0)
    serial_port = "/dev/ttyUSB0"

    print(f"Connecting to Victron SmartShunt on {serial_port}...")
    reader = VEDirectReader(port=serial_port)

    try:
        while True:
            frame = reader.read_frame()
            if frame:
                display_data(frame)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping reader.")
    finally:
        reader.ser.close()


if __name__ == "__main__":
    main()