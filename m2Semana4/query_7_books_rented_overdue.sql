--SQLite
SELECT Books.*
FROM Books
JOIN Rents ON Books.ID = Rents.BookID
WHERE Rents.State = 'Overdue';