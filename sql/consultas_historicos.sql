-- Consultas de historicos del Invernadero IoT.
-- Son las mismas que ejecuta gateway/consultas.py (py -m gateway.consultas).
-- datetime(timestamp, 'unixepoch', 'localtime') convierte los segundos
-- desde 1970 que envia la placa en una fecha legible, en la hora de la PC.

-- Ultimas 10 lecturas de sensores
SELECT
    id,
    dispositivo,
    datetime(timestamp, 'unixepoch', 'localtime') AS fecha,
    temperatura,
    humedad,
    luz,
    ventilador,
    luz_cultivo,
    modo
FROM lecturas
ORDER BY id DESC
LIMIT 10;

-- Ultimos 10 eventos (reglas automaticas y reconexiones)
SELECT
    id,
    dispositivo,
    datetime(timestamp, 'unixepoch', 'localtime') AS fecha,
    tipo,
    detalle
FROM eventos
ORDER BY id DESC
LIMIT 10;

-- Ultimos 10 comandos recibidos (ejecutados o rechazados)
SELECT
    id,
    dispositivo,
    datetime(timestamp, 'unixepoch', 'localtime') AS fecha,
    accion,
    valor,
    resultado,
    motivo
FROM comandos
ORDER BY id DESC
LIMIT 10;
