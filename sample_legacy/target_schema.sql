CREATE TABLE Accounts (
    AccountID BIGINT PRIMARY KEY,
    CustomerFullName VARCHAR(150),
    BranchID INT
);

CREATE TABLE Transactions (
    TransactionID BIGINT PRIMARY KEY,
    AccountID BIGINT,
    Amount DECIMAL(18,2)
);
