"""
Configuración del gateway (Python en la PC).

Valores compartidos con la placa (broker, tópicos y token) y ruta de la
base de datos. Vienen del contrato: docs/contrato.md.
Las claves de Adafruit IO NO van aquí: van en secretos.py, que no se sube.
"""

# --- MQTT (los mismos valores que placa/config.py) ---
MQTT_BROKER = "broker.emqx.io"
MQTT_PUERTO = 1883

TOPICO_BASE = "utp/fisc/ds8/fran0699/invernadero"
TOPICO_LECTURAS = TOPICO_BASE + "/lecturas"
TOPICO_EVENTOS = TOPICO_BASE + "/eventos"
TOPICO_COMANDOS = TOPICO_BASE + "/comandos"
TOPICO_CONTROL = TOPICO_BASE + "/control"

# El gateway agrega este token a cada orden que envía a la placa
TOKEN = "INVERNADERO_DS8_2026"

# --- Base de datos (Juan) ---
RUTA_BASE_DATOS = "invernadero.db"   # Archivo SQLite que usa el gateway

# --- Adafruit IO (Luis) ---

ADAFRUIT_SERVIDOR = "io.adafruit.com"
ADAFRUIT_PUERTO = 8883
INTERVALO_NUBE_S = 15

# Feeds para visualizar lecturas y estados
FEED_TEMPERATURA = "temperatura"
FEED_HUMEDAD = "humedad"
FEED_LUZ = "luz"

FEED_ESTADO_VENTILADOR = "estado-ventilador"
FEED_ESTADO_LUZ_CULTIVO = "estado-luz-cultivo"
FEED_ESTADO_MODO = "estado-modo"

# Feeds para recibir comandos del dashboard
FEED_CONTROL_VENTILADOR = "control-ventilador"
FEED_CONTROL_LUZ_CULTIVO = "control-luz-cultivo"
FEED_CONTROL_MODO = "control-modo"