"""
Configuración de la placa (Pico W en Wokwi).

Aquí están todos los valores fijos de la placa: pines, umbrales, Wi-Fi,
broker MQTT, tópicos y token. Los demás módulos los importan, así que para
cambiar un valor solo se toca este archivo.
Los valores vienen del contrato: docs/contrato.md.
"""

# --- Pines (Francisco) ---
PIN_DHT22 = 15          # Dato del sensor de temperatura y humedad
PIN_LUZ = 26            # Salida analógica de la fotorresistencia (GP26 = ADC0)
PIN_VENTILADOR = 16     # Relé que enciende el ventilador
PIN_LUZ_CULTIVO = 17    # LED que representa la luz de cultivo

# --- Umbrales de las reglas automáticas (Francisco) ---
TEMPERATURA_MAXIMA = 30.0   # °C: por encima, se enciende el ventilador
LUZ_MINIMA = 40             # %: por debajo, se enciende la luz de cultivo

# --- Muestreo (José) ---
INTERVALO_LECTURA_MS = 5000  # Cada cuánto el Timer pide una lectura

# --- Wi-Fi (José) ---
WIFI_SSID = "Wokwi-GUEST"    # Red abierta que crea Wokwi
WIFI_CLAVE = ""
WIFI_TIMEOUT_S = 15          # Regla #1: no esperar la conexión para siempre

# --- MQTT (José) ---
MQTT_BROKER = "broker.emqx.io"
MQTT_PUERTO = 1883
DISPOSITIVO = "pico01"

# "fran0699" evita que otro grupo use los mismos tópicos en el broker público
TOPICO_BASE = "utp/fisc/ds8/fran0699/invernadero"
TOPICO_LECTURAS = TOPICO_BASE + "/lecturas"
TOPICO_EVENTOS = TOPICO_BASE + "/eventos"
TOPICO_COMANDOS = TOPICO_BASE + "/comandos"
TOPICO_CONTROL = TOPICO_BASE + "/control"

# Regla #11: la placa solo ejecuta las órdenes que traen este token
TOKEN = "INVERNADERO_DS8_2026"

# --- Almacenamiento offline y tiempo UTC (José) ---
ARCHIVO_PENDIENTES = "pendientes.json"
MAX_LECTURAS_PENDIENTES = 50
SEGUNDOS_ENTRE_1970_Y_2000 = 946684800
