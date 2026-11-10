
"""
main.py

Gateway MQTT del Invernadero IoT.

Se conecta al broker EMQX para recibir los mensajes
enviados por la Raspberry Pi Pico W.
"""

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

import json

from gateway.base_datos import (
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



def al_conectar(cliente, datos_usuario, flags, codigo, propiedades):
    """Se suscribe a los tópicos MQTT del invernadero."""

    if codigo == 0:
        print("Gateway conectado correctamente al broker MQTT.")

        # Suscribirse a las lecturas de sensores
        cliente.subscribe(TOPICO_LECTURAS)
        print("Suscrito al tópico:", TOPICO_LECTURAS)

        # Suscribirse a los eventos del invernadero
        cliente.subscribe(TOPICO_EVENTOS)
        print("Suscrito al tópico:", TOPICO_EVENTOS)

        # Suscribirse a las respuestas de comandos
        cliente.subscribe(TOPICO_COMANDOS)
        print("Suscrito al tópico:", TOPICO_COMANDOS)

    else:
        print("Error de conexion MQTT. Codigo:", codigo)





def al_recibir_mensaje(cliente, datos_usuario, mensaje):
    """Recibe mensajes MQTT y los guarda según su tópico."""
    try:
        contenido = mensaje.payload.decode("utf-8")
        datos = json.loads(contenido)

        if not isinstance(datos, dict):
            print("Error: el mensaje JSON debe ser un objeto.")
            return

        print("\n===== MENSAJE MQTT RECIBIDO =====")
        print("Topico:", mensaje.topic)
        print("Contenido:", datos)

        
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
                guardar_lectura(datos)
            else:
                print("Lectura MQTT rechazada: datos invalidos.")

        
        elif mensaje.topic == TOPICO_EVENTOS:

            if validar_evento(datos):
                guardar_evento(datos)
            else:
                print("Evento MQTT rechazado: datos invalidos.")


        
        elif mensaje.topic == TOPICO_COMANDOS:

            if validar_comando(datos):
                guardar_comando(datos)
            else:
                print("Comando MQTT rechazado: datos invalidos.")


        else:
            print("Mensaje recibido desde un topico desconocido.")

    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print("Error al interpretar el mensaje MQTT:", error)





def iniciar_gateway():
    """Crea el cliente MQTT y establece la conexión."""

    # Crear un cliente MQTT con un identificador propio
    cliente = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    # Indicar qué función ejecutar al conectarse
    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir_mensaje

    try:
        print("Conectando al broker:", MQTT_BROKER)

        # Establecer conexión con EMQX
        cliente.connect(MQTT_BROKER, MQTT_PUERTO, 60)

        # Mantener el cliente procesando mensajes MQTT
        cliente.loop_forever()

    except (OSError, ValueError) as error:
        print("Error al iniciar el Gateway:", error)


def enviar_comando(cliente, accion, valor):


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
