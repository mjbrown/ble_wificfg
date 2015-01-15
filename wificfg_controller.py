import logging
import sys
import time
from bgapi.bgmodule import BlueGigaClient, GATTService, GATTCharacteristic

term = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
term.setFormatter(formatter)
api_logger = logging.getLogger("bgapi")
api_logger.addHandler(term)
api_logger.setLevel(level=logging.INFO)

SSID_UUID = "\x00\x01\x00\x00\x00\x00\xF0\x00\xF0\x00\xF0\x00\x00\x00\x00\x00"[::-1]
PSK_UUID = "\x00\x02\x00\x00\x00\x00\xF0\x00\xF0\x00\xF0\x00\x00\x00\x00\x00"[::-1]
INTERFACE_UUID = "\x00\x03\x00\x00\x00\x00\xF0\x00\xF0\x00\xF0\x00\x00\x00\x00\x00"[::-1]
IPADDRESS_UUID = "\x00\x04\x00\x00\x00\x00\xF0\x00\xF0\x00\xF0\x00\x00\x00\x00\x00"[::-1]

def Main():
    cfg_client = BlueGigaClient(port="COM9", baud=115200, timeout=0.1)
    # BLE Device configuration and start advertising
    cfg_client.reset_ble_state()
    resp = cfg_client.scan_all(timeout=4)
    connection = cfg_client.connect(resp[0])
    connection.read_by_group_type(GATTService.PRIMARY_SERVICE_UUID)
    for service in connection.get_services():
        connection.find_information(service=service)
        connection.read_by_type(service=service, type=GATTCharacteristic.CHARACTERISTIC_UUID)
        connection.read_by_type(service=service, type=GATTCharacteristic.CLIENT_CHARACTERISTIC_CONFIG)
        connection.read_by_type(service=service, type=GATTCharacteristic.USER_DESCRIPTION)

    for characteristic in connection.get_characteristics():
        if characteristic.is_readable():
            connection.read_by_handle(characteristic.value_handle)
        if characteristic.has_indicate():
            connection.characteristic_subscription(characteristic=characteristic, indicate=True, notify=False)

    for characteristic in connection.get_characteristics():
        description = characteristic.get_descriptor_by_uuid(GATTCharacteristic.USER_DESCRIPTION)
        if description:
            print "%s - Handle:%d - Current Value:%s" % (description.value, characteristic.handle, characteristic.value)

    cfg_client.disconnect(connection)

    time.sleep(1)


if __name__ == "__main__":
    Main()