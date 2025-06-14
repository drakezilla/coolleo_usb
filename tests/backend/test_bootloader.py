import pytest
import subprocess

from unittest import mock
from unittest.mock import patch, MagicMock
from core.Bootloader import Bootloader


@patch("core.Bootloader.Bootloader._verify_device_ready", return_value=None)
@patch("core.Bootloader.DeviceUpdateDaemon")
@patch("core.Bootloader.DeviceController")
@patch("core.Bootloader.DeviceBridge")
@patch("core.Bootloader.DeviceDetection")
def test_bootloader_start_success(
    mock_detection, mock_bridge, mock_controller, mock_daemon, mock_verify
):
    mock_detection.return_value.handle.return_value = {"device_port": "/dev/fakeport"}
    mock_bridge.return_value.handle.return_value = MagicMock(port="/dev/fakeport")
    mock_controller.return_value = MagicMock()
    mock_daemon.return_value = MagicMock()

    boot = Bootloader()
    result = boot.start()

    assert result.device_info == {"device_port": "/dev/fakeport"}
    assert result.bridge.port == "/dev/fakeport"
    assert isinstance(result.controller, MagicMock)
    assert isinstance(result.daemon, MagicMock)

    result.daemon.start.assert_called_once()



@mock.patch("subprocess.run", side_effect=FileNotFoundError)
def test_bootloader_exits_if_sensors_not_found(mock_run):
    with pytest.raises(SystemExit) as exc:
        Bootloader().start()
    assert "lm-sensors" in str(exc.value)


@mock.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "sensors"))
def test_bootloader_exits_if_sensors_fails(mock_run):
    with pytest.raises(SystemExit) as exc:
        Bootloader().start()
    assert "lm-sensors" in str(exc.value)