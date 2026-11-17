"""
Prueba de gateway/nube.py sin la placa ni el gateway de Juan.

Se conecta a Adafruit IO con un callback de prueba y cada 5 s (lo mismo que
la placa) le pasa a nube.enviar_lectura() una lectura inventada. Sirve para:
- Ver en el dashboard cómo cambian temperatura, humedad, luz y estados.
- Comprobar que solo se envía una de cada tres lecturas (límite de 15 s).
- Presionar los botones del dashboard y ver en la terminal la orden traducida.

Ejecutar desde la raíz del proyecto:  py -m gateway.prueba_nube
Se detiene con Ctrl+C.
"""
import random
import time

from gateway import nube

INTERVALO_PRUEBA_S = 5      # Igual que INTERVALO_LECTURA_MS de la placa


def mostrar_comando(accion, valor):
    """Callback de prueba: muestra lo que el gateway publicaría en /control."""
    print("  -> El gateway publicaría en /control:", {"accion": accion, "valor": valor})


def lectura_inventada(numero):
    """
    Devuelve una lectura con el formato de /lecturas (contrato, sección 3).
    La temperatura sube y baja alrededor de 30 °C para que el ventilador cambie.
    """
    temperatura = round(28 + random.uniform(0, 4), 1)
    luz = random.randint(20, 80)
    return {
        "dispositivo": "pico01",
        "timestamp": int(time.time()),
        "temperatura": temperatura,
        "humedad": round(random.uniform(55, 75), 1),
        "luz": luz,
        "ventilador": temperatura > 30.0,
        "luz_cultivo": luz < 40,
        "modo": "auto",
    }


def main():
    """Conecta, espera la conexión y envía lecturas hasta que se presione Ctrl+C."""
    nube.conectar(mostrar_comando)
    for _ in range(10):
        if nube.hay_conexion():
            break
        time.sleep(1)  # La conexión se hace en otro hilo: se le da tiempo
    if not nube.hay_conexion():
        print("No se pudo conectar a Adafruit IO. Revisa Internet y secretos.py.")
        nube.desconectar()
        return

    numero = 1
    try:
        while True:
            lectura = lectura_inventada(numero)
            enviada = nube.enviar_lectura(lectura)
            if enviada:
                estado = "ENVIADA"
            else:
                estado = "ignorada (aún no pasan 15 s)"
            print("Lectura", numero, "-", lectura["temperatura"], "°C, luz", lectura["luz"], "% ->", estado)
            numero = numero + 1
            time.sleep(INTERVALO_PRUEBA_S)
    except KeyboardInterrupt:
        print("\nPrueba terminada.")
    finally:
        nube.desconectar()


if __name__ == "__main__":
    main()
