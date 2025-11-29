-- SQLite
CREATE TABLE DetalleFactura(
    idDetalleFactura INT PRIMARY KEY,
    idFactura INT,
    idProducto INT,
    Cantidad INT,
    MontoTotal INT,
    FOREIGN KEY (idFactura) REFERENCES Facturas(idFactura),
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto)
);