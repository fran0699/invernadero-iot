
"""
base_datos.py

Gestiona la base de datos SQLite del Invernadero IoT.
Inicializa las tablas utilizando el archivo crear_tablas.sql.
"""

import sqlite3
import json
from pathlib import Path

from gateway.config import RUTA_BASE_DATOS


# Obtener la carpeta principal del proyecto
RUTA_PROYECTO = Path(__file__).resolve().parent.parent

# Obtener la carpeta del gateway
RUTA_GATEWAY = Path(__file__).resolve().parent

# Obtener la ruta de la base de datos desde config.py
RUTA_BD = Path(RUTA_BASE_DATOS)

# Ubicar la base de datos dentro de gateway
if not RUTA_BD.is_absolute():
    RUTA_BD = RUTA_GATEWAY / RUTA_BD

# Ubicar el archivo SQL
RUTA_SQL = RUTA_PROYECTO / "sql" / "crear_tablas.sql"


def inicializar_base_datos():
    """Crea las tablas de SQLite si todavía no existen."""

    try:
        # Leer el archivo SQL
        with open(RUTA_SQL, "r", encoding="utf-8") as archivo:
            instrucciones_sql = archivo.read()

        # Abrir o crear la base de datos
        with sqlite3.connect(RUTA_BD) as conexion:

            # Ejecutar las instrucciones SQL
            conexion.executescript(instrucciones_sql)

        print("Base de datos inicializada correctamente.")
        return True

    except (sqlite3.Error, OSError) as error:
        print("Error al inicializar la base de datos:", error)
        return False


def guardar_lectura(lectura):
    """Guarda una lectura de sensores en SQLite."""

    try:
        # Abrir la conexión con la base de datos
        with sqlite3.connect(RUTA_BD) as conexion:

            # Insertar los datos recibidos
            conexion.execute(
                """
                INSERT INTO lecturas (
                    dispositivo,
                    timestamp,
                    temperatura,
                    humedad,
                    luz,
                    ventilador,
                    luz_cultivo,
                    modo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lectura["dispositivo"],
                    lectura["timestamp"],
                    lectura["temperatura"],
                    lectura["humedad"],
                    lectura["luz"],
                    int(lectura["ventilador"]),
                    int(lectura["luz_cultivo"]),
                    lectura["modo"]
                )
            )

        print("Lectura guardada correctamente.")
        return True

    except (sqlite3.Error, KeyError, TypeError, ValueError) as error:
        print("Error al guardar la lectura:", error)
        return False


def guardar_evento(evento):
    """Guarda un evento del invernadero en SQLite."""

    try:
        # Abrir la conexión con SQLite
        with sqlite3.connect(RUTA_BD) as conexion:

            # Insertar el evento recibido
            conexion.execute(
                """
                INSERT INTO eventos (
                    dispositivo,
                    timestamp,
                    tipo,
                    detalle
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    evento["dispositivo"],
                    evento["timestamp"],
                    evento["tipo"],
                    evento["detalle"]
                )
            )

        print("Evento guardado correctamente.")
        return True

    except (sqlite3.Error, KeyError, TypeError, ValueError) as error:
        print("Error al guardar el evento:", error)
        return False


def guardar_comando(comando):
    """Guarda la respuesta de un comando MQTT en SQLite."""

    try:
        # Convertir el valor recibido a texto para SQLite
        valor = json.dumps(comando["valor"])

        # Abrir la conexión con la base de datos
        with sqlite3.connect(RUTA_BD) as conexion:

            # Insertar la respuesta del comando
            conexion.execute(
                """
                INSERT INTO comandos (
                    dispositivo,
                    timestamp,
                    accion,
                    valor,
                    resultado,
                    motivo
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    comando["dispositivo"],
                    comando["timestamp"],
                    comando["accion"],
                    valor,
                    comando["resultado"],
                    comando["motivo"]
                )
            )

        print("Comando guardado correctamente.")
        return True

    except (sqlite3.Error, KeyError, TypeError, ValueError) as error:
        print("Error al guardar el comando:", error)
        return False


if __name__ == "__main__":
    inicializar_base_datos()
