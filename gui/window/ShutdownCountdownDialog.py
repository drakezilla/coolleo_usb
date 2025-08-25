from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class ShutdownCountdownDialog(QDialog):
    """
    Dialogo con cuenta regresiva para apagar el sistema.
    - 'Aceptar' se emite automáticamente al finalizar la cuenta.
    - Botones: "Cancelar" (abort) y "Apagar ahora" (accept inmediato).
    """

    def __init__(self, seconds: int = 30, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Temperatura crítica · Preparando apagado")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self._seconds = max(1, int(seconds))

        self.label = QLabel(self._format_text())
        self.label.setWordWrap(True)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_now = QPushButton("Apagar ahora")

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_now.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_now)

        root = QVBoxLayout()
        root.addWidget(self.label)
        root.addLayout(buttons)
        self.setLayout(root)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _format_text(self) -> str:
        return (
            f"Se ha detectado una temperatura CRÍTICA.\n\n"
            f"El sistema se apagará en {self._seconds} s si no se cancela."
        )

    def _tick(self):
        self._seconds -= 1
        if self._seconds <= 0:
            self.timer.stop()
            self.accept()
        else:
            self.label.setText(self._format_text())
