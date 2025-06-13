import os
import sys
from backend.DeviceDetection import DeviceDetection
from backend.DeviceBridge import DeviceBridge
from backend.DeviceController import DeviceController
from backend.DeviceUpdateDaemon import DeviceUpdateDaemon

class Bootloader:
    def __init__(self):
        self.device_info = None
        self.bridge = None
        self.controller = None
        self.daemon = None

    def start(self):
        self.device_info = DeviceDetection().handle()
        self.verify_device_ready()
        self.bridge = DeviceBridge(self.device_info).handle()
        self.controller = DeviceController(self.bridge.port)
        self.daemon = DeviceUpdateDaemon(self.controller)
        self.daemon.start()
        return self
    
    def verify_device_ready(self):
        device_port = self.device_info['device_port']

        if not device_port:
            sys.exit("[ERROR]: No Coolleo device found.")
            return False

        if not os.access(device_port, os.R_OK | os.W_OK):
            sys.exit(
                f"[ERROR]: Not enough permissions over {device_port}.\n"
                f"[INFO]: Execute sudo usermod -a -G dialout $USER and reboot\n"
            )
        
