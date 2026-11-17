"""
Gestión de la conexión Wi-Fi y sincronización de hora NTP.

Se conecta con placa/config.py para leer las credenciales y el timeout,
y es utilizado por placa/main.py y placa/conexion_mqtt.py.
"""

import network
import time
import ntptime
import config


def conectar_wifi():
    """
    Conecta la Pico W a la red Wi-Fi configurada respetando el timeout.
    No recibe parámetros. Devuelve True si se conectó o False si falló.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return True

    print("Conectando a Wi-Fi:", config.WIFI_SSID)
    wlan.connect(config.WIFI_SSID, config.WIFI_CLAVE)

    inicio = time.time()
    while not wlan.isconnected():
        if (time.time() - inicio) >= config.WIFI_TIMEOUT_S:
            print("Tiempo de espera agotado al conectar a Wi-Fi.")
            return False
        time.sleep(0.5)

    print("Wi-Fi conectado. IP:", wlan.ifconfig()[0])
    return True


def wifi_conectado():
    """
    Verifica si el enlace Wi-Fi sigue activo.
    No recibe parámetros. Devuelve True si está conectado o False si se cayó.
    """
    wlan = network.WLAN(network.STA_IF)
    return wlan.active() and wlan.isconnected()


def sincronizar_hora_ntp():
    """
    Ajusta el reloj interno de la placa en UTC usando un servidor NTP.
    No recibe parámetros. Devuelve True si sincronizó o False si hubo error.
    """
    try:
        ntptime.settime()
        print("Hora UTC sincronizada por NTP.")
        return True
    except Exception as error:
        # Si NTP falla al arrancar, el sistema continúa para no bloquear la placa
        print("No se pudo sincronizar NTP:", error)
        return False


def obtener_timestamp():
    """
    Entrega la hora actual en segundos desde 1970 (Unix epoch UTC).
    No recibe parámetros. Devuelve un entero con el timestamp UTC.
    """
    segundos = int(time.time())
    # Algunos firmwares de MicroPython cuentan desde el año 2000 en vez de 1970
    if segundos < config.SEGUNDOS_ENTRE_1970_Y_2000:
        segundos = segundos + config.SEGUNDOS_ENTRE_1970_Y_2000
    return segundos
