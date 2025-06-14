import os
import sys
import subprocess

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
        self._check_lm_sensors_installed()
        self._verify_device_ready()
        self.bridge = DeviceBridge(self.device_info).handle()
        self.controller = DeviceController(self.bridge.port)
        self.daemon = DeviceUpdateDaemon(self.controller)
        self.daemon.start()
        return self
    
    def _verify_device_ready(self):
        device_port = self.device_info['device_port']

        if not device_port:
            sys.exit("[ERROR]: No Coolleo device found.")

        if not os.access(device_port, os.R_OK | os.W_OK):
            sys.exit(
                f"[ERROR]: Not enough permissions over {device_port}.\n"
                f"[INFO]: Execute sudo usermod -a -G dialout $USER and reboot\n"
            )

    def _check_lm_sensors_installed(self):
        try:
            subprocess.run(["sensors"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            sys.exit(
                "[ERROR]: 'lm-sensors' no está instalado o no funciona correctamente.\n"
                "[INFO]: Ubuntu/Debian: sudo apt install lm-sensors\n"
                "[INFO]: Fedora: sudo dnf install lm_sensors\n"
            )
