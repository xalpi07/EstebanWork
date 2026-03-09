-- SQLite
CREATE TABLE Customers (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Email TEXT NOT NULL
);

INSERT INTO Customers (ID, Name, Email) VALUES
    (1, 'John Doe', 'j.doe@email.com'),
    (2, 'Jane Doe', 'jane@doe.com'),
    (3, 'Luke Skywalker', 'darth.son@email.com');
 