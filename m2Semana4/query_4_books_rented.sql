--SQLite
SELECT DISTINCT Books.*
FROM Books
JOIN Rents ON Books.ID = Rents.BookID;