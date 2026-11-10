"""
Programa principal del Invernadero IoT en la Raspberry Pi Pico W.

Coordina los módulos de hardware (sensores, actuadores, reglas) de Francisco
con los módulos de red, MQTT y almacenamiento offline de José.
"""

import json
import time
from machine import Timer
import config
import red
import almacenamiento
import conexion_mqtt
import sensores
import actuadores
import reglas

# Estado global sencillo para que sea fácil de seguir en pantalla
modo_operacion = "auto"
cliente_mqtt = None
lectura_solicitada = False
estaba_desconectado = False


def solicitar_lectura(temporizador):
    """
    Callback del Timer que levanta la bandera cada 5 segundos.
    Recibe el objeto Timer. No devuelve nada para no bloquear la interrupción.
    """
    global lectura_solicitada
    lectura_solicitada = True


def validar_y_ejecutar_orden(datos):
    """
    Verifica el token y aplica la acción pedida sobre actuadores o modo.
    Recibe el diccionario JSON del comando. Devuelve tupla (resultado, motivo).
    """
    global modo_operacion

    token_recibido = datos.get("auth_token")
    if token_recibido != config.TOKEN:
        return ("rechazado", "token invalido")

    accion = datos.get("accion")
    valor = datos.get("valor")

    if accion == "ventilador" and type(valor) is bool:
        actuadores.cambiar_ventilador(valor)
        modo_operacion = "manual"
        return ("ejecutado", "")

    if accion == "luz_cultivo" and type(valor) is bool:
        actuadores.cambiar_luz_cultivo(valor)
        modo_operacion = "manual"
        return ("ejecutado", "")

    if accion == "modo" and valor in ("auto", "manual"):
        modo_operacion = valor
        return ("ejecutado", "")

    return ("rechazado", "accion desconocida")


def al_recibir_control(topico_bytes, mensaje_bytes):
    """
    Procesa los mensajes que llegan al tópico /control y responde en /comandos.
    Recibe tópico y mensaje en bytes desde umqtt. No devuelve ningún valor.
    """
    global cliente_mqtt

    try:
        texto = mensaje_bytes.decode("utf-8")
        datos = json.loads(texto)
    except Exception:
        conexion_mqtt.publicar_respuesta_comando(
            cliente_mqtt, "", None, "rechazado", "mensaje no es JSON"
        )
        return

    accion = datos.get("accion", "")
    valor = datos.get("valor", None)
    resultado, motivo = validar_y_ejecutar_orden(datos)

    conexion_mqtt.publicar_respuesta_comando(
        cliente_mqtt, accion, valor, resultado, motivo
    )
    print("Orden procesada:", accion, "->", resultado, motivo)


def reenviar_pendientes_y_notificar():
    """
    Envía las lecturas guardadas durante una caída y publica el evento reconexion.
    No recibe parámetros. Devuelve True si todo se envió correctamente.
    """
    global cliente_mqtt

    pendientes = almacenamiento.cargar_lecturas_pendientes()
    cantidad = len(pendientes)

    for lectura in pendientes:
        exito = conexion_mqtt.publicar_lectura(cliente_mqtt, lectura)
        if not exito:
            return False
        time.sleep(0.1)

    almacenamiento.limpiar_lecturas_pendientes()
    detalle = "Se reenviaron " + str(cantidad) + " lecturas guardadas"
    conexion_mqtt.publicar_evento(cliente_mqtt, "reconexion", detalle)
    print("Reconexión completada:", detalle)
    return True


def asegurar_conexion():
    """
    Verifica que Wi-Fi y MQTT estén activos; si cayeron, intenta reconectar.
    No recibe parámetros. Devuelve True si hay conexión lista para publicar.
    """
    global cliente_mqtt, estaba_desconectado

    if not red.wifi_conectado():
        estaba_desconectado = True
        cliente_mqtt = None
        if not red.conectar_wifi():
            return False
        red.sincronizar_hora_ntp()

    if cliente_mqtt is None:
        cliente_mqtt = conexion_mqtt.conectar_mqtt(al_recibir_control)
        if cliente_mqtt is None:
            estaba_desconectado = True
            return False

        if estaba_desconectado:
            if reenviar_pendientes_y_notificar():
                estaba_desconectado = False

    return True


def construir_mensaje_lectura(datos_sensores, estado_actual):
    """
    Une las lecturas de sensores, el estado de actuadores y el modo en el JSON.
    Recibe diccionarios de sensores y actuadores. Devuelve el diccionario final.
    """
    return {
        "dispositivo": config.DISPOSITIVO,
        "timestamp": red.obtener_timestamp(),
        "temperatura": datos_sensores["temperatura"],
        "humedad": datos_sensores["humedad"],
        "luz": datos_sensores["luz"],
        "ventilador": estado_actual["ventilador"],
        "luz_cultivo": estado_actual["luz_cultivo"],
        "modo": modo_operacion
    }


def procesar_ciclo_lectura():
    """
    Lee sensores, aplica reglas si está en modo auto y publica o guarda offline.
    No recibe parámetros. No devuelve ningún valor.
    """
    global cliente_mqtt, estaba_desconectado

    datos_sensores = sensores.leer_sensores()
    eventos_reglas = []

    if modo_operacion == "auto":
        eventos_reglas = reglas.aplicar_reglas(datos_sensores)

    estado_actual = actuadores.estado_actuadores()
    lectura = construir_mensaje_lectura(datos_sensores, estado_actual)

    if asegurar_conexion():
        enviado = conexion_mqtt.publicar_lectura(cliente_mqtt, lectura)
        if enviado:
            print("Lectura publicada:", lectura)
            for texto_evento in eventos_reglas:
                conexion_mqtt.publicar_evento(
                    cliente_mqtt, "regla_automatica", texto_evento
                )
            return

    # Si falló el envío o no hay red, se guarda localmente con su timestamp original
    estaba_desconectado = True
    cliente_mqtt = None
    almacenamiento.guardar_lectura_pendiente(lectura)


def iniciar():
    """
    Inicializa la red, el reloj NTP, el cliente MQTT y el Timer de muestreo.
    No recibe parámetros. Corre el bucle principal indefinidamente.
    """
    global lectura_solicitada, cliente_mqtt, estaba_desconectado

    if red.conectar_wifi():
        red.sincronizar_hora_ntp()
        cliente_mqtt = conexion_mqtt.conectar_mqtt(al_recibir_control)
        if cliente_mqtt is not None:
            pendientes = almacenamiento.cargar_lecturas_pendientes()
            if len(pendientes) > 0:
                reenviar_pendientes_y_notificar()
        else:
            estaba_desconectado = True
    else:
        estaba_desconectado = True

    temporizador = Timer(-1)
    temporizador.init(
        period=config.INTERVALO_LECTURA_MS,
        mode=Timer.PERIODIC,
        callback=solicitar_lectura
    )

    while True:
        if cliente_mqtt is not None:
            sigue_conectado = conexion_mqtt.revisar_mensajes(cliente_mqtt)
            if not sigue_conectado:
                estaba_desconectado = True
                cliente_mqtt = None

        if lectura_solicitada:
            lectura_solicitada = False
            procesar_ciclo_lectura()

        time.sleep(0.1)


if __name__ == "__main__":
    iniciar()
