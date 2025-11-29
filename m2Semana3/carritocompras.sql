-- SQLite
CREATE TABLE CarritoCompras(
    idCarrito INT PRIMARY KEY,
    idUsuario INT,
    FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario)
);