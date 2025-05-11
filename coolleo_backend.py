import socket
import threading
import time
import serial
import subprocess
import psutil

SOCKET_PATH = "/tmp/coolleo_socket"
PORT = "/dev/ttyACM0"
BAUDRATE = 9600

current_mode = "temperature"
current_brightness = 5
refresh_interval = 2  # Segundos

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
                        return min(int(float(parts[i - 1])), 99)
        return 0
    except:
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
    print(f"Enviado al disipador: {packet.upper()}")


def auto_refresh(ser):
    alt_state = "temperature"  # Estado actual de la alternancia

    while True:
        mode_to_use = current_mode
        if current_mode == "alternate":
            mode_to_use = alt_state
            # Cambiar para la siguiente iteración
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
            print(f"Comando recibido: {cmd}")

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

def socket_server():
    try:
        import os
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(SOCKET_PATH)
            server.listen()
            print(f"Servidor de control escuchando en {SOCKET_PATH}")

            while True:
                conn, _ = server.accept()
                threading.Thread(target=handle_client, args=(conn,ser)).start()
    except KeyboardInterrupt:
        print("Backend finalizado.")

if __name__ == "__main__":
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        refresh_thread = threading.Thread(target=auto_refresh, args=(ser,), daemon=True)
        refresh_thread.start()

        socket_server()  # Aquí también deberías pasar `ser` a las funciones que lo necesiten
