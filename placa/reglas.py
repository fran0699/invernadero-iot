"""
Reglas automáticas del invernadero (solo actúan en modo automático).

En cada lectura, el código de José llama a aplicar_reglas() con lo que
devolvió sensores.leer_sensores(). Por cada actuador que cambia, devuelve
un texto que José publica como evento "regla_automatica".
Los umbrales vienen de config.py.
"""
import actuadores
import config


def regla_ventilador(temperatura):
    """
    Enciende el ventilador si la temperatura supera el umbral; si no, lo apaga.
    Devuelve un texto si el ventilador cambió, o None si quedó igual.
    """
    if temperatura is None:
        return None  # El DHT22 falló: sin dato, mejor no cambiar nada
    debe_encender = temperatura > config.TEMPERATURA_MAXIMA
    if debe_encender == actuadores.estado_actuadores()["ventilador"]:
        return None  # Ya está como debe estar
    actuadores.cambiar_ventilador(debe_encender)
    if debe_encender:
        return f"Temperatura {temperatura} C mayor que {config.TEMPERATURA_MAXIMA} C: ventilador encendido"
    return f"Temperatura {temperatura} C no supera {config.TEMPERATURA_MAXIMA} C: ventilador apagado"


def regla_luz(luz):
    """
    Enciende la luz de cultivo si la luz está por debajo del umbral; si no, la apaga.
    Devuelve un texto si la luz de cultivo cambió, o None si quedó igual.
    """
    debe_encender = luz < config.LUZ_MINIMA
    if debe_encender == actuadores.estado_actuadores()["luz_cultivo"]:
        return None  # Ya está como debe estar
    actuadores.cambiar_luz_cultivo(debe_encender)
    if debe_encender:
        return f"Luz {luz} % menor que {config.LUZ_MINIMA} %: luz de cultivo encendida"
    return f"Luz {luz} % no es menor que {config.LUZ_MINIMA} %: luz de cultivo apagada"


def aplicar_reglas(lectura):
    """
    Aplica las dos reglas a una lectura.
    Recibe {"temperatura": ..., "humedad": ..., "luz": ...}.
    Devuelve una lista con un texto por cada actuador que cambió (vacía si nada cambió).
    """
    cambios = []
    texto = regla_ventilador(lectura["temperatura"])
    if texto:
        cambios.append(texto)
    texto = regla_luz(lectura["luz"])
    if texto:
        cambios.append(texto)
    return cambios
