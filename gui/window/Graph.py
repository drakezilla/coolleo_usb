import pyqtgraph
from collections import deque
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer

from gui.communication.DeviceGuiCommunication import DeviceGuiCommunication

GRAPH_TITLE = "Temperature, CPU Usage, and Power consumption"

class Graph():

    temperature_data = deque(maxlen=50)
    cpu_usage_data = deque(maxlen=50)
    power_consumption_data = deque(maxlen=50)
    time_data = deque(maxlen=50)

    def __init__(self):
        self.graph = pyqtgraph.PlotWidget()
        self.graph.setBackground((25,25,25))
        self.graph.setYRange(0, 100)
        self.graph.setTitle(GRAPH_TITLE)
        self.graph.addLegend()
        self.counter = 0

        self.temp_curve = self.graph.plot(
            pen=pyqtgraph.mkPen(color='#FF6666', width=2), name="Temp (°C)"
        )
        self.cpu_curve = self.graph.plot(
            pen=pyqtgraph.mkPen(color='#66FF66', width=2), name="CPU (%)"
        )
        self.watts_curve = self.graph.plot(
            pen=pyqtgraph.mkPen(color='#6666FF', width=2), name="Watts"
        )

        self.timer = QTimer()
    
    def handle(self):
        graph_layout = QVBoxLayout()
        graph_layout.setSpacing(24)
        graph_layout.addLayout(self._create_graph_layout())

        self.timer.timeout.connect(self.update_graph)
        self.timer.start(2000)

        return graph_layout
    
    def update_graph(self):
        temp, ucpu, watts = DeviceGuiCommunication.read_device_status()
        
        self.time_data.append(self.counter)
        self.counter += 1
        self.temperature_data.append(temp)
        self.cpu_usage_data.append(ucpu)
        self.power_consumption_data.append(watts)

        self.temp_curve.setData(self.time_data, self.temperature_data)
        self.cpu_curve.setData(self.time_data, self.cpu_usage_data)
        self.watts_curve.setData(self.time_data, self.power_consumption_data)

        self._set_curve_label(self.temp_curve,  f"Temp ({float(temp):.1f} °C)")
        self._set_curve_label(self.cpu_curve,   f"CPU ({int(round(float(ucpu)))} %)")
        self._set_curve_label(self.watts_curve, f"Watts ({self._fmt_watts(watts)})")


    def _create_graph_layout(self):
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.graph)

        return graph_layout
    
    def _fmt_watts(self, w):
        try:
            w = float(w)
        except (TypeError, ValueError):
            return "—"
        return f"{w/1000:.1f} kW" if w >= 1000 else f"{int(round(w))} W"
    
    def _set_curve_label(self, curve, text):
        """Actualiza el texto de la leyenda para 'curve' de forma compatible con varias versiones."""
        # A) Si existe setName (versiones nuevas)
        if hasattr(curve, "setName"):
            try:
                curve.setName(text)
                return
            except Exception:
                pass

        # B) Actualizar el label directamente desde la legend (versiones clásicas)
        legend = getattr(self.graph.plotItem, "legend", None)
        if legend and hasattr(legend, "itemDict") and curve in legend.itemDict:
            sample, label = legend.itemDict[curve]
            if hasattr(label, "setText"):
                label.setText(text)
                return

        # C) Fallback: quitar y volver a añadir el item con el nuevo texto
        if legend:
            try:
                legend.removeItem(curve)
            except Exception:
                pass
            legend.addItem(curve, text)
