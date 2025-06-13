import os
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

        if not device_port:
            logger("error", "No Coolleo device found.")
            raise RuntimeError("Coolleo device not detected")
        else:
            self.check_serial_port_permissions(device_port)
        
        logger("info", f"Device name: {device_name}. Device port {device_port}")



        return {
            "device_port": device_port,
            "device_name": device_name,
        }
    

    def check_serial_port_permissions(self, device_path):
        if not os.access(device_path, os.R_OK | os.W_OK):
            raise PermissionError(f"No tienes permisos para acceder a {device_path}. "
                                f"Prueba ejecutando el programa con sudo o añade tu usuario al grupo 'dialout'.")

