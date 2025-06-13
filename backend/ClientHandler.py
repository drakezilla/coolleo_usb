from core.CommandParser import CommandParser

class ClientHandler:
    def __init__(self, conn, device_controller):
        self.conn = conn
        self.device_controller = device_controller

    def handle(self):
        with self.conn:
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                cmd = data.decode().strip()
                response = self.process_command(cmd)
                self.conn.sendall(response.encode())

    def process_command(self, cmd: str) -> str:
        return CommandParser(self.device_controller).handle(cmd)