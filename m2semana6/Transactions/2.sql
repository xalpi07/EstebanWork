SELECT stock, precio
FROM productos
WHERE id = 1
FOR UPDATE;

SELECT 1
FROM usuarios
WHERE id = 1;

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
    'completada'
);

UPDATE productos
SET stock = stock - 2
WHERE id = 1;