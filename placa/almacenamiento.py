"""
Resiliencia offline para guardar lecturas en memoria flash cuando cae la red.

Se conecta con placa/config.py para el nombre del archivo y límite de cola,
y es llamado por placa/main.py durante desconexiones y reconexiones.
"""

import json
import os
import config


def cargar_lecturas_pendientes():
    """
    Lee del archivo local la lista de lecturas guardadas durante una caída.
    No recibe parámetros. Devuelve una lista de diccionarios de lecturas.
    """
    try:
        if config.ARCHIVO_PENDIENTES not in os.listdir():
            return []
        with open(config.ARCHIVO_PENDIENTES, "r") as archivo:
            datos = json.load(archivo)
            if isinstance(datos, list):
                return datos
            return []
    except Exception as error:
        print("Error al leer lecturas pendientes:", error)
        return []


def guardar_lectura_pendiente(lectura):
    """
    Agrega una lectura no enviada al archivo local de respaldo.
    Recibe el diccionario de la lectura. Devuelve la cantidad total acumulada.
    """
    pendientes = cargar_lecturas_pendientes()

    # Evita llenar la memoria flash de la Pico W si la caída dura mucho tiempo
    if len(pendientes) >= config.MAX_LECTURAS_PENDIENTES:
        pendientes.pop(0)

    pendientes.append(lectura)

    try:
        with open(config.ARCHIVO_PENDIENTES, "w") as archivo:
            json.dump(pendientes, archivo)
        print("Lectura guardada localmente. Pendientes:", len(pendientes))
    except Exception as error:
        print("Error al guardar lectura pendiente:", error)

    return len(pendientes)


def limpiar_lecturas_pendientes():
    """
    Borra las lecturas acumuladas una vez que fueron reenviadas al broker.
    No recibe parámetros. No devuelve ningún valor.
    """
    try:
        if config.ARCHIVO_PENDIENTES in os.listdir():
            os.remove(config.ARCHIVO_PENDIENTES)
    except Exception as error:
        print("Error al limpiar archivo de pendientes:", error)
