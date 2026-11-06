# Invernadero IoT

Sistema IoT que monitorea y controla las condiciones de cultivo de un invernadero simulado en Wokwi. Parcial 2 de Desarrollo de Software VIII.

La Pico W lee la temperatura, la humedad y la luz, y enciende el ventilador o la luz de cultivo según umbrales. Envía todo por MQTT a un gateway en Python, que lo guarda en SQLite y lo muestra en un dashboard de Adafruit IO. Desde el dashboard se pueden encender y apagar los actuadores.

## Integrantes y aportes

| Integrante | Usuario GitHub | Aporte |
|---|---|---|
| Francisco Lata | fran0699 | Placa: sensores, actuadores y circuito |
| José Luna | Josamatsu19 | Placa: conexión y eventos |
| Juan Vasquez | java0594 | Gateway y base de datos |
| Luis Barnett | Iambarnett | Nube y documentación |

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `placa/` | Código MicroPython y circuito del proyecto de Wokwi |
| `gateway/` | Programa en Python que corre en la PC |
| `sql/` | Scripts de la base de datos |
| `docs/` | Contrato entre módulos, arquitectura, flujo de datos y configuración de la nube |

## Cómo ejecutarlo

Se completa cuando cada módulo esté listo.

## Cómo trabajamos

- Antes de programar, lee [docs/contrato.md](docs/contrato.md): tópicos, mensajes, funciones y dueño de cada archivo.
- Lo que vale es lo que está en `main`. Wokwi es solo para probar: cada uno usa su copia del proyecto.
- Una rama por tarea, por ejemplo `feature/sensores-dht22`, y un PR con dos apartados: "Qué cambia" y "Cómo se verificó".
- Cada PR lo aprueba otro integrante antes de fusionarlo: José revisa a Francisco, Juan a José, Luis a Juan y Francisco a Luis.
- El código se escribe para explicarlo proyectado:
  - Cada archivo empieza con un comentario corto: qué hace y con qué módulo se conecta.
  - Funciones cortas, que quepan en la pantalla, con un docstring que diga qué reciben y qué devuelven.
  - Nombres en español y descriptivos.
  - Pines, umbrales y tópicos solo en `config.py`.
  - Comentarios que explican el porqué, no el qué.
  - Nada "ingenioso": sin lambdas ni comprensiones anidadas.
