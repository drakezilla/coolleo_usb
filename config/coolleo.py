import sys
from pathlib import Path
from dotenv import load_dotenv
import os

if getattr(sys, 'frozen', False):
    root_path = Path(sys._MEIPASS)
else:
    root_path = Path(__file__).parent.parent
env_path = root_path / ".env"
resource_path = root_path / "resources/"

load_dotenv(dotenv_path=env_path)

mode = os.getenv("DEFAULT_MODE", "temperature")
brightness = os.getenv("DEFAULT_BRIGHTNESS", 5)
baudrate = os.getenv("DEFAULT_BAUDRATE", 9600)
refresh_interval = int(os.getenv("DEFAULT_REFRESH_INTERVAL", 2))
socket_path = os.getenv("DEFAULT_SOCKET_PATH", "/tmp/coolleo_socket")
show_device_communication = os.getenv("SHOW_DEVICE_COMM", "False").lower() in ("1", "true", "yes")