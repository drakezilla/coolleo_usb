from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


default_mode = os.getenv("DEFAULT_MODE", "temperature")
default_brightness = os.getenv("DEFAULT_BRIGHTNESS", 5)
default_baudrate = os.getenv("DEFAULT_BAUDRATE", 9600)
default_refresh_interval = int(os.getenv("DEFAULT_REFRESH_INTERVAL", 2))
