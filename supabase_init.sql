-- 1. Asegurarse de que la extensión pgcrypto esté activa (para UUIDs aleatorios)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Eliminar la tabla si ya existiera
DROP TABLE IF EXISTS reports;

-- 3. Crear la tabla "reports"
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_url TEXT,
    category TEXT NOT NULL,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    description TEXT,
    status TEXT DEFAULT 'pendiente',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Crear índice espacial opcional para búsquedas geográficas
CREATE INDEX reports_location_idx ON reports
USING gist (point(longitude, latitude));
