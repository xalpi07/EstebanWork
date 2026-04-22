BEGIN TRANSACTION;

IF NOT EXISTS (
    SELECT 1
    FROM productos
    WHERE id = 1
      AND stock >= 2
)
BEGIN
    ROLLBACK TRANSACTION;
    RETURN;
END;

IF NOT EXISTS (
    SELECT 1
    FROM usuarios
    WHERE id = 1
)
BEGIN
    ROLLBACK TRANSACTION;
    RETURN;
END;

INSERT INTO facturas (
    usuario_id,
    producto_id,
    cantidad,
    precio_unitario,
    total,
    estado
)
VALUES (
    1,
    1,
    2,
    (SELECT precio FROM productos WHERE id = 1),
    (SELECT precio FROM productos WHERE id = 1) * 2,
    N'completada'
);

UPDATE productos
SET stock = stock - 2
WHERE id = 1;

SAVE TRANSACTION factura_creada;

IF 0 = 1
BEGIN
    ROLLBACK TRANSACTION factura_creada;
    ROLLBACK TRANSACTION;
    RETURN;
END;

COMMIT TRANSACTION;
