import serial
import time
import psutil
import subprocess

PORT = "/dev/ttyACM0"
BAUDRATE = 9600
BRILLO = 5
MODO = "ucpu"

def get_cpu_temp():
    try:
        output = subprocess.check_output(["sensors"]).decode()
        for line in output.splitlines():
            if "Package" in line or "Tdie" in line or "CPU" in line:
                parts = line.split()
                for part in parts:
                    if "°C" in part:
                        return int(float(part.replace("°C", "").replace("+", "")))
        return 40
    except:
        return 40

def get_cpu_usage():
    return int(psutil.cpu_percent(interval=0))

def get_cpu_watts():
    try:
        output = subprocess.check_output(["sensors"]).decode()
        for line in output.splitlines():
            if "PPT" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if "W" in part and i > 0:
                        # Extraemos el valor antes de la 'W'
                        return min(int(float(parts[i - 1])), 99)  # Máximo 99W mostrado en pantalla

        return 0  # Si no encuentra, asumimos 0W
    except:
        return 0

def build_packet(temp, ucpu, modo, brillo, cpu_watts):
    temp_hex = f"{temp:02X}"
    ucpu_hex = f"{ucpu:02X}"
    modo_byte = 0x40 if modo == "temperature" else 0x00
    brillo = min(brillo, 5)
    modo_brillo_hex = f"{modo_byte | brillo:02X}"
    cpu_watts_hex = f"{cpu_watts:02X} 00"  # Solo cambiamos el primer byte, como ya vimos
    print ("consumo en watts", cpu_watts_hex)
    packet = f"{temp_hex} {ucpu_hex} {modo_brillo_hex} 01 01 01 01 {cpu_watts_hex} 00 00 00 00"
    return bytes.fromhex(packet)

if __name__ == "__main__":
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            while True:
                # 1. Mostrar temperatura
                temp = get_cpu_temp()
                ucpu = get_cpu_usage()
                cpu_watts = get_cpu_watts()
                packet = build_packet(temp, ucpu, "temperature", BRILLO, cpu_watts)
                ser.write(packet)
                print(f"[Temp] {temp}°C, CPU: {ucpu}%, Watts: {cpu_watts}w → {packet.hex().upper()}")
                time.sleep(2)

                # 2. Mostrar UCPU
                temp = get_cpu_temp()
                ucpu = get_cpu_usage()
                cpu_watts = get_cpu_watts()
                packet = build_packet(temp, ucpu, "ucpu", BRILLO, cpu_watts)
                ser.write(packet)
                print(f"[UCPU] {temp}°C, CPU: {ucpu}%, Watts: {cpu_watts}w → {packet.hex().upper()}")
                time.sleep(2)
    except KeyboardInterrupt:
        print("Finalizando alternancia automática.")
