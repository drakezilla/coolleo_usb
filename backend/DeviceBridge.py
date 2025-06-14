import serial
import atexit
import os
import socket

from utils.helper import logger
from config import coolleo

class DeviceBridge():
    def __init__(self, device_info):
        self.device_info = device_info
        atexit.register(self._cleanup_socket)

    def handle(self):
        self.uplink_server()
        self.uplink_port()
        return self

    def uplink_server(self):
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(coolleo.socket_path)
        self.server.listen()
        logger("info", f"Now listening {coolleo.socket_path}")

    def uplink_port(self):
        self.port = serial.Serial(
            self.device_info["device_port"],
            coolleo.baudrate,
            timeout=1
        )
        logger("info", f"{self.device_info['device_port']} opened at {coolleo.baudrate} rate")
            
    def _cleanup_socket(self):
        if (os.path.exists(coolleo.socket_path)):
            logger("info", f"Removing old {coolleo.socket_path}")
            os.remove(coolleo.socket_path)