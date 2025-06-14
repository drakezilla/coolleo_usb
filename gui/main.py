import threading

from gui.CoolleoGui import CoolleoGui
from core.Bootloader import Bootloader
from backend.ClientHandler import ClientHandler


def main():
    backend_thread = threading.Thread(target=backend_init, daemon=True)
    backend_thread.start()
    
    gui = CoolleoGui()
    gui.start()

def backend_init():
    boot = Bootloader().start()

    while True:
        conn, _ = boot.bridge.server.accept()
        threading.Thread(
            target=ClientHandler(conn, boot.controller).handle
        ).start()

if __name__ == "__main__":
    main()