-- SQLite
CREATE TABLE Productos (
    id INT PRIMARY KEY,
    codigo VARCHAR(25),
    nombre VARCHAR(25),
    precio INT CHECK(precio BETWEEN 1000 AND 250000),
    fecha_ingreso DATETIME,
    marca VARCHAR(25)
);