-- SQLite
CREATE TABLE Rents (
    ID INTEGER PRIMARY KEY,
    BookID INTEGER NOT NULL,
    CustomerID INTEGER NOT NULL,
    State TEXT NOT NULL
);

INSERT INTO Rents (ID, BookID, CustomerID, State) VALUES
    (1, 1, 2, 'Returned'),
    (2, 2, 2, 'Returned'),
    (3, 1, 1, 'On time'),
    (4, 3, 1, 'On time'),
    (5, 2, 2, 'Overdue');
