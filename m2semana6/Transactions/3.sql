BEGIN;

SELECT producto_id, cantidad, estado
FROM facturas
WHERE id = 1
FOR UPDATE;

UPDATE productos
SET stock = stock + (
    SELECT cantidad FROM facturas WHERE id = 1
)
WHERE id = (SELECT producto_id FROM facturas WHERE id = 1);

UPDATE facturas
SET estado = 'retornada'
WHERE id = 1;

COMMIT;
