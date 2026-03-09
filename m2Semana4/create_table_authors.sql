-- SQLite
CREATE TABLE Authors (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

INSERT INTO Authors (ID, Name) VALUES
    (1, 'Miguel de Cervantes'),
    (2, 'Dante Alighieri'),
    (3, 'Takehiko Inoue'),
    (4, 'Akira Toriyama'),
    (5, 'Walt Disney');
