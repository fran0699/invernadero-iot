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
# El usuario y la clave NO van aquí: van en secretos.py (ver secretos_ejemplo.py)
ADAFRUIT_SERVIDOR = "io.adafruit.com"
ADAFRUIT_PUERTO = 8883      # MQTT con TLS: la clave no viaja en texto plano.
                            # Si la red bloquea el 8883, usar 1883 (sin cifrar) solo para probar.

# Contrato, sección 5: máximo un envío cada 15 s, porque el plan gratis
# permite 30 datos por minuto y cada envío manda hasta 6 datos (6 x 4 = 24)
INTERVALO_NUBE_S = 15

# Feeds que llena el gateway con lo que reporta la placa (el dashboard solo los muestra)
FEED_TEMPERATURA = "temperatura"
FEED_HUMEDAD = "humedad"
FEED_LUZ = "luz"
FEED_ESTADO_VENTILADOR = "estado-ventilador"
FEED_ESTADO_LUZ_CULTIVO = "estado-luz-cultivo"
FEED_ESTADO_MODO = "estado-modo"

# Feeds que escriben los botones del dashboard (el gateway solo los escucha).
# Van separados de los de estado: si fueran el mismo feed, el gateway recibiría
# su propio estado como si fuera una orden y pasaría la placa a modo manual.
FEED_CONTROL_VENTILADOR = "control-ventilador"
FEED_CONTROL_LUZ_CULTIVO = "control-luz-cultivo"
FEED_CONTROL_MODO = "control-modo"
