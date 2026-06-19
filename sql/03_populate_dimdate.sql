-- =============================================================
-- 03_populate_dimdate.sql
-- Populates DimDate for 2014-01-01 .. 2018-12-31 (covers all
-- Superstore order & ship dates). Run BEFORE the SSIS fact load.
-- =============================================================
USE SuperstoreDW;
GO
DELETE FROM dbo.DimDate;   -- TRUNCATE is blocked because FactSales has FK references to DimDate.
GO
DECLARE @start DATE = '2014-01-01';
DECLARE @end   DATE = '2018-12-31';
;WITH d AS (
    SELECT @start AS dt
    UNION ALL
    SELECT DATEADD(DAY, 1, dt) FROM d WHERE dt < @end
)
INSERT INTO dbo.DimDate (DateKey, FullDate, [Day], [Month], MonthName, [Quarter], [Year], WeekdayName)
SELECT
    YEAR(dt) * 10000 + MONTH(dt) * 100 + DAY(dt),
    dt,
    DAY(dt),
    MONTH(dt),
    DATENAME(MONTH, dt),
    DATEPART(QUARTER, dt),
    YEAR(dt),
    DATENAME(WEEKDAY, dt)
FROM d
OPTION (MAXRECURSION 0);
GO
DECLARE @DimDateRows INT = (SELECT COUNT(*) FROM dbo.DimDate);
PRINT CONCAT('DimDate populated with ', @DimDateRows, ' rows (expected 1826).');
