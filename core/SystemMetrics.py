import subprocess
import psutil
from utils.helper import logger

class SystemMetrics():

    def get_cpu_temp(self):
        try:
            output = subprocess.check_output(["sensors"]).decode()
            for line in output.splitlines():
                if "Tctl" in line:
                    parts = line.split()
                    for part in parts:
                        if "°C" in part:
                            return int(float(part.replace("°C", "").replace("+", "")))
            return 40
        except Exception as e:      
            logger("warning", f"Error al obtener temperatura: {e}")
            return 40
        
    def get_cpu_usage(self):
        return int(psutil.cpu_percent(interval=0))

    def get_cpu_watts(self):
        try:
            output = subprocess.check_output(["sensors"]).decode()
            for line in output.splitlines():
                if "PPT" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "W" in part and i > 0:
                            return min(int(float(parts[i - 1])), 99)
            return 0
        except Exception as e:
            logger("warning", f"Error al obtener consumo: {e}")
            return 0