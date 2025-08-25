from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QLabel, QPushButton, QMessageBox
)


class ThresholdsConfigDialog(QDialog):
    """Dialogo de configuración de umbrales de temperatura.

    Guarda valores en QSettings con organization 'Coolleo' y app 'Dashboard'.
    Claves:
      - thresholds/warning_c (int)
      - thresholds/critical_c (int)
    """

    ORG = "Coolleo"
    APP = "Dashboard"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración · Umbrales de temperatura")
        self.setModal(True)

        self.settings = QSettings(self.ORG, self.APP)

        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(0, 110)
        self.warning_spin.setSuffix(" °C")
        self.warning_spin.setSingleStep(1)
        self.warning_spin.setToolTip("Temperatura de aviso (amarillo)")

        self.critical_spin = QSpinBox()
        self.critical_spin.setRange(0, 110)
        self.critical_spin.setSuffix(" °C")
        self.critical_spin.setSingleStep(1)
        self.critical_spin.setToolTip("Temperatura crítica (rojo)")

        # Cargar valores guardados o defaults
        warning_default = 70
        critical_default = 85
        warning_val = int(self.settings.value("thresholds/warning_c", warning_default))
        critical_val = int(self.settings.value("thresholds/critical_c", critical_default))
        self.warning_spin.setValue(warning_val)
        self.critical_spin.setValue(critical_val)

        # Layout de formulario
        form = QFormLayout()
        form.addRow(QLabel("Umbral de aviso:"), self.warning_spin)
        form.addRow(QLabel("Umbral crítico:"), self.critical_spin)

        # Botones
        self.btn_save = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_save)

        # Contenedor principal
        root = QVBoxLayout()
        root.addLayout(form)
        root.addStretch(1)
        root.addLayout(buttons)
        self.setLayout(root)

        self.setMinimumWidth(380)

    # --- API pública de utilidad ---
    @staticmethod
    def get_thresholds():
        s = QSettings(ThresholdsConfigDialog.ORG, ThresholdsConfigDialog.APP)
        w = int(s.value("thresholds/warning_c", 70))
        c = int(s.value("thresholds/critical_c", 85))
        return w, c

    # --- Internos ---
    def _on_save(self):
        w = self.warning_spin.value()
        c = self.critical_spin.value()
        if w >= c:
            QMessageBox.warning(
                self,
                "Valores inválidos",
                "El umbral de aviso debe ser menor que el umbral crítico.",
            )
            return

        self.settings.setValue("thresholds/warning_c", w)
        self.settings.setValue("thresholds/critical_c", c)
        self.settings.sync()
        self.accept()
