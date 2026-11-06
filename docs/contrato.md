# Contrato entre módulos

Este documento fija lo que comparten los módulos: los tópicos MQTT, el formato de los mensajes y los nombres de las funciones que un módulo llama de otro. Mientras todos lo respeten, cada uno puede programar y probar su parte sin esperar a los demás.

Si algo de aquí tiene que cambiar, se avisa en el grupo y primero se cambia este archivo, en un PR propio.

## 1. Dueño de cada archivo

Cada archivo tiene un dueño, y solo él lo cambia. Si necesitas un archivo de otro para probar, créalo en tu copia de Wokwi o en tu PC, pero no lo agregues a tu commit.

| Archivo | Dueño | Qué hace |
|---|---|---|
| `placa/config.py` | Compartido | Pines, umbrales, Wi-Fi, broker, tópicos y token |
| `placa/sensores.py` | Francisco | Lee el DHT22 y la fotorresistencia |
| `placa/actuadores.py` | Francisco | Enciende y apaga el relé del ventilador y el LED |
| `placa/reglas.py` | Francisco | Reglas automáticas por umbral |
| `placa/diagram.json` | Francisco | Circuito de Wokwi |
| `placa/red.py` | José | Wi-Fi con timeout y hora NTP |
| `placa/conexion_mqtt.py` | José | Conexión MQTT, publicar y recibir comandos |
| `placa/almacenamiento.py` | José | Guardar lecturas en la placa si se cae la conexión y reenviarlas |
| `placa/main.py` | José | Inicializa todo y corre el bucle de eventos |
| `gateway/config.py` | Compartido | Broker, tópicos, token y ruta de la base de datos |
| `gateway/main.py` | Juan | Escucha MQTT, guarda en SQLite y reenvía comandos a la placa |
| `gateway/base_datos.py` | Juan | Funciones para guardar y consultar |
| `gateway/consultas.py` | Juan | Consultas de históricos desde la terminal |
| `sql/` y `requirements.txt` | Juan | Tablas, consultas y librerías del gateway |
| `gateway/nube.py` | Luis | Conexión con Adafruit IO |
| `gateway/secretos_ejemplo.py` | Luis | Plantilla para las claves de Adafruit IO |
| `docs/` y `README.md` | Luis | Arquitectura, flujo de datos, configuración de la nube y README final |

La carpeta `placa/` tiene exactamente los archivos del proyecto de Wokwi: se copian tal cual.

## 2. Tópicos MQTT

- Broker: `broker.emqx.io`, puerto `1883`, sin usuario ni contraseña.
- Base de todos los tópicos: `utp/fisc/ds8/fran0699/invernadero`. El broker es público; `fran0699` hace que ningún otro grupo use los mismos tópicos.

| Tópico (después de la base) | Publica → escucha | Para qué | Tabla en SQLite |
|---|---|---|---|
| `/lecturas` | Placa → gateway | Lecturas de los sensores y estado de los actuadores, cada 5 s | `lecturas` |
| `/eventos` | Placa → gateway | Lo que hacen las reglas automáticas y las reconexiones | `eventos` |
| `/comandos` | Placa → gateway | Qué hizo la placa con cada orden recibida | `comandos` |
| `/control` | Gateway → placa | Órdenes que llegan desde el dashboard | — |

Regla fácil de recordar: cada tópico que sale de la placa se guarda en la tabla del mismo nombre. `control` lleva la orden; `comandos` lleva lo que la placa hizo con ella.

## 3. Formato de los mensajes

Todos los mensajes son JSON. En todos los que publica la placa:
- `dispositivo` vale `"pico01"`.
- `timestamp` son los segundos desde 1970 en UTC, tomados de la hora NTP. Así cada lectura guardada en la placa durante una caída conserva la hora en que se midió. José confirma en la prueba mínima que `time.time()` cuenta desde 1970; si cuenta desde 2000, se le suma `946684800` antes de publicar.

**`/lecturas`**
```json
{"dispositivo": "pico01", "timestamp": 1762460000, "temperatura": 28.4, "humedad": 62.1, "luz": 45, "ventilador": false, "luz_cultivo": true, "modo": "auto"}
```
- `luz`: porcentaje de 0 a 100.
- `temperatura` y `humedad`: `null` si el DHT22 falló en esa lectura.
- `ventilador` y `luz_cultivo`: estado actual (`true` = encendido).
- `modo`: `"auto"` o `"manual"` (sección 4).

**`/eventos`**
```json
{"dispositivo": "pico01", "timestamp": 1762460005, "tipo": "regla_automatica", "detalle": "Temperatura 31.2 C mayor que 30.0 C: ventilador encendido"}
```
- `tipo`: `"regla_automatica"` o `"reconexion"` (por ejemplo, `"Se reenviaron 4 lecturas guardadas"`).

**`/control`** (el gateway agrega el token antes de publicar)
```json
{"auth_token": "INVERNADERO_DS8_2026", "accion": "ventilador", "valor": true}
```
- `accion` y `valor`: `"ventilador"` con `true` o `false`; `"luz_cultivo"` con `true` o `false`; `"modo"` con `"auto"` o `"manual"`.

**`/comandos`** (nunca incluye el token)
```json
{"dispositivo": "pico01", "timestamp": 1762460010, "accion": "ventilador", "valor": true, "resultado": "ejecutado", "motivo": ""}
```
- `resultado`: `"ejecutado"` o `"rechazado"`.
- `motivo`, si fue rechazado: `"token invalido"`, `"accion desconocida"` o `"mensaje no es JSON"`.

## 4. Modo automático y modo manual

- La placa arranca en modo `auto`: en cada lectura, `reglas.py` decide según los umbrales.
- Una orden de `ventilador` o `luz_cultivo` aplica el valor y pasa la placa a modo `manual`, y las reglas dejan de actuar. Sin esto, la regla deshace lo que pidió el botón en la siguiente lectura.
- La orden `modo` con valor `"auto"` devuelve el control a las reglas.

## 5. Funciones que un módulo llama de otro

**Placa (José llama a las de Francisco)**
- `sensores.leer_sensores()`: devuelve `{"temperatura": float o None, "humedad": float o None, "luz": int}`.
- `actuadores.cambiar_ventilador(encendido)` y `actuadores.cambiar_luz_cultivo(encendido)`: reciben `True` o `False`.
- `actuadores.estado_actuadores()`: devuelve `{"ventilador": bool, "luz_cultivo": bool}`.
- `reglas.aplicar_reglas(lectura)`: recibe lo que devolvió `leer_sensores()` y devuelve una lista de textos, uno por cada actuador que cambió (vacía si nada cambió). José publica cada texto como evento `regla_automatica`.

**Gateway (Juan llama a las de Luis)**
- `nube.conectar(al_recibir_comando)`: conecta con Adafruit IO. Cuando alguien presiona un botón del dashboard, llama a `al_recibir_comando(accion, valor)` con los valores de la sección 3 (`nube.py` traduce lo que manda el botón a ese formato).
- `nube.enviar_lectura(lectura)`: recibe el diccionario de `/lecturas`. Envía a la nube como máximo una vez cada 15 s e ignora las demás, porque el plan gratis de Adafruit IO permite 30 datos por minuto.

## 6. Valores compartidos (`config.py`)

| Valor | Dónde | Contenido |
|---|---|---|
| Wi-Fi | Placa | `Wokwi-GUEST`, sin contraseña |
| Intervalo de lectura | Placa | 5000 ms, con `Timer` |
| Umbral de temperatura | Placa | 30.0 °C: más que eso enciende el ventilador |
| Umbral de luz | Placa | 40 %: menos que eso enciende la luz de cultivo |
| Token | Placa y gateway | `INVERNADERO_DS8_2026` |
| CLIENT_ID de la placa | Placa | `"invernadero_"` + id único de la placa (`machine.unique_id()`) + un número aleatorio |
| CLIENT_ID del gateway | Gateway | Lo genera la librería; no se fija a mano |

- El token va escrito en el código porque Wokwi no tiene variables de entorno.
- El número aleatorio del CLIENT_ID es por si dos de nosotros simulamos a la vez: con el mismo CLIENT_ID, el broker los desconectaría a ambos una y otra vez.
- Las claves de Adafruit IO van solo en `gateway/secretos.py`, que nunca se sube (está en `.gitignore`).

## 7. Cómo probar sin esperar a los demás

- **Francisco:** sensores, actuadores y reglas en Wokwi, mostrando los valores con `print`, sin MQTT.
- **José:** conexión y mensajes con lecturas inventadas, viendo lo que llega al broker con un cliente MQTT (por ejemplo, MQTTX).
- **Juan:** el gateway, publicando a mano mensajes con el formato de la sección 3 desde un cliente MQTT, sin la placa.
- **Luis:** `nube.py`, desde un script que llama a `enviar_lectura` con un diccionario de ejemplo.
