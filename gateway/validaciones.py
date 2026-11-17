
"""
Validaciones de mensajes MQTT del Invernadero IoT.

Verifica que los mensajes recibidos tengan los
campos obligatorios antes de almacenarlos.
"""


def validar_campos(datos, campos_obligatorios):
    """Verifica que un mensaje contenga los campos requeridos."""

    if not isinstance(datos, dict):
        print("Error: el mensaje debe ser un diccionario.")
        return False

    for campo in campos_obligatorios:

        if campo not in datos:
            print("Error: falta el campo obligatorio:", campo)
            return False


    return True


def validar_tipos_lectura(lectura):
    """Verifica los tipos de datos de una lectura MQTT."""

    if not isinstance(lectura["dispositivo"], str):
        print("Error: dispositivo debe ser texto.")
        return False

    if type(lectura["timestamp"]) is not int:
        print("Error: timestamp debe ser un numero entero.")
        return False

    if lectura["temperatura"] is not None:
        if type(lectura["temperatura"]) not in (int, float):
            print("Error: temperatura debe ser un numero.")
            return False

    if lectura["humedad"] is not None:
        if type(lectura["humedad"]) not in (int, float):
            print("Error: humedad debe ser un numero.")
            return False

    if type(lectura["luz"]) is not int:
        print("Error: luz debe ser un numero entero.")
        return False

    if type(lectura["ventilador"]) is not bool:
        print("Error: ventilador debe ser True o False.")
        return False

    if type(lectura["luz_cultivo"]) is not bool:
        print("Error: luz_cultivo debe ser True o False.")
        return False

    if not isinstance(lectura["modo"], str):
        print("Error: modo debe ser texto.")
        return False

    return True


def validar_valores_lectura(lectura):
    """Verifica los rangos y valores permitidos de una lectura."""

    if lectura["dispositivo"] != "pico01":
        print("Error: dispositivo no reconocido.")
        return False

    if lectura["timestamp"] < 0:
        print("Error: timestamp no puede ser negativo.")
        return False

    if not 0 <= lectura["luz"] <= 100:
        print("Error: luz debe estar entre 0 y 100.")
        return False

    if lectura["humedad"] is not None:
        if not 0 <= lectura["humedad"] <= 100:
            print("Error: humedad debe estar entre 0 y 100.")
            return False

    if lectura["modo"] not in ("auto", "manual"):
        print("Error: modo debe ser auto o manual.")
        return False

    return True


def validar_evento(evento):
    """Verifica los campos y valores de un evento MQTT."""

    campos = [
        "dispositivo",
        "timestamp",
        "tipo",
        "detalle"
    ]

    if not validar_campos(evento, campos):
        return False

    if evento["dispositivo"] != "pico01":
        print("Error: dispositivo no reconocido.")
        return False

    if type(evento["timestamp"]) is not int:
        print("Error: timestamp debe ser un entero.")
        return False

    if evento["timestamp"] < 0:
        print("Error: timestamp no puede ser negativo.")
        return False

    if evento["tipo"] not in ("regla_automatica", "reconexion"):
        print("Error: tipo de evento no permitido.")
        return False

    if not isinstance(evento["detalle"], str):
        print("Error: detalle debe ser texto.")
        return False

    return True


def validar_comando(comando):
    """Valida las confirmaciones de comandos recibidas por MQTT."""

    campos = [
        "dispositivo",
        "timestamp",
        "accion",
        "valor",
        "resultado",
        "motivo"
    ]

    if not validar_campos(comando, campos):
        return False

    if comando["dispositivo"] != "pico01":
        print("Error: dispositivo no reconocido.")
        return False

    if type(comando["timestamp"]) is not int:
        print("Error: timestamp debe ser un entero.")
        return False

    if comando["timestamp"] < 0:
        print("Error: timestamp no puede ser negativo.")
        return False

    
    if comando["resultado"] not in ("ejecutado", "rechazado"):
        print("Error: resultado no permitido.")
        return False

    if not isinstance(comando["accion"], str):
        print("Error: accion debe ser texto.")
        return False

    if comando["resultado"] == "ejecutado":

        if comando["accion"] not in ("ventilador", "luz_cultivo", "modo"):
            print("Error: accion no permitida.")
            return False

        if comando["accion"] == "modo":
            if comando["valor"] not in ("auto", "manual"):
                print("Error: modo debe ser auto o manual.")
                return False
        else:
            if type(comando["valor"]) is not bool:
                print("Error: valor debe ser True o False.")
                return False


    if not isinstance(comando["motivo"], str):
        print("Error: motivo debe ser texto.")
        return False

    return True

