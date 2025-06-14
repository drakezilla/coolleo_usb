from config import coolleo
from core.DeviceCommunication import DeviceCommunication

class DeviceController():
    def __init__(self, serial_port):
        self._dc = DeviceCommunication()
        self._serial_port = serial_port
        self._current_mode = coolleo.mode
        self._current_brightness = coolleo.brightness
        self._alternate_toggle = False

    def set_mode(self, mode):
        self._current_mode = mode
        self.handle()
    
    def set_brightness(self, brightness):
        self._current_brightness = brightness
        self.handle()

    def handle(self):
        if self._current_mode == "alternate":
            mode = "temperature" if self._alternate_toggle else "cpu_usage"
            self._alternate_toggle = not self._alternate_toggle
        else:
            mode = self._current_mode
        self._dc.handle(mode, self._current_brightness, self._serial_port)