import serial
import time

PORT = "/dev/ttyACM0"
BAUDRATE = 9600  # ajustaremos si no funciona

# Abrir conexión
ser = serial.Serial(PORT, BAUDRATE, timeout=1)

# Esperar un momento para asegurar que se inicializa
time.sleep(2)

# Paquete ejemplo (en binario)
packet = bytes.fromhex("2A0442010101010C0000000000")

# Enviar paquete
ser.write(packet)
print("Paquete enviado.")

# Opcional: leer respuesta (si devuelve algo)
response = ser.read(64)
print("Respuesta recibida:", response.hex())

# Cerrar puerto
ser.close()
