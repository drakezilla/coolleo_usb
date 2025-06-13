from core.SystemMetrics import SystemMetrics

class CommandParser:
    def __init__(self, device_controller):
        self.metrics = SystemMetrics()
        self.device_controller = device_controller

    def handle(self, cmd: str) -> str:
        if cmd.startswith("SET_MODE"):
            _, mode = cmd.split()
            self.device_controller.set_mode(mode)
            return f"OK. Modo cambiado a {mode}\n"

        elif cmd.startswith("SET_BRIGHTNESS"):
            _, level = cmd.split()
            self.device_controller.set_brightness(int(level))
            return f"OK. Brillo cambiado a {level}\n"

        elif cmd == "GET_STATUS":
            temp = self.metrics.get_cpu_temp()
            ucpu = self.metrics.get_cpu_usage()
            watts = self.metrics.get_cpu_watts()
            return f"TEMP:{temp};UCPU:{ucpu};WATTS:{watts}\n"

        return "ERROR. Comando no reconocido.\n"