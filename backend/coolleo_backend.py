import socket
import threading
import time
import serial
import subprocess
import psutil
import logging
import sys
import os

SOCKET_PATH = "/tmp/coolleo_socket"
BAUDRATE = 9600

if len(sys.argv) > 1:
    PORT = sys.argv[1]

print(f"Using serial port: {PORT}")  # Debug opcional para confirmar

current_mode = "temperature"
current_brightness = 5
refresh_interval = 2  # Segundos

# --- Logger Setup ---
def setup_logger(verbose=False):
    logger = logging.getLogger("coolleo_backend")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    return logger

verbose_mode = "--verbose" in sys.argv
logger = setup_logger(verbose_mode)

def get_cpu_temp():
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
        logger.warning(f"Error al obtener temperatura: {e}")
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
                        return min(int(float(parts[i - 1])), 99)
        return 0
    except Exception as e:
        logger.warning(f"Error al obtener consumo: {e}")
        return 0

def send_packet_to_device(mode, brightness, ser):
    temp = get_cpu_temp()
    ucpu = get_cpu_usage()
    cpu_watts = get_cpu_watts()

    temp_hex = f"{temp:02X}"
    ucpu_hex = f"{ucpu:02X}"
    modo_byte = 0x40 if mode == "temperature" else 0x00
    modo_brillo_hex = f"{modo_byte | brightness:02X}"
    cpu_watts_hex = f"{cpu_watts:02X} 00"
    packet = f"{temp_hex} {ucpu_hex} {modo_brillo_hex} 01 01 01 01 {cpu_watts_hex} 00 00 00 00"
    packet_bytes = bytes.fromhex(packet)

    ser.write(packet_bytes)
    logger.debug(f"Enviado al disipador: {packet.upper()}")

def auto_refresh(ser):
    alt_state = "temperature"
    while True:
        mode_to_use = current_mode
        if current_mode == "alternate":
            mode_to_use = alt_state
            alt_state = "ucpu" if alt_state == "temperature" else "temperature"

        send_packet_to_device(mode_to_use, current_brightness, ser)
        time.sleep(refresh_interval)

def handle_client(conn, ser):
    global current_mode, current_brightness
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            cmd = data.decode().strip()
            logger.debug(f"Comando recibido: {cmd}")

            if cmd.startswith("SET_MODE"):
                _, mode = cmd.split()
                current_mode = mode
                send_packet_to_device(current_mode, current_brightness, ser)
                conn.sendall(f"OK. Modo cambiado a {mode}\n".encode())
            elif cmd.startswith("SET_BRIGHTNESS"):
                _, level = cmd.split()
                current_brightness = int(level)
                send_packet_to_device(current_mode, current_brightness, ser)
                conn.sendall(f"OK. Brillo cambiado a {level}\n".encode())
            elif cmd.startswith("GET_STATUS"):
                temp = get_cpu_temp()
                ucpu = get_cpu_usage()
                watts = get_cpu_watts()
                status = f"TEMP:{temp};UCPU:{ucpu};WATTS:{watts}"
                conn.sendall(f"{status}\n".encode())
            else:
                conn.sendall(b"ERROR. Comando no reconocido.\n")

def socket_server(ser):
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(SOCKET_PATH)
        server.listen()
        logger.info(f"Servidor de control escuchando en {SOCKET_PATH}")

        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(conn, ser)).start()

if __name__ == "__main__":
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            refresh_thread = threading.Thread(target=auto_refresh, args=(ser,), daemon=True)
            refresh_thread.start()
            socket_server(ser)
    except KeyboardInterrupt:
        logger.warning("Backend finalizado por el usuario.")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
    finally:
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
