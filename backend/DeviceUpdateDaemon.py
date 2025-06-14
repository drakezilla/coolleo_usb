
import threading
import time
from config import coolleo
from utils.helper import logger


class DeviceUpdateDaemon(threading.Thread):
    def __init__(self, device_controller):
        super().__init__(daemon=True)
        self.controller = device_controller
        self.interval = coolleo.refresh_interval
        self._running = True

    def run(self):
        logger("info", "Starting device daemon")
        while self._running:
            try:
                self.controller.handle()
                time.sleep(self.interval)
            except Exception as ex:
                logger("error", f"yikes... {ex.with_traceback()}")
                self._running = False

    def stop(self):
        self._running = False

