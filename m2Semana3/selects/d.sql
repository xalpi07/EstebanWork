-- SQLite
SELECT idProducto, SUM(Cantidad) AS TotalComprado
FROM DetalleFactura
GROUP BY idProducto;