-- =============================================================
-- 01_create_landing_table.sql
-- Creates the internal CSV landing table inside the main DW database.
-- This is not a separate staging database.
-- Run in SSMS against your local SQL Server instance.
-- =============================================================
IF DB_ID('SuperstoreDW') IS NULL CREATE DATABASE SuperstoreDW;
GO
USE SuperstoreDW;
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
PRINT 'SuperstoreDW.dbo.stg_Orders created.';
