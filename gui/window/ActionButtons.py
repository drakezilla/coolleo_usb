from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QSlider
from PyQt6.QtCore import Qt

from gui.communication.DeviceCommunication import DeviceCommunication

class ActionButtons():

    def handle(self):
        button_layout = QVBoxLayout()
        button_layout.addLayout(self._create_mode_controls_layout())
        button_layout.addLayout(self._create_brightness_slider_layout())
        
        return button_layout
    
    def _create_mode_controls_layout(self):
        mode_layout = QHBoxLayout()
        
        label = QLabel("Mode:")
        
        temp_button = QPushButton("Temperature")
        temp_button.clicked.connect(lambda: print(DeviceCommunication.set_mode("temperature")))

        usage_button = QPushButton("CPU Usage")
        usage_button.clicked.connect(lambda: print(DeviceCommunication.set_mode("usage")))

        alternate_button = QPushButton("Alternate")
        alternate_button.clicked.connect(lambda: print(DeviceCommunication.set_mode("alternate")))

        mode_layout.addWidget(label)
        mode_layout.addWidget(temp_button)
        mode_layout.addWidget(usage_button)
        mode_layout.addWidget(alternate_button)

        return mode_layout

    def _create_brightness_slider_layout(self):
        brightness_layout = QHBoxLayout()
        label = QLabel("Brightness:")
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(5)
        slider.setMaximum(5)
        slider.setMinimum(1)
        slider.setFixedWidth(436)
        slider.sliderReleased.connect(lambda: print(DeviceCommunication.set_brightness(slider.value())))

        brightness_layout.addWidget(label)
        brightness_layout.addWidget(slider)

        return brightness_layout