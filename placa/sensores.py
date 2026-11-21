"""
Sensores del invernadero: DHT22 (temperatura y humedad) y fotorresistencia (luz).

Lo usa el código de José: en cada lectura del Timer llama a leer_sensores()
y publica el resultado. Los pines vienen de config.py.
"""
import dht
from machine import ADC, Pin

import config

# Cada sensor se crea una sola vez, cuando se importa este módulo
sensor_dht = dht.DHT22(Pin(config.PIN_DHT22))
sensor_luz = ADC(Pin(config.PIN_LUZ))

# read_u16() devuelve un número entre 0 (0 V) y 65535 (3,3 V)
VALOR_MAXIMO_ADC = 65535


def leer_temperatura_y_humedad():
    """
    Lee el DHT22.
    Devuelve (temperatura en °C, humedad en %), o (None, None) si la lectura
    falla, para que un fallo del sensor no detenga el programa.
    """
    try:
        sensor_dht.measure()
        # El DHT22 mide con un decimal; round() quita restos como 19.300002
        temperatura = round(sensor_dht.temperature(), 1)
        humedad = round(sensor_dht.humidity(), 1)
        return temperatura, humedad
    except OSError:
        return None, None


def leer_luz():
    """
    Lee la fotorresistencia.
    Devuelve la luz en porcentaje: 0 = oscuridad, 100 = máxima luz.
    """
    valor = sensor_luz.read_u16()
    # El voltaje del módulo BAJA cuando hay más luz, por eso se invierte
    porcentaje_oscuridad = valor * 100 // VALOR_MAXIMO_ADC
    return 100 - porcentaje_oscuridad


def leer_sensores():
    """
    Lee todos los sensores.
    Devuelve {"temperatura": float o None, "humedad": float o None, "luz": int},
    el formato fijado en docs/contrato.md (sección 5).
    """
    temperatura, humedad = leer_temperatura_y_humedad()
    return {
        "temperatura": temperatura,
        "humedad": humedad,
        "luz": leer_luz(),
    }
