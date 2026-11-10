"""
Cliente MQTT para publicar lecturas, eventos y respuestas, y recibir órdenes.

Se conecta con placa/config.py, placa/red.py y es utilizado por placa/main.py
para comunicarse con el Gateway Python a través de broker.emqx.io.
"""

import json
import machine
import urandom
from umqtt.simple import MQTTClient
import config
import red


def generar_client_id():
    """
    Construye un identificador único con sufijo aleatorio para el broker.
    No recibe parámetros. Devuelve un string con el CLIENT_ID.
    """
    id_placa = ""
    for byte in machine.unique_id():
        id_placa = id_placa + "{:02x}".format(byte)
    aleatorio = urandom.getrandbits(16)
    return "invernadero_" + id_placa + "_" + str(aleatorio)


def conectar_mqtt(callback_mensajes):
    """
    Conecta al broker EMQX y se suscribe al tópico de control.
    Recibe la función que procesará los comandos entrantes.
    Devuelve el objeto MQTTClient conectado o None si falló.
    """
    client_id = generar_client_id()
    try:
        cliente = MQTTClient(
            client_id,
            config.MQTT_BROKER,
            port=config.MQTT_PUERTO,
            keepalive=60
        )
        cliente.set_callback(callback_mensajes)
        cliente.connect()
        cliente.subscribe(config.TOPICO_CONTROL.encode("utf-8"))
        print("MQTT conectado como:", client_id)
        print("Suscrito a:", config.TOPICO_CONTROL)
        return cliente
    except Exception as error:
        print("Error al conectar a MQTT:", error)
        return None


def publicar_json(cliente, topico, diccionario):
    """
    Convierte un diccionario a JSON y lo publica en el tópico indicado.
    Recibe el cliente MQTT, el tópico (str) y el diccionario de datos.
    Devuelve True si se publicó con éxito o False si falló la conexión.
    """
    if cliente is None:
        return False
    try:
        mensaje = json.dumps(diccionario)
        cliente.publish(topico.encode("utf-8"), mensaje.encode("utf-8"))
        return True
    except Exception as error:
        print("Error al publicar en", topico, ":", error)
        return False


def publicar_lectura(cliente, lectura):
    """
    Publica una lectura de sensores y estado en el tópico /lecturas.
    Recibe el cliente MQTT y el diccionario de lectura. Devuelve True o False.
    """
    return publicar_json(cliente, config.TOPICO_LECTURAS, lectura)


def publicar_evento(cliente, tipo_evento, detalle_texto):
    """
    Arma y publica un evento (regla_automatica o reconexion) en /eventos.
    Recibe el cliente MQTT, el tipo de evento y el detalle descriptivo.
    Devuelve True si se envió o False si hubo un fallo.
    """
    evento = {
        "dispositivo": config.DISPOSITIVO,
        "timestamp": red.obtener_timestamp(),
        "tipo": tipo_evento,
        "detalle": detalle_texto
    }
    return publicar_json(cliente, config.TOPICO_EVENTOS, evento)


def publicar_respuesta_comando(cliente, accion, valor, resultado, motivo):
    """
    Publica la confirmación de una orden procesada en el tópico /comandos.
    Recibe cliente MQTT, acción, valor, resultado y motivo. Devuelve True o False.
    """
    respuesta = {
        "dispositivo": config.DISPOSITIVO,
        "timestamp": red.obtener_timestamp(),
        "accion": accion,
        "valor": valor,
        "resultado": resultado,
        "motivo": motivo
    }
    return publicar_json(cliente, config.TOPICO_COMANDOS, respuesta)


def revisar_mensajes(cliente):
    """
    Revisa sin bloquear si llegó alguna orden desde el tópico /control.
    Recibe el cliente MQTT. Devuelve True si la conexión sigue sana o False si cayó.
    """
    if cliente is None:
        return False
    try:
        cliente.check_msg()
        return True
    except Exception as error:
        print("Fallo al revisar mensajes MQTT:", error)
        return False
