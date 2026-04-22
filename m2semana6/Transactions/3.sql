BEGIN TRANSACTION;

IF NOT EXISTS (
    SELECT 1
    FROM facturas
    WHERE id = 1
)
BEGIN
    ROLLBACK TRANSACTION;
    RETURN;
END;

IF EXISTS (
    SELECT 1
    FROM facturas
    WHERE id = 1
      AND LOWER(LTRIM(RTRIM(estado))) = N'retornada'
)
BEGIN
    ROLLBACK TRANSACTION;
    RETURN;
END;

UPDATE productos
SET
    stock = stock + (
        SELECT cantidad
        FROM facturas
        WHERE id = 1
    )
WHERE id = (
    SELECT producto_id
    FROM facturas
    WHERE id = 1
);

UPDATE facturas
SET estado = N'retornada'
WHERE id = 1;

COMMIT TRANSACTION;
