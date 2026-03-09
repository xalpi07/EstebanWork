--SQLite
SELECT * FROM Customers
WHERE ID NOT IN (SELECT CustomerID FROM Rents);