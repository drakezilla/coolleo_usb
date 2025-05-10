import socket

SOCKET_PATH = "/tmp/coolleo_socket"

def send_command(command):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(SOCKET_PATH)
        client.sendall(command.encode())
        response = client.recv(1024)
        print(response.decode())

# Ejemplo de uso:
send_command("SET_MODE ucpu")
send_command("SET_BRIGHTNESS 3")
send_command("GET_STATUS")
