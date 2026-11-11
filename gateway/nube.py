"""
Conexión del gateway con Adafruit IO (dashboard en la nube).

Lo usa gateway/main.py (Juan) con las dos funciones del contrato
(docs/contrato.md, sección 5):
- conectar(al_recibir_comando): escucha los botones del dashboard y entrega
  cada orden al gateway como al_recibir_comando(accion, valor).
- enviar_lectura(lectura): manda al dashboard una lectura de /lecturas,
  como máximo una vez cada config.INTERVALO_NUBE_S segundos.

Habla con Adafruit IO por MQTT (la misma librería paho que usa el gateway con
EMQX), pero con un cliente propio, porque es otro broker: io.adafruit.com.
Feeds y servidor en config.py; usuario y clave en secretos.py.
"""
import time
import traceback

import paho.mqtt.client as mqtt

from gateway import config

# Valores que puede mandar un botón del dashboard para "encendido" y "apagado".
# El bloque Toggle manda "ON"/"OFF"; se aceptan también 1/0 y true/false
# por si alguien publica a mano desde la página del feed.
TEXTOS_ENCENDIDO = ("ON", "1", "TRUE")
TEXTOS_APAGADO = ("OFF", "0", "FALSE")
MODOS_VALIDOS = ("auto", "manual")

PUERTO_TLS = 8883  # Puerto cifrado de Adafruit IO; 1883 es el mismo servicio sin cifrar

# Qué acción del contrato representa cada feed de control
ACCION_POR_FEED = {
    config.FEED_CONTROL_VENTILADOR: "ventilador",
    config.FEED_CONTROL_LUZ_CULTIVO: "luz_cultivo",
    config.FEED_CONTROL_MODO: "modo",
}

# Qué campo de la lectura va a cada feed de sensores
CAMPO_POR_FEED_SENSOR = {
    config.FEED_TEMPERATURA: "temperatura",
    config.FEED_HUMEDAD: "humedad",
    config.FEED_LUZ: "luz",
}

# Qué campo de la lectura va a cada feed de estado
CAMPO_POR_FEED_ESTADO = {
    config.FEED_ESTADO_VENTILADOR: "ventilador",
    config.FEED_ESTADO_LUZ_CULTIVO: "luz_cultivo",
    config.FEED_ESTADO_MODO: "modo",
}

# Estado del módulo (un solo cliente para todo el gateway)
_cliente = None
_usuario = None
_al_recibir_comando = None
_ultimo_envio = None        # time.monotonic() del último envío aceptado
_ultimos_estados = {}       # feed de estado -> último valor enviado


# ---------------------------------------------------------------------------
# Funciones del contrato
# ---------------------------------------------------------------------------

def conectar(al_recibir_comando):
    """
    Conecta con Adafruit IO y empieza a escuchar los botones del dashboard.

    Recibe: al_recibir_comando, función del gateway que se llamará como
            al_recibir_comando(accion, valor) con los valores del contrato,
            por ejemplo ("ventilador", True) o ("modo", "manual").
    Devuelve: nada.

    No bloquea: la conexión corre en un hilo aparte y paho reconecta sola si
    se cae Internet. Por eso al_recibir_comando se ejecuta en ese hilo.
    Lanza RuntimeError si falta secretos.py o todavía tiene los valores de ejemplo.
    """
    global _cliente, _usuario, _al_recibir_comando
    _usuario, clave = _leer_credenciales()
    _al_recibir_comando = al_recibir_comando

    _cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    _cliente.username_pw_set(_usuario, clave)
    if config.ADAFRUIT_PUERTO == PUERTO_TLS:
        _cliente.tls_set()  # Certificados del sistema; io.adafruit.com usa uno público
    _cliente.on_connect = _al_conectar
    _cliente.on_disconnect = _al_desconectar
    _cliente.on_message = _al_llegar_mensaje

    print("Conectando a Adafruit IO:", config.ADAFRUIT_SERVIDOR)
    # connect_async no lanza error si no hay Internet: el hilo sigue intentando
    _cliente.connect_async(config.ADAFRUIT_SERVIDOR, config.ADAFRUIT_PUERTO)
    _cliente.loop_start()


def enviar_lectura(lectura):
    """
    Envía una lectura al dashboard, como máximo una vez cada config.INTERVALO_NUBE_S.

    Recibe: el diccionario de /lecturas (docs/contrato.md, sección 3).
    Devuelve: True si se envió; False si se ignoró porque llegó antes de
              tiempo o porque no hay conexión con Adafruit IO.

    Los sensores se mandan siempre; los estados (ventilador, luz de cultivo,
    modo) solo cuando cambian, para gastar menos datos del plan gratis.
    """
    global _ultimo_envio
    if not hay_conexion():
        return False
    ahora = time.monotonic()
    if _ultimo_envio is not None and ahora - _ultimo_envio < config.INTERVALO_NUBE_S:
        return False  # Contrato: las lecturas intermedias se ignoran

    _ultimo_envio = ahora
    enviados = _publicar_sensores(lectura) + _publicar_estados(lectura)
    print("Nube: lectura enviada a Adafruit IO (" + str(enviados) + " datos)")
    return True


# ---------------------------------------------------------------------------
# Funciones de apoyo (no son parte del contrato, pero se pueden usar)
# ---------------------------------------------------------------------------

def hay_conexion():
    """Devuelve True si el cliente está conectado a Adafruit IO."""
    return _cliente is not None and _cliente.is_connected()


def desconectar():
    """Cierra la conexión con Adafruit IO. Útil al cerrar el gateway con Ctrl+C."""
    if _cliente is None:
        return
    _cliente.disconnect()
    _cliente.loop_stop()
    print("Desconectado de Adafruit IO.")


def traducir_comando(feed, texto):
    """
    Traduce lo que manda un botón del dashboard al formato del contrato.

    Recibe: el feed que cambió (por ejemplo "control-ventilador") y su valor
            como texto (por ejemplo "ON").
    Devuelve: (accion, valor), por ejemplo ("ventilador", True),
              o None si el feed no es de control o el valor no se reconoce.
    """
    accion = ACCION_POR_FEED.get(feed)
    if accion is None:
        return None
    if accion == "modo":
        valor = _texto_a_modo(texto)
    else:
        valor = _texto_a_booleano(texto)
    if valor is None:
        return None
    return accion, valor


# ---------------------------------------------------------------------------
# Callbacks de paho (se ejecutan en el hilo de la conexión)
# ---------------------------------------------------------------------------

def _al_conectar(cliente, datos_usuario, banderas, codigo, propiedades):
    """Al conectar, se suscribe a los botones y a los avisos de Adafruit IO."""
    if codigo.is_failure:
        print("Adafruit IO rechazó la conexión:", codigo)
        if _es_error_de_clave(codigo):
            # Reintentar con una clave mala no sirve: se detiene y avisa
            print("Revisa el usuario y la clave en gateway/secretos.py.")
            cliente.disconnect()
        return

    print("Conectado a Adafruit IO como", _usuario)
    # Tras una reconexión se reenvían todos los estados en el siguiente envío
    _ultimos_estados.clear()
    for feed in ACCION_POR_FEED:
        cliente.subscribe(_topico_feed(feed))
        print("Escuchando el feed:", feed)
    # Adafruit IO avisa aquí si un dato fue rechazado o si se pasó el límite
    cliente.subscribe(_usuario + "/errors")
    cliente.subscribe(_usuario + "/throttle")


def _al_desconectar(cliente, datos_usuario, banderas, codigo, propiedades):
    """Avisa que se perdió la conexión; paho reintenta sola."""
    print("Se perdió la conexión con Adafruit IO:", codigo)


def _al_llegar_mensaje(cliente, datos_usuario, mensaje):
    """Recibe un mensaje de Adafruit IO y, si es una orden válida, la entrega al gateway."""
    texto = mensaje.payload.decode("utf-8", errors="replace")
    if mensaje.topic.endswith("/errors"):
        print("Adafruit IO reportó un error:", texto)
        return
    if mensaje.topic.endswith("/throttle"):
        print("Adafruit IO limitó los envíos:", texto)
        return

    feed = mensaje.topic.split("/")[-1]
    comando = traducir_comando(feed, texto)
    if comando is None:
        print("Nube: valor no reconocido en", feed, "->", texto, "(se ignora)")
        return
    accion, valor = comando
    print("Nube: orden del dashboard ->", accion, valor)
    _entregar_comando(accion, valor)


# ---------------------------------------------------------------------------
# Funciones internas
# ---------------------------------------------------------------------------

def _leer_credenciales():
    """Devuelve (usuario, clave) de secretos.py, o lanza RuntimeError con la solución."""
    try:
        from gateway import secretos
    except ImportError:
        raise RuntimeError(
            "Falta gateway/secretos.py. Copia gateway/secretos_ejemplo.py con ese "
            "nombre y escribe tu usuario y clave de Adafruit IO."
        )
    from gateway import secretos_ejemplo
    if secretos.ADAFRUIT_IO_CLAVE == secretos_ejemplo.ADAFRUIT_IO_CLAVE:
        raise RuntimeError(
            "gateway/secretos.py todavía tiene la clave de ejemplo. "
            "Escribe tu clave de Adafruit IO."
        )
    return secretos.ADAFRUIT_IO_USUARIO, secretos.ADAFRUIT_IO_CLAVE


def _entregar_comando(accion, valor):
    """
    Llama al callback del gateway.

    Si el callback falla, se muestra el error pero el hilo de la conexión
    sigue vivo; si no, un error en el gateway dejaría la nube sorda.
    """
    if _al_recibir_comando is None:
        return
    try:
        _al_recibir_comando(accion, valor)
    except Exception:
        print("Error en al_recibir_comando del gateway:")
        traceback.print_exc()


def _publicar_sensores(lectura):
    """Publica temperatura, humedad y luz. Devuelve cuántos datos publicó."""
    publicados = 0
    for feed, campo in CAMPO_POR_FEED_SENSOR.items():
        valor = lectura.get(campo)
        if valor is None:
            continue  # El DHT22 falló en esta lectura: no se manda un dato falso
        if _publicar(feed, valor):
            publicados = publicados + 1
    return publicados


def _publicar_estados(lectura):
    """Publica los estados que cambiaron desde el último envío. Devuelve cuántos publicó."""
    publicados = 0
    for feed, campo in CAMPO_POR_FEED_ESTADO.items():
        if campo not in lectura:
            continue
        valor = _valor_para_feed(lectura[campo])
        if _ultimos_estados.get(feed) == valor:
            continue  # Igual que antes: no gasta un dato
        if _publicar(feed, valor):
            _ultimos_estados[feed] = valor
            publicados = publicados + 1
    return publicados


def _publicar(feed, valor):
    """Publica un valor en un feed. Devuelve True si paho lo aceptó."""
    resultado = _cliente.publish(_topico_feed(feed), str(valor))
    return resultado.rc == mqtt.MQTT_ERR_SUCCESS


def _valor_para_feed(valor):
    """
    Convierte un valor de la lectura al texto que guarda el feed.
    True/False pasan a 1/0 para que el bloque Indicator y las gráficas los entiendan.
    """
    if valor is True:
        return 1
    if valor is False:
        return 0
    return valor


def _topico_feed(feed):
    """Devuelve el tópico MQTT de un feed: usuario/feeds/clave-del-feed."""
    return _usuario + "/feeds/" + feed


def _texto_a_booleano(texto):
    """Convierte "ON"/"OFF" (o 1/0, true/false) en True/False. Devuelve None si no se reconoce."""
    texto = texto.strip().upper()
    if texto in TEXTOS_ENCENDIDO:
        return True
    if texto in TEXTOS_APAGADO:
        return False
    return None


def _texto_a_modo(texto):
    """Convierte "auto"/"manual" (sin importar mayúsculas). Devuelve None si no se reconoce."""
    texto = texto.strip().lower()
    if texto in MODOS_VALIDOS:
        return texto
    return None


def _es_error_de_clave(codigo):
    """True si Adafruit IO rechazó la conexión por usuario o clave incorrectos."""
    # 134 = "Bad user name or password", 135 = "Not authorized"
    return codigo.value in (134, 135)
