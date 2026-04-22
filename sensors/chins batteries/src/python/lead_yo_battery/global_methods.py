from lead_yo_battery.SmartBattery import SmartBattery
import asyncio
import logging
from bleak import BleakScanner

logger = logging.getLogger('lead_yo_battery')


#
# Look for all LeadYO battery advertisements by finding any advertisements that include their uuid as a supported
# protocol.  Return an instance of a smart battery object for each found instance.
#
async def async_find_all_batteries(refresh_rate: int = 5) -> [SmartBattery]:

    logger.debug("Finding all available batteries within range")
    found_batteries = []
    devices = await BleakScanner.discover(timeout=30, return_adv=False)
    for d in devices:
        logger.debug('%s>>%s>>%s>>%s', str(d.name), str(d.address), str(d.metadata), str(d.rssi))
        uuids = d.metadata.get('uuids', {})

        if '0000ff00-0000-1000-8000-00805f9b34fb' in uuids:
            logger.info("Found battery %s at %s", str(d.name), str(d.address))
            found_batteries.append(SmartBattery(d.address, d.name, refresh_rate=refresh_rate))

    return found_batteries


#
# Synchronous version of the above async function
#
def find_all_batteries(refresh_rate: int = 5) -> [SmartBattery]:
    return asyncio.run(async_find_all_batteries(refresh_rate))

