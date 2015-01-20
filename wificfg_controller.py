import time
from bgapi.bgmodule import BlueGigaClient, GATTService, GATTCharacteristic
from wificfg_server import UUIDS

def Main():
    cfg_client = BlueGigaClient(port="COM9", baud=115200, timeout=0.1)
    cfg_client.pipe_logs_to_terminal()
    # BLE Device configuration and start advertising
    cfg_client.reset_ble_state()
    resp = cfg_client.scan_all(timeout=4)
    connection = cfg_client.connect(resp[0])
    connection.read_by_group_type(GATTService.PRIMARY_SERVICE_UUID)
    for service in connection.get_services():
        connection.find_information(service=service)
        connection.read_by_type(service=service, type=GATTCharacteristic.CHARACTERISTIC_UUID)
        connection.read_by_type(service=service, type=GATTCharacteristic.CLIENT_CHARACTERISTIC_CONFIG)
        #connection.read_by_type(service=service, type=GATTCharacteristic.USER_DESCRIPTION)

    app_handles = {}
    for key, value in UUIDS.iteritems():
        app_handles[key] = connection.get_handles_by_uuid(value)[0]

    for characteristic in connection.get_characteristics():
        if characteristic.has_indicate():
            connection.characteristic_subscription(characteristic=characteristic, indicate=True, notify=False)

    connection.write_by_handle(app_handles["SSID"], "Some SSID", timeout=1)
    connection.write_by_handle(app_handles["PSK"], "Some PSK", timeout=1)
    connection.write_by_handle(app_handles["USERNAME"], "Some Username", timeout=1)
    connection.write_by_handle(app_handles["PASSWORD"], "Some Passowrd", timeout=1)
    connection.write_by_handle(app_handles["ACTIONS"], "\x00\x01", timeout=1)
    time.sleep(3)
    cfg_client.disconnect(connection)

    time.sleep(1)


if __name__ == "__main__":
    Main()