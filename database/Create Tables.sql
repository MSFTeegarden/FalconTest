-- Create Sessions table
CREATE TABLE Sessions
(
    sessionID INT PRIMARY KEY,
    isActive INT,
    activeDate DATETIME,
    inactiveDate DATETIME
)

-- Create Items table
CREATE TABLE Items
(
    itemId INT PRIMARY KEY,
    price MONEY
)

-- Create Carts table
CREATE TABLE Carts
(
    sessionID INT,
	itemID INT,
	price MONEY,
	currentDate DATETIME,
	PRIMARY KEY (sessionID, itemID)
)
-- Populate Items Table

DECLARE @id INT
DECLARE @myprice MONEY
SET @myprice = 0.01
SET @id = 1
WHILE (@id <= 10000)
BEGIN
	INSERT INTO Items (itemId, price) VALUES (@id, @myprice)
	SELECT @id = @id + 1
	SELECT @myprice = @myprice + 0.01
END
