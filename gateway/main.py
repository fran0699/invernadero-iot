
"""
main.py

Gateway MQTT del Invernadero IoT.

Se conecta al broker EMQX para recibir mensajes de la Raspberry Pi Pico W,
validarlos y almacenarlos en SQLite.

También se conecta con Adafruit IO para mostrar lecturas en el dashboard
y reenviar comandos de control hacia la placa.
"""

import json
import paho.mqtt.client as mqtt

from gateway.config import (
    MQTT_BROKER,
    MQTT_PUERTO,
    TOPICO_LECTURAS,
    TOPICO_EVENTOS,
    TOPICO_COMANDOS,
    TOPICO_CONTROL,
    TOKEN
)

from gateway.base_datos import (
    inicializar_base_datos,
    guardar_lectura,
    guardar_evento,
    guardar_comando
)

from gateway.validaciones import (
    validar_campos,
    validar_tipos_lectura,
    validar_valores_lectura,
    validar_evento,
    validar_comando
)

from gateway import nube


# Cliente MQTT que se conecta al broker EMQX.
# Se comparte con la función que recibe comandos desde Adafruit IO.
cliente_emqx = None


def al_conectar(cliente, datos_usuario, flags, codigo, propiedades):
    """Se suscribe a los tópicos MQTT del invernadero."""

    if codigo == 0:
        print("Gateway conectado correctamente al broker MQTT.")

        cliente.subscribe(TOPICO_LECTURAS)
        print("Suscrito al tópico:", TOPICO_LECTURAS)

        cliente.subscribe(TOPICO_EVENTOS)
        print("Suscrito al tópico:", TOPICO_EVENTOS)

        cliente.subscribe(TOPICO_COMANDOS)
        print("Suscrito al tópico:", TOPICO_COMANDOS)

    else:
        print("Error de conexion MQTT. Codigo:", codigo)



def al_recibir_mensaje(cliente, datos_usuario, mensaje):
    """Recibe mensajes MQTT, los valida y los guarda en SQLite."""

    try:
        contenido = mensaje.payload.decode("utf-8")
        datos = json.loads(contenido)

        if not isinstance(datos, dict):
            print("Error: el mensaje JSON debe ser un objeto.")
            return

        if mensaje.topic == TOPICO_LECTURAS:

            campos_lectura = [
                "dispositivo",
                "timestamp",
                "temperatura",
                "humedad",
                "luz",
                "ventilador",
                "luz_cultivo",
                "modo"
            ]

            if (
                validar_campos(datos, campos_lectura)
                and validar_tipos_lectura(datos)
                and validar_valores_lectura(datos)
            ):
                dispositivo = datos["dispositivo"]

                temperatura = datos["temperatura"]
                humedad = datos["humedad"]
                luz = datos["luz"]

                ventilador = (
                    "ENCENDIDO" if datos["ventilador"]
                    else "apagado"
                )

                luz_cultivo = (
                    "ENCENDIDA" if datos["luz_cultivo"]
                    else "apagada"
                )

                modo = datos["modo"]

                print(
                    f"\n---------- Lectura de {dispositivo} ----------"
                )

                print(
                    f"Temperatura: {temperatura} C | "
                    f"Humedad: {humedad} % | "
                    f"Luz: {luz} %"
                )

                print(
                    f"Ventilador: {ventilador} | "
                    f"Luz de cultivo: {luz_cultivo} | "
                    f"Modo: {modo}"
                )

                guardar_lectura(datos)

                # Enviar la lectura valida a Adafruit IO.
                # nube.py controla el intervalo de publicacion.
                nube.enviar_lectura(datos)

            else:
                print("Lectura MQTT rechazada: datos invalidos.")

        elif mensaje.topic == TOPICO_EVENTOS:

            if validar_evento(datos):
                dispositivo = datos["dispositivo"]
                tipo = datos["tipo"]
                detalle = datos["detalle"]

                print(
                    f"\n---------- Evento de {dispositivo} ----------"
                )
                print(f"{tipo}: {detalle}")

                guardar_evento(datos)

            else:
                print("Evento MQTT rechazado: datos invalidos.")

        elif mensaje.topic == TOPICO_COMANDOS:

            if validar_comando(datos):
                dispositivo = datos["dispositivo"]
                accion = datos["accion"]
                valor = datos["valor"]
                resultado = datos["resultado"]

                print(
                    f"\n---------- Comando de {dispositivo} ----------"
                )
                print(f"{accion} = {valor} -> {resultado}")

                guardar_comando(datos)

            else:
                print("Comando MQTT rechazado: datos invalidos.")

        else:
            print("Mensaje recibido desde un topico desconocido.")

    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print("Error al interpretar el mensaje MQTT:", error)



def reenviar_orden_de_la_nube(accion, valor):
    """
    Recibe una orden desde Adafruit IO y la envía a la Pico W
    utilizando el cliente MQTT conectado a EMQX.
    """

    global cliente_emqx

    if cliente_emqx is None or not cliente_emqx.is_connected():
        print("No hay conexion con EMQX para enviar el comando.")
        return False

    return enviar_comando(cliente_emqx, accion, valor)


def iniciar_gateway():
    """Inicializa SQLite y establece las conexiones MQTT."""

    global cliente_emqx

    # Crear las tablas de SQLite si todavía no existen.
    inicializar_base_datos()

    # Crear el cliente MQTT de EMQX.
    cliente = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir_mensaje

    # Guardar la referencia para enviar comandos desde la nube.
    cliente_emqx = cliente

    try:
        print("Conectando al broker:", MQTT_BROKER)

        # Conectar primero con EMQX.
        cliente.connect(MQTT_BROKER, MQTT_PUERTO, 60)

        # Iniciar la conexión independiente con Adafruit IO.
        nube.conectar(reenviar_orden_de_la_nube)

        # Mantener el cliente EMQX procesando mensajes.
        cliente.loop_forever()

    except (OSError, ValueError, RuntimeError) as error:
        print("Error al iniciar el Gateway:", error)

    finally:
        nube.desconectar()
        cliente.disconnect()
        cliente_emqx = None


def enviar_comando(cliente, accion, valor):
    """Publica un comando validado en el tópico /control."""

    if accion not in ("ventilador", "luz_cultivo", "modo"):
        print("Error: accion no permitida.")
        return False

    if accion == "modo":
        if valor not in ("auto", "manual"):
            print("Error: modo debe ser auto o manual.")
            return False
    else:
        if type(valor) is not bool:
            print("Error: valor debe ser True o False.")
            return False

    comando = {
        "auth_token": TOKEN,
        "accion": accion,
        "valor": valor
    }

    mensaje = json.dumps(comando)

    resultado = cliente.publish(
        TOPICO_CONTROL,
        payload=mensaje
    )

    if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
        print("Error al publicar comando MQTT.")
        return False

    resultado.wait_for_publish(timeout=5)

    if resultado.is_published():
        print("Comando MQTT publicado:", comando)
        return True

    print("Error: no se confirmo la publicacion MQTT.")
    return False


if __name__ == "__main__":
    iniciar_gateway()
