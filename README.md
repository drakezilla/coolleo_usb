Coolleo Dashboard

Graphical controller and real-time backend for the Coolleo B40S DIG cooler.
REQUIREMENTS

    Python 3.10 or higher

    System dependencies:

        lm-sensors (for monitoring CPU temperature and power consumption)

        psutil (CPU usage monitoring)

        pyserial (device communication)

Install system dependencies (Linux):

lm-sensors

INSTALL PYTHON DEPENDENCIES

pip install -r requirements.txt

EXECUTION

Backend (Controller):

python backend.py              # Normal mode (no logs)
python backend.py --verbose    # Verbose mode (detailed logs)

Important: Make sure the device is connected at /dev/ttyACM0.
If not, modify the PORT variable in backend.py.

Frontend (Graphical Dashboard):

python dashboard.py

CUSTOMIZATION

    Language selector: Available from the main window.

    Brightness and display modes: Controlled from the interface.

    Backend logs: Enabled with --verbose.

PROJECT STRUCTURE

coolleo_dashboard/
├── backend.py
├── dashboard.py
├── requirements.txt
├── i18n/
│ ├── ES_es.qm
│ └── EN_en.qm
└── assets/
└── coolleo_icon.svg
PRODUCTION MODE

To run the backend as a background service:

nohup python backend.py & 

LICENSE

Personal project developed by Enrique Núñez.
Feel free to fork and contribute! 🚀


Coolleo Dashboard

Controlador gráfico y backend en tiempo real para el disipador Coolleo B40S DIG.
REQUISITOS

    Python 3.10 o superior

    Dependencias del sistema:

        lm-sensors (para monitorizar temperatura y consumo CPU)

        psutil (uso de CPU)

        pyserial (comunicación con el dispositivo)

Instalación de dependencias del sistema (Linux):

sudo apt install lm-sensors
sudo sensors-detect   # (Opcional: para configurar sensores)

INSTALACIÓN DE DEPENDENCIAS PYTHON

pip install -r requirements.txt

EJECUCIÓN

Backend (Controlador):

python backend.py         # Modo normal (sin logs)
python backend.py --verbose  # Modo verbose (con logs detallados)

Importante: Asegúrate de que el dispositivo esté conectado en /dev/ttyACM0.
Si no, modifica la variable PORT en backend.py.

Frontend (Dashboard Gráfico):

python dashboard.py

PERSONALIZACIÓN

    Selector de idioma: Disponible desde la ventana principal.

    Brillo y modos de visualización: Controlables desde la interfaz.

    Logs del backend: Activables con --verbose.

ESTRUCTURA DE PROYECTO

coolleo_dashboard/
├── backend.py
├── dashboard.py
├── requirements.txt
├── i18n/
│ ├── ES_es.qm
│ └── EN_en.qm
└── assets/
└── coolleo_icon.svg
MODO PRODUCCIÓN

Para ejecutar el backend como servicio:

nohup python backend.py & 

LICENCIA

Proyecto personal desarrollado por Enrique Núñez.
Feel free to fork and contribute! 🚀
