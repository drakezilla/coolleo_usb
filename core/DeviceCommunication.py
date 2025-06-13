from utils.helper import logger
from core.SystemMetrics import SystemMetrics


class DeviceCommunication():
    def __init__(self):
        self.metrics = SystemMetrics()

    def handle(self, mode, brightness, server_socket):
        temp = self.metrics.get_cpu_temp()
        ucpu = self.metrics.get_cpu_usage()
        cpu_watts = self.metrics.get_cpu_watts()

        temp_hex = f"{temp:02X}"
        ucpu_hex = f"{ucpu:02X}"
        modo_byte = 0x40 if mode == "temperature" else 0x00
        modo_brillo_hex = f"{modo_byte | int(brightness):02X}"
        cpu_watts_hex = f"{cpu_watts:02X} 00"
        packet = f"{temp_hex} {ucpu_hex} {modo_brillo_hex} 01 01 01 01 {cpu_watts_hex} 00 00 00 00"
        packet_bytes = bytes.fromhex(packet)

        server_socket.write(packet_bytes)
        logger("debug", f"Enviado al disipador: {packet.upper()}")