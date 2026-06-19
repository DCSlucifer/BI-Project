-- =============================================================
-- 01_create_staging.sql
-- Creates the staging database and raw landing table for the CSV.
-- Run in SSMS against your local SQL Server instance.
-- =============================================================
IF DB_ID('SuperstoreStaging') IS NULL CREATE DATABASE SuperstoreStaging;
GO
USE SuperstoreStaging;
GO
IF OBJECT_ID('dbo.stg_Orders') IS NOT NULL DROP TABLE dbo.stg_Orders;
GO
CREATE TABLE dbo.stg_Orders (
    RowID        INT,
    OrderID      NVARCHAR(20),
    OrderDate    DATE,
    ShipDate     DATE,
    ShipMode     NVARCHAR(50),
    CustomerID   NVARCHAR(20),
    CustomerName NVARCHAR(100),
    Segment      NVARCHAR(50),
    Country      NVARCHAR(50),
    City         NVARCHAR(100),
    [State]      NVARCHAR(100),
    PostalCode   NVARCHAR(20),   -- string keeps leading zeros
    Region       NVARCHAR(50),
    ProductID    NVARCHAR(30),
    Category     NVARCHAR(50),
    SubCategory  NVARCHAR(50),
    ProductName  NVARCHAR(255),
    Sales        DECIMAL(18,4),
    Quantity     INT,
    Discount     DECIMAL(9,4),
    Profit       DECIMAL(18,4)
);
GO
PRINT 'SuperstoreStaging.dbo.stg_Orders created.';
