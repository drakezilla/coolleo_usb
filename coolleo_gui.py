import sys
import socket
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu,
    QWidget, QVBoxLayout, QSlider, QLabel, QPushButton
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

SOCKET_PATH = "/tmp/coolleo_socket"

def send_command(command):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(SOCKET_PATH)
            client.sendall(command.encode())
            response = client.recv(1024)
            print(response.decode())
    except Exception as e:
        print(f"Error: {e}")

class BrightnessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ajustar Brillo")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()
        self.label = QLabel("Brillo: 5", self)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(5)
        self.slider.setValue(5)
        self.slider.valueChanged.connect(self.update_label)

        apply_button = QPushButton("Aplicar")
        apply_button.clicked.connect(self.apply_brightness)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Brillo: {value}")

    def apply_brightness(self):
        value = self.slider.value()
        send_command(f"SET_BRIGHTNESS {value}")
        self.hide()  # Ocultamos la ventana pero no cerramos la aplicación

def main():
    app = QApplication(sys.argv)

    tray = QSystemTrayIcon()
    tray.setIcon(QIcon.fromTheme("preferences-system"))  # Cambia este icono si quieres
    tray.setVisible(True)

    menu = QMenu()
    brightness_window = BrightnessWindow()

    # Modo: Temperatura
    action_temp = QAction("Mostrar Temperatura")
    action_temp.triggered.connect(lambda: send_command("SET_MODE temperature"))
    menu.addAction(action_temp)

    # Modo: UCPU
    action_ucpu = QAction("Mostrar UCPU")
    action_ucpu.triggered.connect(lambda: send_command("SET_MODE ucpu"))
    menu.addAction(action_ucpu)

    # Alternar modos
    action_alternate = QAction("Alternar Temp/UCPU")
    action_alternate.triggered.connect(lambda: send_command("SET_MODE alternate"))
    menu.addAction(action_alternate)

    # Control de Brillo
    def open_brightness_window():
        brightness_window.show()
        brightness_window.raise_()  # Trae la ventana al frente
        brightness_window.activateWindow()

    action_brillo = QAction("Ajustar Brillo")
    action_brillo.triggered.connect(open_brightness_window)
    menu.addAction(action_brillo)

    # Salir
    exit_action = QAction("Salir")
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray.setContextMenu(menu)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
