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