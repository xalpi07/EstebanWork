-- SQLite
CREATE TABLE Usuarios(
    idUsuario INT PRIMARY KEY,
    NombreCompleto VARCHAR(255),
    Correousuario VARCHAR(255) UNIQUE,
    FechaRegistro DATETIME
);