import socket
import time
import os
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QSlider, QHBoxLayout
)
from PyQt6.QtGui import QIcon

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.abspath(os.path.join(BASE_DIR, "../resources/icon/coolleo_dashboard.svg"))

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Coolleo Dashboard")
        self.setFixedSize(600, 400)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        else:
            print("WARNING: Icon file not found for window.")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)

        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground((25, 25, 25))
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.addLegend()
        self.plot_widget.getAxis('bottom').setTicks([])
        self.update_graph_labels()
        main_layout.addWidget(self.plot_widget)

        # Mode controls
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel("Mode:")
        self.mode_label.setStyleSheet("font-size: 14px; padding-right: 10px;")

        self.temp_button = QPushButton("Temperature")
        self.temp_button.clicked.connect(lambda: self.send_command("SET_MODE temperature"))

        self.ucpu_button = QPushButton("CPU Usage")
        self.ucpu_button.clicked.connect(lambda: self.send_command("SET_MODE ucpu"))

        self.alternate_button = QPushButton("Temp/CPU Usage")
        self.alternate_button.clicked.connect(lambda: self.send_command("SET_MODE alternate"))

        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.temp_button)
        mode_layout.addWidget(self.ucpu_button)
        mode_layout.addWidget(self.alternate_button)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        # Brightness slider
        brightness_layout = QHBoxLayout()
        self.brightness_label = QLabel("Brightness:")
        self.brightness_label.setStyleSheet("font-size: 14px; padding-right: 10px;")

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(1)
        self.brightness_slider.setMaximum(5)
        self.brightness_slider.setValue(5)
        self.brightness_slider.setFixedWidth(200)
        self.brightness_slider.sliderReleased.connect(self.apply_brightness)

        brightness_layout.addWidget(self.brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addStretch()
        main_layout.addLayout(brightness_layout)

        self.setLayout(main_layout)

        # Data and timer
        self.temp_data, self.ucpu_data, self.watts_data, self.time_data = [], [], [], []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(2000)

    def send_command(self, command):
        SOCKET_PATH = "/tmp/coolleo_socket"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(SOCKET_PATH)
                client.sendall(command.encode())
                response = client.recv(1024)
                print(response.decode())
        except Exception as e:
            print(f"Error: {e}")

    def apply_brightness(self):
        value = self.brightness_slider.value()
        self.send_command(f"SET_BRIGHTNESS {value}")

    def update_graph(self):
        SOCKET_PATH = "/tmp/coolleo_socket"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(SOCKET_PATH)
                client.sendall(b"GET_STATUS")
                response = client.recv(1024).decode().strip()
                data = dict(item.split(":") for item in response.split(";"))
                temp = int(data.get("TEMP", 40))
                ucpu = int(data.get("UCPU", 10))
                watts = int(data.get("WATTS", 20))
        except Exception as e:
            print(f"Error: {e}")
            temp, ucpu, watts = 40, 10, 20

        if len(self.time_data) > 50:
            self.time_data.pop(0)
            self.temp_data.pop(0)
            self.ucpu_data.pop(0)
            self.watts_data.pop(0)

        self.time_data.append(len(self.time_data))
        self.temp_data.append(temp)
        self.ucpu_data.append(ucpu)
        self.watts_data.append(watts)

        self.plot_widget.clear()
        self.plot_widget.setTitle("Temperature, CPU Usage, and Power consumption")

        self.temp_curve = self.plot_widget.plot(
            self.time_data, self.temp_data, pen=pg.mkPen(color='#FF6666', width=2),
            name=f"Temp (°C): {temp}"
        )
        self.ucpu_curve = self.plot_widget.plot(
            self.time_data, self.ucpu_data, pen=pg.mkPen(color='#66FF66', width=2),
            name=f"CPU Usage (%): {ucpu}"
        )
        self.watts_curve = self.plot_widget.plot(
            self.time_data, self.watts_data, pen=pg.mkPen(color='#6699FF', width=2),
            name=f"Power (W): {watts:03}"
        )
        self.plot_widget.getAxis('bottom').setTicks([])

    def update_graph_labels(self):
        self.plot_widget.setTitle("Temperature, CPU Usage, and Power consumption")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
