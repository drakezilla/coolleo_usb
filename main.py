from core.Bootloader import Bootloader
from backend.ClientHandler import ClientHandler
import threading

def main():
    boot = Bootloader().start()

    while True:
        conn, _ = boot.bridge.server.accept()
        threading.Thread(
            target=ClientHandler(conn, boot.controller).handle
        ).start()

if __name__ == "__main__":
    main()