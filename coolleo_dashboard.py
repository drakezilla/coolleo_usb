import sys
import socket
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer, QTranslator
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget, QLabel,
    QVBoxLayout, QPushButton, QSlider, QHBoxLayout
)
from PyQt6.QtGui import QIcon, QAction

translator = QTranslator()
current_tray = None  # Referencia global al systray

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.tr("Coolleo Dashboard"))
        self.setFixedSize(600, 400)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)

        # Gráfico
        self.plot_widget = pg.PlotWidget(title=self.tr("Temperatura, UCPU y Watts"))
        self.plot_widget.setBackground((25, 25, 25))
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.addLegend()
        self.plot_widget.getAxis('bottom').setTicks([])

        self.temp_curve = self.plot_widget.plot(pen=pg.mkPen(color='#FF6666', width=2))
        self.ucpu_curve = self.plot_widget.plot(pen=pg.mkPen(color='#66FF66', width=2))
        self.watts_curve = self.plot_widget.plot(pen=pg.mkPen(color='#6699FF', width=2))

        main_layout.addWidget(self.plot_widget)

        # Modo Controls
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel(self.tr("Modo:"))
        self.mode_label.setStyleSheet("font-size: 14px; padding-right: 10px;")

        self.temp_button = QPushButton(self.tr("Mostrar Temperatura"))
        self.temp_button.clicked.connect(lambda: self.send_command("SET_MODE temperature"))

        self.ucpu_button = QPushButton(self.tr("Mostrar UCPU"))
        self.ucpu_button.clicked.connect(lambda: self.send_command("SET_MODE ucpu"))

        self.alternate_button = QPushButton(self.tr("Alternar Temp/UCPU"))
        self.alternate_button.clicked.connect(lambda: self.send_command("SET_MODE alternate"))

        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.temp_button)
        mode_layout.addWidget(self.ucpu_button)
        mode_layout.addWidget(self.alternate_button)
        mode_layout.addStretch()

        main_layout.addLayout(mode_layout)

        # Brillo Slider
        brightness_layout = QHBoxLayout()
        self.brightness_label = QLabel(self.tr("Brillo:"))
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

        # Timer para el gráfico
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
        self.temp_curve = self.plot_widget.plot(
            self.time_data, self.temp_data, pen=pg.mkPen(color='#FF6666', width=2),
            name=f"Temp (°C): {temp}"
        )
        self.ucpu_curve = self.plot_widget.plot(
            self.time_data, self.ucpu_data, pen=pg.mkPen(color='#66FF66', width=2),
            name=f"UCPU (%): {ucpu}"
        )
        self.watts_curve = self.plot_widget.plot(
            self.time_data, self.watts_data, pen=pg.mkPen(color='#6699FF', width=2),
            name=f"Consumption (W): {watts:03}"
        )
        self.plot_widget.getAxis('bottom').setTicks([])

    def update_ui_texts(self):
        self.setWindowTitle(self.tr("Coolleo Dashboard"))
        self.mode_label.setText(self.tr("Modo:"))
        self.temp_button.setText(self.tr("Mostrar Temperatura"))
        self.ucpu_button.setText(self.tr("Mostrar UCPU"))
        self.alternate_button.setText(self.tr("Alternar Temp/UCPU"))
        self.brightness_label.setText(self.tr("Brillo:"))

def set_language(app, language_code, dashboard_window):
    global current_tray

    if language_code == "es":
        translator.load("i18n/ES_es.qm")
    elif language_code == "en":
        translator.load("i18n/EN_en.qm")
    app.installTranslator(translator)

    if current_tray:
        current_tray.hide()
        current_tray.deleteLater()

    # Crear nuevo systray y asignar a la variable global
    current_tray = QSystemTrayIcon()
    current_tray.setIcon(QIcon.fromTheme("preferences-system"))
    current_tray.setVisible(True)

    # Crear nuevo menú
    new_menu = QMenu()

    action_show = QAction(app.translate("SysTray", "Mostrar Panel"))
    action_show.triggered.connect(dashboard_window.show)
    new_menu.addAction(action_show)

    language_menu = QMenu(app.translate("SysTray", "Idioma"))

    english_action = QAction(app.translate("SysTray", "Inglés"))
    english_action.triggered.connect(lambda: set_language(app, "en", dashboard_window))
    language_menu.addAction(english_action)

    spanish_action = QAction(app.translate("SysTray", "Español"))
    spanish_action.triggered.connect(lambda: set_language(app, "es", dashboard_window))
    language_menu.addAction(spanish_action)

    new_menu.addMenu(language_menu)

    exit_action = QAction(app.translate("SysTray", "Salir"))
    exit_action.triggered.connect(app.quit)
    new_menu.addAction(exit_action)

    current_tray.setContextMenu(new_menu)

    # Actualizar la UI de la ventana principal
    dashboard_window.update_ui_texts()

def systraymenu():
    global current_tray
    app = QApplication(sys.argv)

    dashboard_window = DashboardWindow()

    # Crear systray inicial y asignar a la variable global
    current_tray = QSystemTrayIcon()
    current_tray.setIcon(QIcon.fromTheme("preferences-system"))
    current_tray.setVisible(True)

    # Crear menú inicial
    menu = QMenu()

    action_show = QAction(app.translate("SysTray", "Mostrar Panel"))
    action_show.triggered.connect(dashboard_window.show)
    menu.addAction(action_show)

    language_menu = QMenu(app.translate("SysTray", "Idioma"))

    english_action = QAction(app.translate("SysTray", "Inglés"))
    english_action.triggered.connect(lambda: set_language(app, "en", dashboard_window))
    language_menu.addAction(english_action)

    spanish_action = QAction(app.translate("SysTray", "Español"))
    spanish_action.triggered.connect(lambda: set_language(app, "es", dashboard_window))
    language_menu.addAction(spanish_action)

    menu.addMenu(language_menu)

    exit_action = QAction(app.translate("SysTray", "Salir"))
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    current_tray.setContextMenu(menu)

    sys.exit(app.exec())

def main():
    systraymenu()

if __name__ == "__main__":
    main()
