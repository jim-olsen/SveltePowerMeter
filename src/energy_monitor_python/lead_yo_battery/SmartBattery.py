import asyncio
import logging
import time

from bleak import BleakClient, BLEDevice
from typing import Union

logger = logging.getLogger('lead_yo_battery')

class SmartBattery:
    SPP_DATA_UUID = '0000ff01-0000-1000-8000-00805f9b34fb'
    SPP_COMMAND_UUID = '0000ff02-0000-1000-8000-00805f9b34fb'

    def __init__(self, battery_address: Union[BLEDevice, str], battery_name):
        self.battery_address = battery_address
        self.battery_name = battery_name
        self.spp_command_characteristic = None
        self.spp_data_characteristic = None
        self.basic_information_and_status = None
        self.cell_block_voltage = None
        self.last_basic_info_update = None

    async def async_update_characteristics(self, client):
        self.spp_data_characteristic = None
        self.spp_command_characteristic = None
        for service in client.services:
            logger.debug("%s", str(service))
            try:
                logger.debug(">>>> Service Characteristics")
                for characteristic in service.characteristics:
                    logger.debug("      %s:%s", str(characteristic), str(characteristic.properties))
                    if characteristic.uuid == SmartBattery.SPP_DATA_UUID:
                        logger.debug("Found SPP data characteristic")
                        self.spp_data_characteristic = characteristic
                    elif characteristic.uuid == SmartBattery.SPP_COMMAND_UUID:
                        logger.debug("Found SPP command characteristic")
                        self.spp_command_characteristic = characteristic
            except Exception as e:
                print(e)

    async def async_get_basic_info_and_status(self):
        command_complete = asyncio.Event()
        data_length_of_response = 0
        current_data_queue = bytearray()

        def data_received(characteristic, data):
            nonlocal data_length_of_response
            nonlocal current_data_queue
            logger.debug("Received data: %s", str(data))

            # If we receive the correct response to our request to get the info start gathering it
            if data[:2] == bytearray([0xDD, 0x03]):
                data_length_of_response = data[3]
                logger.debug("Total length of data response %s", str(data_length_of_response))
                self.basic_information_and_status = bytearray(data[4:])
                current_data_queue = self.basic_information_and_status
                logger.debug("Current response data: " + str(self.basic_information_and_status))
                if len(self.basic_information_and_status) >= data_length_of_response:
                    logger.debug("Got all the data, proceeding")
                    command_complete.set()
                else:
                    logger.debug("Response data not complete, waiting for more data to arrive")
            elif data[:2] == bytearray([0xDD, 0x04]):
                data_length_of_response = data[3]
                logger.debug("Total length of data response %s", str(data_length_of_response))
                self.cell_block_voltage = bytearray(data[4:])
                current_data_queue = self.cell_block_voltage
                logger.debug("Current response data: " + str(self.basic_information_and_status))
                if len(self.cell_block_voltage) >= data_length_of_response:
                    logger.debug("Got all the data, proceeding")
                    command_complete.set()
                else:
                    logger.debug("Response data not complete, waiting for more data to arrive")
            elif data_length_of_response != 0:
                logger.debug("Appending additional data")
                current_data_queue.extend(data[:-3])
                logger.debug("New length of data is now %s", len(self.basic_information_and_status))
                if len(current_data_queue) >= data_length_of_response:
                    logger.debug("Got all the data, proceeding")
                    command_complete.set()
            else:
                self.basic_information_and_status = None
                self.cell_block_voltage = None
                command_complete.set()

        self.basic_information_and_status = None
        self.cell_block_voltage = None
        if self.basic_information_and_status is None or self.cell_block_voltage is None:
            try:
                async with BleakClient(self.battery_address) as client:
                    await self.async_update_characteristics(client)
                    await client.start_notify(self.spp_data_characteristic, data_received)
                    while self.basic_information_and_status is None:
                        try:
                            command_complete.clear()
                            logger.debug("Sending command to fetch basic info and status from battery")
                            await client.write_gatt_char(self.spp_command_characteristic,
                                         bytearray([0xDD, 0xA5, 0x03, 0x00, 0xFF, 0xFD, 0x77]), response=False)
                            await asyncio.wait_for(command_complete.wait(), 1)
                        except Exception as e:
                            logger.error("Failed to receive result from battery to command request: %s", str(e))
                    while self.cell_block_voltage is None:
                        try:
                            command_complete.clear()
                            logger.debug("Sending command to fetch cell block info from battery")
                            await client.write_gatt_char(self.spp_command_characteristic,
                                                         bytearray([0xDD, 0xA5, 0x04, 0x00, 0xFF, 0xFC, 0x77]), response=False)
                            await asyncio.wait_for(command_complete.wait(), 1)
                        except Exception as e:
                            logger.error("Failed to receive result from battery to command request: %s", str(e))
                await client.disconnect()

            except Exception as e:
                logger.error("Failed to connect to battery: %s", str(e))
            except asyncio.exceptions.CancelledError as ce:
                logger.error("Failed to connect to battery: %s", str(ce))
        self.last_basic_info_update = time.time()

    def get_basic_info_and_status(self):
        asyncio.run(self.async_get_basic_info_and_status())

    def name(self) -> str:
        return self.battery_name

    def refresh_data(self):
        if self.basic_information_and_status is None or self.last_basic_info_update is None or \
                time.time() - self.last_basic_info_update >= 5:
            self.get_basic_info_and_status()

    def voltage(self) -> float:
        self.refresh_data()
        return float(int.from_bytes(self.basic_information_and_status[0:2], byteorder='big')) / 100

    def current(self) -> float:
        self.refresh_data()
        return float(int.from_bytes(self.basic_information_and_status[2:4], byteorder='big', signed=True)) / 100

    def residual_capacity(self) -> float:
        self.refresh_data()
        return float(int.from_bytes(self.basic_information_and_status[4:6], byteorder='big', signed=True)) / 100

    def nominal_capacity(self) -> float:
        self.refresh_data()
        return float(int.from_bytes(self.basic_information_and_status[6:8], byteorder='big', signed=True)) / 100

    def cycles(self) -> int:
        self.refresh_data()
        return int.from_bytes(self.basic_information_and_status[8:10], byteorder='big', signed=True)

    def balance_status(self, cell_number=0) -> bool:
        self.refresh_data()
        if cell_number <= 16:
            return int.from_bytes(self.basic_information_and_status[12:14], byteorder='big') & (1 << cell_number) == 1

        return int.from_bytes(self.basic_information_and_status[14:16], byteorder='big') & (1 << (cell_number - 16)) == 1

    def protection_status(self) -> [str]:
        self.refresh_data()
        status = []
        protect = int.from_bytes(self.basic_information_and_status[16:18], byteorder='big');
        if protect & 0x1:
            status.append('Cell Block Over-Vol')
        if protect & (1 << 1):
            status.append('Cell Bock Under-Vol')
        if protect & (1 << 2):
            status.append('Battery Over-Vol')
        if protect & (1 << 3):
            status.append('Battery Under-Vol')
        if protect & (1 << 4):
            status.append('Charging Over-Temp')
        if protect & (1 << 5):
            status.append('Charging Low-Temp')
        if protect & (1 << 6):
            status.append('Discharging Over-Temp')
        if protect & (1 << 7):
            status.append('Discharging Low-Temp')
        if protect & (1 << 8):
            status.append('Charging Over-Current')
        if protect & (1 << 9):
            status.append('Discharging Over-Current')
        if protect & (1 << 10):
            status.append('Short Circuit')
        if protect & (1 << 11):
            status.append('Fore-end IC Error')
        if protect & (1 << 12):
            status.append('MOS Software Lock-In')

        return status

    def version(self) -> str:
        self.refresh_data()
        return str((self.basic_information_and_status[18] & 0xF0) >> 4) + '.' + \
               str(self.basic_information_and_status[18] & 0x0F)

    def capacity_percent(self) -> int:
        self.refresh_data()
        return self.basic_information_and_status[19]

    def control_status(self) -> str:
        self.refresh_data()
        status = 'MOS OFF'

        if self.basic_information_and_status[20] & 1:
            status = 'Charging'
        elif self.basic_information_and_status[20] & (1 << 1):
            status = 'Discharging'

        return status

    def num_cells(self) -> int:
        self.refresh_data()
        return self.basic_information_and_status[21]

    def battery_temps_f(self) -> [float]:
        self.refresh_data()
        temps = []

        for i in range(self.basic_information_and_status[22]):
            temps.append((float(
                int.from_bytes(self.basic_information_and_status[23 + (i * 2):25 + (i * 2)], byteorder='big')) * 0.1)
                         * 1.8 - 459.67)

        return temps

    def cell_block_voltages(self) -> [float]:
        self.refresh_data()
        voltages = []
        for i in range(0, self.num_cells() * 2, 2):
            voltages.append(float(int.from_bytes(self.cell_block_voltage[i:i + 2], byteorder='big')) / 1000)

        return voltages

    def __str__(self):
        return f'{self.battery_name} SmartBattery'

    def __repr__(self):
        return f'Name: {self.battery_name}, Address: {self.battery_address}'
