import json
import os

class ConfigManager:
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_serial_port(self):
        return self.config.get("serial_port")

    def set_serial_port(self, port):
        self.config["serial_port"] = port
        self.save_config()

    def is_verbose_enabled(self):
        return self.config.get("verbose", False)

    def set_verbose(self, verbose):
        self.config["verbose"] = verbose
        self.save_config()
