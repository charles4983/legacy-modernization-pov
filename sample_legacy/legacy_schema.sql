CREATE TABLE CustomerAccounts (
    AccountID INT PRIMARY KEY,
    CustomerName VARCHAR(100),
    BranchCode VARCHAR(20)
);

CREATE TABLE LegacyTransactions (
    TransactionID INT PRIMARY KEY,
    AccountID INT,
    Amount DECIMAL(12,2)
);
