import serial
import atexit
import os
import socket

from utils.helper import logger
from backend.DeviceDetection import DeviceDetection
from config import coolleo

class DeviceBridge():
    _socket_path = "/tmp/coolleo_socket"
    def __init__(self):
        atexit.register(self._cleanup_socket)

    def handle(self):
        self.uplink_server()
        self.uplink_port()
        return self

    def uplink_server(self):
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self._socket_path)
        self.server.listen()
        logger("info", f"Now listening {self._socket_path}")

    def uplink_port(self):
        device_info = DeviceDetection().handle()
        self.port = serial.Serial(
            device_info["device_port"],
            coolleo.default_baudrate,
            timeout=1
        )
        logger("info", f"{device_info['device_port']} opened at {coolleo.default_baudrate} rate")
            
    def _cleanup_socket(self):
        if (os.path.exists(self._socket_path)):
            logger("info", f"Removing old {self._socket_path}")
            os.remove(self._socket_path)