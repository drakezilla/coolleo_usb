import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from dashboard_window import DashboardWindow
from backend_manager import BackendManager
from config_manager import ConfigManager
from config_dialog import ConfigDialog

current_tray = None
tray_actions = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.abspath(os.path.join(BASE_DIR, "../resources/icon/coolleo_dashboard.svg"))

def ensure_configuration_and_backend(app):
    config = ConfigManager()
    if not config.get_serial_port():
        config_dialog = ConfigDialog()
        if not config_dialog.exec():
            sys.exit(1)

    backend_manager = BackendManager()
    print("DEBUG: Checking if backend is running...")
    if not backend_manager.is_backend_running():
        print("DEBUG: Backend not running, attempting to start it...")
        backend_manager.start_backend()
        if not backend_manager.is_backend_running():
            show_backend_error_dialog(app)
            return False
    return True

def show_backend_error_dialog(app):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error")
    msg.setText(
        "Error: The backend could not start.\nDo you want to configure the serial port now?"
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    ret = msg.exec()

    if ret == QMessageBox.StandardButton.Yes:
        config_dialog = ConfigDialog()
        if config_dialog.exec():
            backend_manager = BackendManager()
            if not backend_manager.is_backend_running():
                backend_manager.start_backend()
            if backend_manager.is_backend_running():
                return
    sys.exit(1)

def create_systray(app, dashboard_window):
    global current_tray, tray_actions

    current_tray = QSystemTrayIcon()

    if os.path.exists(ICON_PATH):
        current_tray.setIcon(QIcon(ICON_PATH))
    else:
        print("WARNING: Icon file not found for systray, using default icon.")

    current_tray.setVisible(True)

    menu = QMenu()
    action_show = QAction("Show")
    action_show.triggered.connect(dashboard_window.show)
    menu.addAction(action_show)

    exit_action = QAction("Exit")
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray_actions = {'show': action_show, 'exit': exit_action}
    current_tray.setContextMenu(menu)

def systraymenu():
    global current_tray, tray_actions

    app = QApplication(sys.argv)

    if not ensure_configuration_and_backend(app):
        sys.exit(1)

    dashboard_window = DashboardWindow()

    create_systray(app, dashboard_window)

    sys.exit(app.exec())

if __name__ == "__main__":
    systraymenu()
