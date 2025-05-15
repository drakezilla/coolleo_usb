import os
import subprocess
import time
import socket
from config_manager import ConfigManager

class BackendManager:
    SOCKET_PATH = "/tmp/coolleo_socket"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_PATH = os.path.abspath(os.path.join(BASE_DIR, "../backend/coolleo_backend.py"))

    def __init__(self):
        self.config_manager = ConfigManager()

    def is_backend_running(self):
        """Comprueba si el socket existe y si realmente responde a conexiones."""
        if not os.path.exists(self.SOCKET_PATH):
            return False

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(1)
                client.connect(self.SOCKET_PATH)
                print("DEBUG: Successfully connected to backend socket.")
                return True  # Conexión exitosa, backend está activo
        except Exception:
            # Socket existe pero está muerto, lo eliminamos
            try:
                os.remove(self.SOCKET_PATH)
                print("DEBUG: Found stale socket, removed.")
            except Exception as e:
                print(f"DEBUG: Failed to remove stale socket: {e}")
            return False

    def wait_for_backend(self, retries=10, delay=1):
        """Espera a que el backend cree el socket y responda."""
        for attempt in range(retries):
            if self.is_backend_running():
                print(f"DEBUG: Backend socket available after {attempt + 1} attempts.")
                return True
            print(f"DEBUG: Backend socket not ready, retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
        return False

    def start_backend(self):
        port = self.config_manager.get_serial_port()
        if not port:
            print("No serial port configured. Please set it in the configuration first.")
            return

        verbose_flag = "--verbose" if self.config_manager.is_verbose_enabled() else ""
        command = f"./env/bin/python3 {self.BACKEND_PATH} {port} {verbose_flag}".strip()

        print(f"DEBUG: Launching backend with command: {command}")

        try:
            subprocess.Popen(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("DEBUG: Backend launch command executed.")

            if self.wait_for_backend():
                print("DEBUG: Backend is now running and socket is responding.")
            else:
                print("WARNING: Backend did not start in expected time.")
        except Exception as e:
            print(f"Failed to start backend: {e}")
