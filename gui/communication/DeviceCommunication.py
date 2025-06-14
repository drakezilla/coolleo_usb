import socket

from config import coolleo


class DeviceCommunication():

    @classmethod
    def send_command(cls, command: str) -> str:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(coolleo.socket_path)
                client.sendall(f"{command}\n".encode())
                response = client.recv(1024).decode().strip()
                return response
        except Exception as e:
            return f"[ERROR]: {e}"

    @classmethod
    def set_mode(cls, mode: str) -> str:
        return cls.send_command(f"SET_MODE {mode}")

    @classmethod
    def set_brightness(cls, level: int) -> str:
        return cls.send_command(f"SET_BRIGHTNESS {level}")

    @classmethod
    def get_status(cls) -> str:
        return cls.send_command("GET_STATUS")
    
    @classmethod
    def read_device_status(cls) -> tuple[int, int, int]:
        response = cls.get_status()
        try:
            data = dict(item.split(":") for item in response.split(";"))
            temp = int(data.get("TEMP", 40))
            ucpu = int(data.get("UCPU", 10))
            watts = int(data.get("WATTS", 20))
            return temp, ucpu, watts
        except Exception as e:
            print(f"[ERROR]: {e}")
            return 40, 10, 20