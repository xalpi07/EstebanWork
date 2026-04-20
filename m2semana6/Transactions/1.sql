BEGIN;

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    precio NUMERIC(12, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_productos_precio CHECK (precio >= 0),
    CONSTRAINT ck_productos_stock CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS facturas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
    producto_id INTEGER NOT NULL REFERENCES productos (id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'completada',
    creado_en TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_facturas_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_facturas_precio_unitario CHECK (precio_unitario >= 0),
    CONSTRAINT ck_facturas_total CHECK (total >= 0),
    CONSTRAINT ck_facturas_estado CHECK (estado IN ('completada', 'retornada'))
);

CREATE INDEX IF NOT EXISTS idx_facturas_usuario ON facturas (usuario_id);
CREATE INDEX IF NOT EXISTS idx_facturas_producto ON facturas (producto_id);
CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas (estado);

COMMIT;
