import requests
import time

SHELLY_ADDR = "http://10.0.10.40"

r = requests.get(SHELLY_ADDR + "/rpc/Sys.getStatus")
print(r.text)

r = requests.get(SHELLY_ADDR + "/shelly")
print(r.text)

r = requests.get(SHELLY_ADDR + "/relay/0")
print(r.text)

r = requests.get(SHELLY_ADDR + "/relay/0?turn=off&timer=2")
print(r.text)

r = requests.get(SHELLY_ADDR + "/relay/0")
print(r.text)

time.sleep(5)

r = requests.get(SHELLY_ADDR + "/relay/0")
print(r.text)
