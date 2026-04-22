BEGIN TRANSACTION;

IF OBJECT_ID(N'facturas', N'U') IS NOT NULL
    DROP TABLE facturas;

IF OBJECT_ID(N'productos', N'U') IS NOT NULL
    DROP TABLE productos;

IF OBJECT_ID(N'usuarios', N'U') IS NOT NULL
    DROP TABLE usuarios;

CREATE TABLE usuarios (
    id        INT            IDENTITY(1, 1) NOT NULL,
    nombre    NVARCHAR(200)  NOT NULL,
    email     NVARCHAR(255)  NOT NULL,
    CONSTRAINT pk_usuarios      PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_email UNIQUE (email)
);

CREATE TABLE productos (
    id        INT            IDENTITY(1, 1) NOT NULL,
    nombre    NVARCHAR(200)  NOT NULL,
    precio    NUMERIC(12, 2)  NOT NULL
        CONSTRAINT ck_productos_precio CHECK (precio >= 0),
    stock     INT            NOT NULL
        CONSTRAINT df_productos_stock DEFAULT (0),
    CONSTRAINT pk_productos         PRIMARY KEY (id),
    CONSTRAINT ck_productos_stock_nneg CHECK (stock >= 0)
);

CREATE TABLE facturas (
    id              INT            IDENTITY(1, 1) NOT NULL,
    usuario_id      INT            NOT NULL,
    producto_id     INT            NOT NULL,
    cantidad        INT            NOT NULL,
    precio_unitario NUMERIC(12, 2) NOT NULL,
    total           NUMERIC(12, 2) NOT NULL,
    estado          VARCHAR(20)    NOT NULL
        CONSTRAINT df_facturas_estado DEFAULT (N'completada'),
    creado_en       DATETIME2(3)   NOT NULL
        CONSTRAINT df_facturas_creado_en DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT pk_facturas PRIMARY KEY (id),
    CONSTRAINT fk_factura_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id) ON DELETE NO ACTION,
    CONSTRAINT fk_factura_producto FOREIGN KEY (producto_id)
        REFERENCES productos (id) ON DELETE NO ACTION,
    CONSTRAINT ck_facturas_cantidad         CHECK (cantidad > 0),
    CONSTRAINT ck_facturas_precio_unitario  CHECK (precio_unitario >= 0),
    CONSTRAINT ck_facturas_total            CHECK (total >= 0),
    CONSTRAINT ck_facturas_estado           CHECK (estado IN (N'completada', N'retornada'))
);

CREATE NONCLUSTERED INDEX idx_facturas_usuario
    ON facturas (usuario_id);

CREATE NONCLUSTERED INDEX idx_facturas_producto
    ON facturas (producto_id);

CREATE NONCLUSTERED INDEX idx_facturas_estado
    ON facturas (estado);

COMMIT;
