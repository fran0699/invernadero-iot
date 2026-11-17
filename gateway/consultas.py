
"""
consultas.py

Permite consultar los registros almacenados
en SQLite del proyecto Invernadero IoT.
"""

import sqlite3
from gateway.base_datos import RUTA_BD


def consultar_lecturas():
    """Consulta y muestra las lecturas almacenadas."""

    try:
        # Abrir la conexión con SQLite
        with sqlite3.connect(RUTA_BD) as conexion:

            # Recuperar las últimas 10 lecturas
            registros = conexion.execute(
                """
                SELECT
                    id,
                    dispositivo,
                    temperatura,
                    humedad,
                    luz,
                    ventilador,
                    luz_cultivo,
                    modo
                FROM lecturas
                ORDER BY id DESC
                LIMIT 10
                """
            ).fetchall()

        # Verificar si existen registros
        if not registros:
            print("No hay lecturas registradas.")
            return

        # Mostrar las lecturas encontradas
        print("\n===== HISTORIAL DE LECTURAS =====")

        for registro in registros:
            print(
                "ID:", registro[0],
                "| Dispositivo:", registro[1],
                "| Temperatura:", registro[2],
                "| Humedad:", registro[3],
                "| Luz:", registro[4],
                "| Ventilador:", registro[5],
                "| Luz cultivo:", registro[6],
                "| Modo:", registro[7]
            )

    except sqlite3.Error as error:
        print("Error al consultar las lecturas:", error)


def consultar_eventos():
    """Consulta y muestra los últimos 10 eventos almacenados."""

    try:
        # Abrir la conexión con SQLite
        with sqlite3.connect(RUTA_BD) as conexion:

            # Recuperar los últimos 10 eventos
            registros = conexion.execute(
                """
                SELECT
                    id,
                    dispositivo,
                    timestamp,
                    tipo,
                    detalle
                FROM eventos
                ORDER BY id DESC
                LIMIT 10
                """
            ).fetchall()

        # Verificar si existen eventos
        if not registros:
            print("No hay eventos registrados.")
            return

        # Mostrar los eventos encontrados
        print("\n===== HISTORIAL DE EVENTOS =====")

        for registro in registros:
            print(
                "ID:", registro[0],
                "| Dispositivo:", registro[1],
                "| Timestamp:", registro[2],
                "| Tipo:", registro[3],
                "| Detalle:", registro[4]
            )

    except sqlite3.Error as error:
        print("Error al consultar los eventos:", error)


def consultar_comandos():
    """Consulta y muestra los últimos 10 comandos almacenados."""

    try:
        # Abrir la conexión con SQLite
        with sqlite3.connect(RUTA_BD) as conexion:

            # Recuperar los últimos 10 comandos
            registros = conexion.execute(
                """
                SELECT
                    id,
                    dispositivo,
                    timestamp,
                    accion,
                    valor,
                    resultado,
                    motivo
                FROM comandos
                ORDER BY id DESC
                LIMIT 10
                """
            ).fetchall()

        # Verificar si existen comandos
        if not registros:
            print("No hay comandos registrados.")
            return

        # Mostrar los comandos encontrados
        print("\n===== HISTORIAL DE COMANDOS =====")

        for registro in registros:
            print(
                "ID:", registro[0],
                "| Dispositivo:", registro[1],
                "| Timestamp:", registro[2],
                "| Accion:", registro[3],
                "| Valor:", registro[4],
                "| Resultado:", registro[5],
                "| Motivo:", registro[6]
            )

    except sqlite3.Error as error:
        print("Error al consultar los comandos:", error)


def mostrar_menu():
    """Muestra el menú para consultar los historiales."""

    while True:
        print("\n====================================")
        print("      INVERNADERO IoT - HISTORIAL")
        print("====================================")
        print("1. Consultar lecturas")
        print("2. Consultar eventos")
        print("3. Consultar comandos")
        print("4. Salir")
        print("====================================")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            consultar_lecturas()

        elif opcion == "2":
            consultar_eventos()

        elif opcion == "3":
            consultar_comandos()

        elif opcion == "4":
            print("Saliendo del historial...")
            break

        else:
            print("Opcion no valida. Intente nuevamente.")


if __name__ == "__main__":
    mostrar_menu()
