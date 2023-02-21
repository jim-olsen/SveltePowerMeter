import requests
import logging

logging.basicConfig()
logging.getLogger('shelly_device').setLevel(logging.WARNING)
logger = logging.getLogger('shelly_device')


class Shelly:
    shelly_url = None
    name = None
    id = None
    mac = None
    model = None
    generation = None
    version = None
    application = None
    firmware_id = None

    def __init__(self, url):
        if url is not None:
            self.shelly_url = url
            settings = self.get_settings()
            self.name = settings.get("name", None)
            self.id = settings.get("id", None)
            self.mac = settings.get("mac", None)
            self.model = settings.get("model", None)
            self.generation = settings.get("gen", None)
            self.version = settings.get("ver", None)
            self.application = settings.get("app", None)
            self.firmware_id = settings.get("fw_id", None)

    def get_status(self):
        r = requests.get(self.shelly_url + '/rpc.Sys.getStatus')
        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Failed to retrieve status from Shelly+ {r.status_code}")
            return {}

    def get_settings(self):
        r = requests.get(self.shelly_url + '/shelly')
        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Failed to retrieve settings from Shelly+ {r.status_code}")
            return {}

    def get_relay_status(self, relay=0):
        r = requests.get(self.shelly_url + '/relay/' + str(relay))
        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Failed to retrieve relay status from Shelly+ {r.status_code}")
            return {}

    def turn_relay_on(self, relay=0):
        r = requests.get(self.shelly_url + '/relay/' + str(relay) + '?turn=on')
        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Failed to turn relay on for Shelly+ {r.status_code}")
            return {}

    def turn_relay_off(self, relay=0):
        r = requests.get(self.shelly_url + '/relay/' + str(relay) + '?turn=off')
        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Failed to turn relay off for Shelly+ {r.status_code}")
            return {}

    def power_cycle_relay(self, relay=0, delay=5):
        r = requests.get(self.shelly_url + '/relay/' + str(relay) + '?turn=off&timer=' + str(delay))
        if r.status_code == 200:
            while True:
                current_status = self.get_relay_status(relay)
                if "ison" in current_status:
                    if current_status["ison"]:
                        break
                else:
                    logger.error(f"Received a status response on power cycle with no relay status, aborting... {current_status}")
                    break
            return r.json()
        else:
            logger.error(f"Failed to turn relay off for Shelly+ {r.status_code}")
            return {}


def main():
    shelly = Shelly("http://10.0.10.41")
    print(shelly.get_settings())
    print(shelly.get_status())
    print(shelly.get_relay_status(0))
    print(shelly.turn_relay_off(0))
    print(shelly.turn_relay_on(0))
    print(shelly.power_cycle_relay(0))
    print(shelly.get_relay_status(0))


if __name__ == '__main__':
    main()
