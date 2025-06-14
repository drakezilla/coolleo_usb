from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QCloseEvent
import sys

from gui.window.ActionButtons import ActionButtons
from gui.window.Graph import Graph
from config import coolleo

COOLLEO_WINDOW_TITLE = "Coolleo dashboard"

class CoolleoGui():

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = self.main_window()

    def start(self):
        self.window.show()
        #systray begin. I can't move it anywhere else
        tray_icon = QSystemTrayIcon(QIcon(str(coolleo.resource_path / "icon/systray.svg")), self.window)
        tray_icon.setToolTip("Coolleo Dashboard")

        menu = QMenu()
        action_show = QAction("Mostrar Panel")
        action_quit = QAction("Salir")

        action_show.triggered.connect(self.window.show)
        action_quit.triggered.connect(self.app.quit)

        menu.addAction(action_show)
        menu.addSeparator()
        menu.addAction(action_quit)

        tray_icon.setContextMenu(menu)
        tray_icon.show()

        self._tray_icon = tray_icon
        self._tray_menu = menu
        #systray end
        self.app.exec()

    def main_window(self):
        main_window = CoolleoMainWindow()
        main_window.__init__()
        main_window.setWindowIcon(QIcon(str(coolleo.resource_path / "icon/systray.svg")))
        main_window.setFixedSize(QSize(600, 400))
        main_window.setWindowTitle(COOLLEO_WINDOW_TITLE)

        self.graph = Graph()

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.graph.handle())
        main_layout.addLayout(ActionButtons().handle())

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        
        main_window.setCentralWidget(main_widget)
        return main_window
    

class CoolleoMainWindow(QMainWindow):
    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()