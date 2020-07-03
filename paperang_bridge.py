# Use bluetooth BLE 4.0 slave module to redirect data from a Paperang host (serial) to 
# Paperang device (BT) and vice versa.

import serial
import serial.threaded
from logger import Logger as Logger
import atexit
import signal
from bluetooth import BluetoothSocket, find_service, RFCOMM, discover_devices, BluetoothError
# pyserial tools
# python -m serial.tools.list_ports
# python -m serial.tools.miniterm <port_name>

COM_PORT= 'COM10'
BAUD = 9600
PAPERANG_ADDR = "fc:58:fa:1e:26:63"
UUID = "00001101-0000-1000-8000-00805F9B34FB"
MAX_RECV_LEN = 1024


class SerialToBt(serial.threaded.Protocol):
    """serial->BT socket"""

    def __init__(self, logging):
        self.socket = None
        self.logging = logging

    def __call__(self):
        return self

    def data_received(self, data):
        if self.socket is not None:
            self.logging.debug('Host2Device: {}'.format(data.hex()))
            # self.socket.sendall(data)
            len = 0
            while True:
                len = self.socket.send(data[len:])
                if not len:
                    break

class Bridge:
    serial_worker = None
    ser_to_bt = None
    intentional_exit = False

    def __init__(self, log, port=COM_PORT, baud=BAUD, address=PAPERANG_ADDR, 
                uuid=UUID):
        self.host_port = COM_PORT
        self.address = address
        self.uuid = uuid
        self.host = serial.Serial(None, baud, timeout=0)
        self.logging = log.logger

    def connect_host(self):
        try:
            self.host.port = self.host_port
            self.host.open()
        except serial.SerialException as e:
            self.logging.error(
                'Could not open serial port {}: {}\n'.format(self.host_port, e))
            return False
        self.logging.info("Host connected.")
        return True

    def disconnect_host(self):
        self.host.close()
        self.logging.info("Host disconnected.")

    def scanservices(self):
        self.logging.info("Searching for services...")
        service_matches = find_service(uuid=self.uuid, address=self.address)
        valid_service = list(filter(
            lambda s: 'protocol' in s and 'name' in s and s[
                'protocol'] == 'RFCOMM' and s['name'] == b'Port\x00',
            service_matches
        ))
        if len(valid_service) == 0:
            self.logging.error("Cannot find valid services on device with MAC %s." % self.address)
            return False
        self.logging.info("Found a valid service on target device.")
        self.service = valid_service[0]
        return True

    def connect_device(self):
        if not self.scanservices():
            self.logging.error('Not found valid service.')
            return False
        self.logging.info("Service found. Connecting to \"%s\" on %s..." %
                     (self.service["name"], self.service["host"]))
        self.sock = BluetoothSocket(RFCOMM)
        self.sock.connect((self.service["host"], self.service["port"]))
        self.sock.settimeout(60)
        self.logging.info("Device connected.")

        return True

    def disconnect_device(self):
        try:
            self.sock.close()
        except:
            pass
        self.logging.info("Device disconnected.")

    def redirect_Serial2Bt_thread(self):
        # start thread to handle redirect host data to device
        self.ser_to_bt = SerialToBt(self.logging)
        self.ser_to_bt.socket = self.sock
        self.serial_worker = serial.threaded.ReaderThread(self.host, self.ser_to_bt)
        self.serial_worker.start()
        self.logging.info("Start to redirect host data to device ...")

    def redirect_Bt2Serial(self):
        self.logging.info("Start to redirect device data to host ...")
        device_socket = self.sock
        self.intentional_exit = False
        try:
            # enter network <-> serial loop
            while not self.intentional_exit:
                try:
                    data = device_socket.recv(MAX_RECV_LEN)
                    if not data:
                        break
                    # get a bunch of bytes and send them
                    self.host.write(data)
                except BluetoothError as msg:
                    self.logging.error('ERROR: {}\n'.format(msg))
                    # probably got disconnected
                    break
        except KeyboardInterrupt:
            self.intentional_exit = True
            raise

    def enable(self):
        self.connect_host()
        if not self.connect_device():
            return
        self.redirect_Serial2Bt_thread()
        self.redirect_Bt2Serial()

    def disable(self):
        self.intentional_exit = True
        self.ser_to_bt.socket = None
        self.disconnect_host()
        self.serial_worker.stop()
        self.disconnect_device()



if __name__ == "__main__":
    log = Logger('Paperang.log', level='debug')

    bridge = Bridge(log)
    bridge.enable()
