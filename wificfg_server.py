import logging
import sys
import time
from bgapi.bgmodule import BlueGigaServer
from bgapi.cmd_def import connection_status_mask

term = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
term.setFormatter(formatter)
api_logger = logging.getLogger("bgapi")
api_logger.addHandler(term)
api_logger.setLevel(level=logging.INFO)


class WifiCfgServer(BlueGigaServer):
    def __init__(self, port, baud, timeout):
        super(WifiCfgServer, self).__init__(port, baud, timeout)
        self.connected = False

    def ble_evt_connection_status(self, connection, flags, address, address_type, conn_interval, timeout, latency, bonding):
        super(WifiCfgServer, self).ble_evt_connection_status(connection, flags, address, address_type, conn_interval, timeout, latency, bonding)
        if flags & connection_status_mask["connection_connected"]:
            self.connected = True

    def ble_evt_connection_disconnected(self, connection, reason):
        super(WifiCfgServer, self).ble_evt_connection_disconnected(connection, reason)
        self.connected = False


def Main():
    cfg_server = WifiCfgServer(port="COM12", baud=115200, timeout=0.1)
    # BLE Device configuration and start advertising
    cfg_server.reset_ble_state()
    cfg_server.get_module_info()
    cfg_server.set_device_capabilities()
    cfg_server.delete_bonding()
    cfg_server.allow_bonding()
    cfg_server.advertise_general()

    while (1):
        if not cfg_server.connected:
            cfg_server.advertise_general()
            while not cfg_server.connected:
                time.sleep(3)
        else:
            time.sleep(3)

if __name__ == "__main__":
    Main()