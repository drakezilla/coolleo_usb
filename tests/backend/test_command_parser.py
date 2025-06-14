import pytest
from unittest.mock import MagicMock, patch
from core.CommandParser import CommandParser


def test_handle_set_mode():
    mock_controller = MagicMock()
    parser = CommandParser(mock_controller)

    response = parser.handle("SET_MODE cpu_usage")

    mock_controller.set_mode.assert_called_once_with("cpu_usage")
    assert response == "OK. Modo cambiado a cpu_usage\n"


def test_handle_set_brightness():
    mock_controller = MagicMock()
    parser = CommandParser(mock_controller)

    response = parser.handle("SET_BRIGHTNESS 3")

    mock_controller.set_brightness.assert_called_once_with(3)
    assert response == "OK. Brillo cambiado a 3\n"


@patch("core.CommandParser.SystemMetrics")
def test_handle_get_status(mock_metrics_class):
    mock_metrics = MagicMock()
    mock_metrics.get_cpu_temp.return_value = 42
    mock_metrics.get_cpu_usage.return_value = 75
    mock_metrics.get_cpu_watts.return_value = 88
    mock_metrics_class.return_value = mock_metrics

    parser = CommandParser(MagicMock())
    response = parser.handle("GET_STATUS")

    assert response == "TEMP:42;UCPU:75;WATTS:88\n"


def test_handle_unknown_command():
    parser = CommandParser(MagicMock())
    response = parser.handle("DO_A_FLIP")

    assert response == "ERROR. Comando no reconocido.\n"
