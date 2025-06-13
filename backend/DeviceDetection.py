import serial.tools.list_ports

from utils.helper import logger

COOLLEO_NAME_PREFIX = "CH5"

class DeviceDetection():
    
    def handle(self):

        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if COOLLEO_NAME_PREFIX in port.description:
                device_port = port.device
                device_name = port.description
                break
            
        return {
            "device_port": device_port,
            "device_name": device_name,
        }
