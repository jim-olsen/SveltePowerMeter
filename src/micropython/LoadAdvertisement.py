class LoadAdvertisement:
    ADVERTISEMENT_FLAGS = [0x02, 0x01, 0x06]
    SERVICE_ID = [0xD2, 0xFC, 0x40, 0x22]

    def __init__(self, local_name):
        self.local_name_data = bytearray([len(local_name) + 1, 0x09])
        self.local_name_data.extend(bytes(local_name, "utf-8"))

    def advertise_data(self, data):
        packet = bytearray(self.ADVERTISEMENT_FLAGS)
        service_data = bytearray([len(data) + len(self.SERVICE_ID) + 1, 0x16])
        service_data.extend(bytearray(self.SERVICE_ID))
        service_data.extend(bytearray(data, "utf-8"))
        packet.extend(service_data)
        packet.extend(self.local_name_data)
        print("Total packet length: " + str(len(packet)))

        return packet
