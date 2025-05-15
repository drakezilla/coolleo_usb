import glob
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
)
from config_manager import ConfigManager

class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Serial Port Configuration"))
        self.setFixedSize(500, 200)
        self.config_manager = ConfigManager()

        layout = QVBoxLayout()

        label = QLabel(self.tr("Select the serial port where the cooler is connected:"))
        layout.addWidget(label)

        self.port_selector = QComboBox()
        self.populate_ports()
        layout.addWidget(self.port_selector)

        button_layout = QHBoxLayout()
        save_button = QPushButton(self.tr("Save"))
        save_button.clicked.connect(self.save_selection)

        cancel_button = QPushButton(self.tr("Cancel"))
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_ports(self):
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        port_descriptions = self.get_lsusb_info()

        if not ports:
            self.port_selector.addItem(self.tr("No devices found"))
            self.port_selector.setEnabled(False)
        else:
            for port in ports:
                desc = port_descriptions.get(port, self.tr("Unknown device"))
                self.port_selector.addItem(f"{port} - {desc}", port)

            current_port = self.config_manager.get_serial_port()
            if current_port:
                index = self.port_selector.findData(current_port)
                if index != -1:
                    self.port_selector.setCurrentIndex(index)

    def get_lsusb_info(self):
        port_info = {}
        try:
            for dev_path in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
                try:
                    udev_info = subprocess.check_output(
                        ["udevadm", "info", "-q", "property", "-n", dev_path]
                    ).decode()

                    vendor, model = None, None
                    for line in udev_info.splitlines():
                        if line.startswith("ID_MODEL="):
                            model = line.split("=")[1]
                        if line.startswith("ID_VENDOR="):
                            vendor = line.split("=")[1]
                    desc = f"{vendor} {model}" if vendor and model else self.tr("USB Device")
                    port_info[dev_path] = desc
                except:
                    port_info[dev_path] = self.tr("USB Device")
        except:
            pass

        return port_info

    def save_selection(self):
        selected_port = self.port_selector.currentData()
        if selected_port:
            self.config_manager.set_serial_port(selected_port)
        self.accept()
