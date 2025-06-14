from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from config import coolleo

class Systray:
    def __init__(self, main_window, app):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(str(coolleo.resource_path / "icon/systray.svg")))
        self.tray.setToolTip("Coolleo Dashboard")

        self.menu = QMenu()
        action_show = QAction("Mostrar Panel")
        action_quit = QAction("Salir")

        action_show.triggered.connect(main_window.show)
        action_quit.triggered.connect(app.quit)

        self.menu.addAction(action_show)
        self.menu.addSeparator()
        self.menu.addAction(action_quit)

        self.tray.setContextMenu(self.menu)
        self.tray.setVisible(True)