from unittest.mock import patch, MagicMock
from backend.DeviceController import DeviceController

@patch("backend.DeviceController.DeviceCommunication")
def test_device_controller_handle_with_fixed_mode(mock_comm_class):
    mock_comm_instance = MagicMock()
    mock_comm_class.return_value = mock_comm_instance

    controller = DeviceController("/dev/fakeport")
    controller.set_mode("temperature")
    controller.set_brightness(3)

    mock_comm_instance.handle.assert_called_with("temperature", 3, "/dev/fakeport")


@patch("backend.DeviceController.DeviceCommunication")
def test_device_controller_handle_with_alternate_mode(mock_comm_class):
    mock_comm_instance = MagicMock()
    mock_comm_class.return_value = mock_comm_instance

    controller = DeviceController("/dev/fakeport")
    controller.set_mode("alternate")
    controller.set_brightness(2)

    # Reinstanciamos para empezar limpio
    controller = DeviceController("/dev/fakeport")
    controller.set_mode("alternate")
    controller.set_brightness(2)

    mock_comm_instance.handle.reset_mock()

    controller.handle()  # Ahora sí: cpu_usage
    mock_comm_instance.handle.assert_called_with("cpu_usage", 2, "/dev/fakeport")

    controller.handle()  # Luego: temperature
    mock_comm_instance.handle.assert_called_with("temperature", 2, "/dev/fakeport")
