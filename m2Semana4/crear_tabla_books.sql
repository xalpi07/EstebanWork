CREATE TABLE Books (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Author INTEGER
);

INSERT INTO Books (ID, Name, Author) VALUES
    (1, 'Don Quijote', 1),
    (2, 'La Divina Comedia', 2),
    (3, 'Vagabond 1-3', 3),
    (4, 'Dragon Ball 1', 4),
    (5, 'The Book of the 5 Rings', NULL);
