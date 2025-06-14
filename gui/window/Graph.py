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

    def _create_graph_layout(self):
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.graph)

        return graph_layout
    
    
    
