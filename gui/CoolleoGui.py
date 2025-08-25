import sys
import subprocess
import shutil
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QCloseEvent

from gui.window.ShutdownCountdownDialog import ShutdownCountdownDialog
from gui.window.ThresholdsConfigDialog import ThresholdsConfigDialog
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

        self.tray = QSystemTrayIcon(QIcon(str(coolleo.resource_path / "icon/coolleo.png")), self.window)
        self.tray.setToolTip("Coolleo Dashboard")

        menu = QMenu(self.window)
        action_show = QAction("Mostrar Panel", self.window)
        action_config = QAction("Umbrales de temperatura", self.window)
        action_config.triggered.connect(self.open_thresholds_config)
        action_quit = QAction("Salir", self.window)

        action_show.triggered.connect(self.window.show)
        action_quit.triggered.connect(self.app.quit)

        menu.addAction(action_show)
        menu.addAction(action_config)
        menu.addSeparator()
        menu.addAction(action_quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

        self.app.exec()

    def main_window(self):
        main_window = CoolleoMainWindow()
        main_window.__init__()
        main_window.setWindowIcon(QIcon(str(coolleo.resource_path / "icon/coolleo.png")))
        main_window.setFixedSize(QSize(600, 400))
        main_window.setWindowTitle(COOLLEO_WINDOW_TITLE)

        menu_bar = main_window.menuBar()
        menu_bar.setNativeMenuBar(False)
        ajustes = menu_bar.addMenu("Ajustes")
        act_umbral = ajustes.addAction("Umbrales de temperatura")
        act_umbral.triggered.connect(self.open_thresholds_config)

        self.graph = Graph()
        self.graph.on_alert = self._handle_threshold_alert
        self._shutdown_dialog_open = False

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.graph.handle())
        main_layout.addLayout(ActionButtons().handle())

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        
        main_window.setCentralWidget(main_widget)
        return main_window
    
    def open_thresholds_config(self):
        dlg = ThresholdsConfigDialog(self.window)
        dlg.exec()
    
    def _ensure_tray(self):
        if getattr(self, "tray", None):
            return
        icon_path = str(coolleo.resource_path / "icon/coolleo.png")
        self.tray = QSystemTrayIcon(QIcon(icon_path), self.window)
        menu = QMenu()
        menu.addAction("Mostrar panel", self.window.show)
        menu.addAction("Umbrales de temperatura", self.open_thresholds_config)
        menu.addAction("Salir", self.app.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def _handle_threshold_alert(self, level: str, temp: float, warn_c: int, crit_c: int):
        try:
            self._ensure_tray()
            icon = (QSystemTrayIcon.MessageIcon.Critical
                    if level == "critical" else QSystemTrayIcon.MessageIcon.Warning)
            self.tray.showMessage(
                "Coolleo · " + ("Temperatura crítica" if level == "critical" else "Temperatura alta"),
                f"Actual: {temp:.1f} °C · Aviso: {warn_c} °C · Crítica: {crit_c} °C",
                icon,
                8000
            )
        except Exception:
            pass

        if level == "critical" and not self._shutdown_dialog_open:
            self._shutdown_dialog_open = True
            dlg = ShutdownCountdownDialog(seconds=30, parent=self.window)
            accepted = dlg.exec()
            self._shutdown_dialog_open = False
            if accepted:
                self._prepare_graceful_shutdown()
                self._try_system_shutdown()

    def _try_system_shutdown(self):

        cmds = [
            ["busctl", "call", "org.freedesktop.login1", "/org/freedesktop/login1",
            "org.freedesktop.login1.Manager", "PowerOff", "b", "true"],
            ["dbus-send", "--system", "--print-reply",
            "--dest=org.freedesktop.login1", "/org/freedesktop/login1",
            "org.freedesktop.login1.Manager.PowerOff", "boolean:true"],

            ["systemctl", "poweroff", "-i"],

            ["qdbus", "org.kde.ksmserver", "/KSMServer", "logout", "0", "2", "2"],
            ["qdbus6", "org.kde.ksmserver", "/KSMServer", "logout", "0", "2", "2"],

            ["shutdown", "-h", "now"],

            ["pkexec", "systemctl", "poweroff", "-i"],
        ]

        for cmd in cmds:
            exe = shutil.which(cmd[0])
            if not exe:
                continue
            cmd[0] = exe
            try:
                # Si falla (exit!=0) lanza excepción y pasamos al siguiente
                subprocess.run(cmd, check=True)
                return True  # Si llega aquí, el sistema debería apagarse o estar en camino
            except Exception:
                continue

        QMessageBox.critical(
            self.window, "No se pudo apagar",
            "No se pudo solicitar el apagado automático.\n"
            "Prueba manualmente desde tu sistema."
        )
        return False


    def _prepare_graceful_shutdown(self):
        if hasattr(self, "graph") and hasattr(self.graph, "stop"):
            try: 
                self.graph.stop()
            except Exception:
                pass


class CoolleoMainWindow(QMainWindow):
    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()