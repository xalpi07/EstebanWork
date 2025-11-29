-- SQLite
CREATE TABLE ReseñaProductos(
    idReseñaProducto INT PRIMARY KEY,
    idProducto INT,
    Comentario VARCHAR(255),
    Calificación INT,
    Fecha DATETIME,
    idUsuario BIGINT,
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto),
    FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario)
);