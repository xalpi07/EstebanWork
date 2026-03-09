--SQLite
SELECT Books.ID, Books.Name, Authors.Name AS Author
FROM Books
LEFT JOIN Authors ON Books.Author = Authors.ID;