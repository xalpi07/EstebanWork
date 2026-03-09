-- SQLite
CREATE TABLE Facturas(
    idFactura INT PRIMARY KEY,
    NumeroFactura INT,
    FechaCompra DATETIME,
    MontoTotal INT,
    idUsuario INT,
    idMetodoPago INT,
    FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario),
    FOREIGN KEY (idMetodoPago) REFERENCES MetodosPago(idMetodoPago)
);