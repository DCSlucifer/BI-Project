-- =============================================================
-- 02_create_dw.sql
-- Creates the data warehouse (star schema): 5 dimensions + 1 fact.
-- Run in SSMS. Drops in FK-safe order so it is re-runnable.
-- =============================================================
IF DB_ID('SuperstoreDW') IS NULL CREATE DATABASE SuperstoreDW;
GO
USE SuperstoreDW;
GO
IF OBJECT_ID('dbo.FactSales')    IS NOT NULL DROP TABLE dbo.FactSales;
IF OBJECT_ID('dbo.DimDate')      IS NOT NULL DROP TABLE dbo.DimDate;
IF OBJECT_ID('dbo.DimProduct')   IS NOT NULL DROP TABLE dbo.DimProduct;
IF OBJECT_ID('dbo.DimCustomer')  IS NOT NULL DROP TABLE dbo.DimCustomer;
IF OBJECT_ID('dbo.DimGeography') IS NOT NULL DROP TABLE dbo.DimGeography;
IF OBJECT_ID('dbo.DimShipMode')  IS NOT NULL DROP TABLE dbo.DimShipMode;
GO

CREATE TABLE dbo.DimDate (
    DateKey     INT PRIMARY KEY,           -- yyyymmdd
    FullDate    DATE NOT NULL,
    [Day]       TINYINT,
    [Month]     TINYINT,
    MonthName   NVARCHAR(20),
    [Quarter]   TINYINT,
    [Year]      SMALLINT,
    WeekdayName NVARCHAR(20)
);

CREATE TABLE dbo.DimProduct (
    ProductKey  INT IDENTITY(1,1) PRIMARY KEY,
    ProductID   NVARCHAR(30) NOT NULL,
    ProductName NVARCHAR(255),
    SubCategory NVARCHAR(50),
    Category    NVARCHAR(50)
);

CREATE TABLE dbo.DimCustomer (
    CustomerKey  INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID   NVARCHAR(20) NOT NULL,
    CustomerName NVARCHAR(100),
    Segment      NVARCHAR(50)
);

CREATE TABLE dbo.DimGeography (
    GeographyKey INT IDENTITY(1,1) PRIMARY KEY,
    Country      NVARCHAR(50),
    Region       NVARCHAR(50),
    [State]      NVARCHAR(100),
    City         NVARCHAR(100),
    PostalCode   NVARCHAR(20)
);

CREATE TABLE dbo.DimShipMode (
    ShipModeKey INT IDENTITY(1,1) PRIMARY KEY,
    ShipMode    NVARCHAR(50) NOT NULL
);

CREATE TABLE dbo.FactSales (
    FactSalesID  INT IDENTITY(1,1) PRIMARY KEY,
    OrderDateKey INT NOT NULL REFERENCES dbo.DimDate(DateKey),
    ShipDateKey  INT NOT NULL REFERENCES dbo.DimDate(DateKey),
    ProductKey   INT NOT NULL REFERENCES dbo.DimProduct(ProductKey),
    CustomerKey  INT NOT NULL REFERENCES dbo.DimCustomer(CustomerKey),
    GeographyKey INT NOT NULL REFERENCES dbo.DimGeography(GeographyKey),
    ShipModeKey  INT NOT NULL REFERENCES dbo.DimShipMode(ShipModeKey),
    OrderID      NVARCHAR(20),              -- degenerate dimension
    Sales        DECIMAL(18,4),
    Quantity     INT,
    Discount     DECIMAL(9,4),
    Profit       DECIMAL(18,4),
    DeliveryDays INT
);
GO
PRINT 'SuperstoreDW star schema created (6 tables).';
