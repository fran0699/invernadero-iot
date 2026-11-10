
-- Base de datos del Invernadero IoT
-- Almacena lecturas, eventos y comandos recibidos por MQTT.

CREATE TABLE IF NOT EXISTS lecturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispositivo TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    temperatura REAL,
    humedad REAL,
    luz INTEGER NOT NULL,
    ventilador INTEGER NOT NULL,
    luz_cultivo INTEGER NOT NULL,
    modo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispositivo TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    detalle TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comandos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispositivo TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    accion TEXT NOT NULL,
    valor TEXT NOT NULL,
    resultado TEXT NOT NULL,
    motivo TEXT NOT NULL
);
