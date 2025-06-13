import threading

from backend.DeviceBridge import DeviceBridge

from backend.DeviceController import DeviceController
from backend.ClientHandler import ClientHandler
from backend.DeviceUpdateDaemon import DeviceUpdateDaemon
from utils.helper import logger

def main():
    device = DeviceBridge().handle()
    device_controller = DeviceController(device.port)

    update_daemon = DeviceUpdateDaemon(device_controller)
    update_daemon.start()
    
    while True:
        conn, _ = device.server.accept()
        threading.Thread(
            target=ClientHandler(conn, device_controller).handle
        ).start()

if __name__ == "__main__":
    main()