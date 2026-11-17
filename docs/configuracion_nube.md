# Configuración de la nube (Adafruit IO)

Pasos para dejar listo el dashboard y conectar el gateway. Se hace una sola vez, en la cuenta de quien vaya a correr el gateway en la sustentación. Toma unos 20 minutos.

## 1. Crear la cuenta

1. Entrar a <https://io.adafruit.com> y crear una cuenta gratis (o entrar con una cuenta de Adafruit).
2. El plan gratis alcanza: 10 feeds, 5 dashboards, 30 datos por minuto y 30 días de historial. Usamos 9 feeds y 1 dashboard.

## 2. Crear los feeds

Un feed es una serie de valores con su fecha y hora, parecido a una tabla de una sola columna. En **Feeds → New Feed**, crear estos nueve con el nombre exacto (en minúsculas y con guiones):

| Feed | Quién escribe | Qué guarda | Valores |
|---|---|---|---|
| `temperatura` | Gateway | Temperatura del DHT22 | número en °C, ej. `28.4` |
| `humedad` | Gateway | Humedad relativa | número en %, ej. `62.1` |
| `luz` | Gateway | Luz de la fotorresistencia | 0 a 100 % |
| `estado-ventilador` | Gateway | Estado real del ventilador | `1` encendido, `0` apagado |
| `estado-luz-cultivo` | Gateway | Estado real de la luz de cultivo | `1` / `0` |
| `estado-modo` | Gateway | Modo de la placa | `auto` / `manual` |
| `control-ventilador` | Botón del dashboard | Orden para el ventilador | `ON` / `OFF` |
| `control-luz-cultivo` | Botón del dashboard | Orden para la luz de cultivo | `ON` / `OFF` |
| `control-modo` | Botón del dashboard | Orden de modo | `auto` / `manual` |

Estos nombres están en `gateway/config.py` (`FEED_...`). Si se cambia uno en Adafruit IO, hay que cambiarlo también ahí. Para confirmar la clave (*key*) de un feed: abrir el feed → **Feed Info**.

> **Por qué hay feeds de estado y de control por separado:** si el botón y el estado fueran el mismo feed, cada vez que el gateway publica el estado lo recibiría de vuelta como si fuera una orden, y la placa pasaría a modo manual sola.

## 3. Crear el dashboard

1. **Dashboards → New Dashboard**. Nombre: `Invernadero`. Descripción: `Parcial 2 - DS8`.
2. Abrir el dashboard, ícono del engranaje → **Create New Block**. Por cada bloque: elegir el tipo, marcar el feed, **Next step**, llenar la configuración y **Create block**.

### Bloques de monitoreo (solo muestran datos)

| Bloque | Tipo | Feed | Configuración |
|---|---|---|---|
| Temperatura | Gauge | `temperatura` | Min 0, Max 50, Label `°C`. Opcional: Low warning 15 / High warning 30 |
| Humedad | Gauge | `humedad` | Min 0, Max 100, Label `%` |
| Luz | Gauge | `luz` | Min 0, Max 100, Label `%`. Opcional: Low warning 40 |
| Historial | Line Chart | `temperatura`, `humedad` y `luz` | Show History: 1 hour. Y-Axis Min 0, Max 100 |
| Ventilador | Indicator | `estado-ventilador` | Condición `=` `1`. On Color verde, Off Color gris |
| Luz de cultivo | Indicator | `estado-luz-cultivo` | Condición `=` `1`. On Color amarillo, Off Color gris |
| Modo actual | Text | `estado-modo` | Font size grande |

Los umbrales opcionales (30 °C y 40 %) son los mismos de `placa/config.py`, así el color del medidor coincide con lo que hace la regla automática.

### Bloques de control (envían órdenes)

| Bloque | Tipo | Feed | Button On Text / Value | Button Off Text / Value |
|---|---|---|---|---|
| Encender ventilador | Toggle | `control-ventilador` | `Encendido` / `ON` | `Apagado` / `OFF` |
| Encender luz de cultivo | Toggle | `control-luz-cultivo` | `Encendida` / `ON` | `Apagada` / `OFF` |
| Modo | Toggle | `control-modo` | `Automático` / `auto` | `Manual` / `manual` |

Los **Value** deben ser exactamente esos: son los que `nube.py` sabe traducir. Los **Text** son solo lo que se ve en el botón.

3. Ordenar los bloques arrastrándolos (sugerencia: medidores arriba, gráfica al medio, indicadores y botones abajo) y presionar **Save Layout**.
4. Opcional, para que el profesor lo vea sin cuenta: en el engranaje, abrir la privacidad del dashboard y marcarlo como público. Los visitantes solo ven los datos; los botones quedan para el dueño de la cuenta.

## 4. Obtener la clave y crear `secretos.py`

1. En Adafruit IO, presionar el ícono de la **llave amarilla** (arriba a la derecha). Aparecen el **Username** y la **Active Key** (empieza con `aio_`).
2. En la PC, desde la raíz del proyecto, copiar la plantilla:

   ```powershell
   copy gateway\secretos_ejemplo.py gateway\secretos.py
   ```

3. Abrir `gateway/secretos.py` y reemplazar los dos valores:

   ```python
   ADAFRUIT_IO_USUARIO = "el_usuario_de_adafruit"
   ADAFRUIT_IO_CLAVE = "aio_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

4. Comprobar que Git **no** lo vea: `git status` no debe mostrar `gateway/secretos.py` (está en `.gitignore`).

La clave se pasa a los compañeros solo por mensaje privado, nunca en el repositorio ni en el chat del grupo. Si se filtra, en la ventana de la llave se presiona **Regenerate Key** y se actualiza `secretos.py`.

## 5. Probar la conexión sin la placa ni el gateway

```powershell
py -m pip install -r requirements.txt
py -m gateway.prueba_nube
```

Resultado esperado:

```text
Conectando a Adafruit IO: io.adafruit.com
Conectado a Adafruit IO como el_usuario_de_adafruit
Escuchando el feed: control-ventilador
Escuchando el feed: control-luz-cultivo
Escuchando el feed: control-modo
Nube: lectura enviada a Adafruit IO (6 datos)
Lectura 1 - 29.8 °C, luz 66 % -> ENVIADA
Lectura 2 - 28.6 °C, luz 63 % -> ignorada (aún no pasan 15 s)
Lectura 3 - 31.3 °C, luz 53 % -> ignorada (aún no pasan 15 s)
Nube: lectura enviada a Adafruit IO (3 datos)
Lectura 4 - 29.8 °C, luz 64 % -> ENVIADA
```

Mientras corre:
- Los medidores y la gráfica del dashboard se mueven cada 15 s.
- Al presionar un botón, la terminal muestra la orden traducida, por ejemplo:

  ```text
  Nube: orden del dashboard -> ventilador True
    -> El gateway publicaría en /control: {'accion': 'ventilador', 'valor': True}
  ```

Se detiene con `Ctrl+C`.

## 6. Cómo lo usa el gateway

`gateway/main.py` (Juan) solo necesita dos llamadas, definidas en `docs/contrato.md`, sección 5:

```python
from gateway import nube

def al_recibir_comando(accion, valor):
    """nube.py la llama cuando alguien presiona un botón del dashboard."""
    orden = {"auth_token": config.TOKEN, "accion": accion, "valor": valor}
    cliente_emqx.publish(config.TOPICO_CONTROL, json.dumps(orden))

nube.conectar(al_recibir_comando)   # una vez, al arrancar

# ...y dentro del manejo de cada mensaje de /lecturas, después de guardar_lectura():
nube.enviar_lectura(lectura)
```

Detalles para la integración:
- `conectar()` no bloquea: abre su propio hilo y reconecta solo si se cae Internet. Por eso `al_recibir_comando` se ejecuta en ese hilo. Publicar con paho desde otro hilo es seguro.
- Si `al_recibir_comando` lanza un error, `nube.py` lo muestra y sigue escuchando.
- `enviar_lectura()` devuelve `True` si envió y `False` si la ignoró (no pasaron 15 s o no hay conexión). Nunca lanza error por falta de red, así que no detiene el guardado en SQLite.
- `nube.desconectar()` cierra la conexión; sirve al salir con `Ctrl+C`.
- `nube.py` no agrega librerías: usa `paho-mqtt`, que ya está en `requirements.txt`.

## 7. Problemas comunes

| Mensaje en la terminal | Causa | Solución |
|---|---|---|
| `Falta gateway/secretos.py` | No se copió la plantilla | Paso 4 |
| `gateway/secretos.py todavía tiene la clave de ejemplo` | Se copió pero no se editó | Escribir la Active Key real |
| `Adafruit IO rechazó la conexión: Bad user name or password` | Usuario o clave mal escritos, o la clave se regeneró | Copiarlos otra vez desde la llave amarilla |
| `Adafruit IO limitó los envíos: …` | Más de 30 datos por minuto (otro programa usa la misma cuenta, o muchos clics) | Esperar un minuto; cerrar otras pruebas con la misma cuenta |
| `Adafruit IO reportó un error: …` | Un feed no existe o tiene otro nombre | Revisar los nombres del paso 2 contra `gateway/config.py` |
| `Nube: valor no reconocido en control-modo -> ON` | El toggle de modo quedó con los valores por defecto | Editar el bloque: On Value `auto`, Off Value `manual` |
| `CERTIFICATE_VERIFY_FAILED` o se queda en `Conectando…` | La red bloquea el puerto 8883 o inspecciona TLS (pasa en algunas redes de la universidad) | Probar con otra red; solo para probar, cambiar `ADAFRUIT_PUERTO` a `1883` en `gateway/config.py` |
