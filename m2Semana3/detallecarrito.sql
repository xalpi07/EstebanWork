-- SQLite
CREATE TABLE DetalleCarrito(
    idDetalleCarrito INT PRIMARY KEY,
    idCarrito INT,
    idProducto INT,
    Cantidad INT,
    SubTotal INT,
    FOREIGN KEY (idCarrito) REFERENCES CarritoCompras(idCarrito),
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto)
);