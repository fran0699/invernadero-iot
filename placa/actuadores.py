"""
Actuadores del invernadero: relé del ventilador y LED de la luz de cultivo.

Los usan reglas.py (en modo automático) y el código de José que procesa
las órdenes del dashboard. Los pines vienen de config.py.
"""
from machine import Pin

import config

# Pines de salida; value=0 hace que arranquen apagados
rele_ventilador = Pin(config.PIN_VENTILADOR, Pin.OUT, value=0)
led_luz_cultivo = Pin(config.PIN_LUZ_CULTIVO, Pin.OUT, value=0)


def cambiar_ventilador(encendido):
    """Enciende (True) o apaga (False) el ventilador a través del relé."""
    rele_ventilador.value(encendido)


def cambiar_luz_cultivo(encendido):
    """Enciende (True) o apaga (False) la luz de cultivo."""
    led_luz_cultivo.value(encendido)


def estado_actuadores():
    """
    Devuelve el estado actual de los actuadores:
    {"ventilador": bool, "luz_cultivo": bool} (docs/contrato.md, sección 5).
    """
    return {
        "ventilador": rele_ventilador.value() == 1,
        "luz_cultivo": led_luz_cultivo.value() == 1,
    }
