from unittest.mock import patch
from gui.communication.DeviceGuiCommunication import DeviceGuiCommunication

@patch("gui.communication.DeviceGuiCommunication.DeviceGuiCommunication.read_device_status")
def test_get_status_data_returns_tuple(mock_read):
    mock_read.return_value = (42.0, 15.0, 5.5)

    temp, cpu, watts = DeviceGuiCommunication.read_device_status()

    assert isinstance(temp, float)
    assert isinstance(cpu, float)
    assert isinstance(watts, float)
    assert temp == 42.0
    assert cpu == 15.0
    assert watts == 5.5