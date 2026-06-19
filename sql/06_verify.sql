-- =============================================================
-- 06_verify.sql
-- Run AFTER the SSIS package finishes. Confirms the ETL is correct:
--   (1) staging totals == warehouse fact totals
--   (2) no orphan fact rows (all surrogate keys resolve)
-- =============================================================

-- (1) Reconciliation: these two rows must match on rows_/sales_/profit_
SELECT 'staging' AS src, COUNT(*) AS rows_, SUM(Sales) AS sales_, SUM(Profit) AS profit_
FROM SuperstoreStaging.dbo.stg_Orders
UNION ALL
SELECT 'fact', COUNT(*), SUM(Sales), SUM(Profit)
FROM SuperstoreDW.dbo.FactSales;

-- (2) Orphan checks: every count below must be 0
USE SuperstoreDW;
SELECT
  (SELECT COUNT(*) FROM FactSales f LEFT JOIN DimProduct   d ON d.ProductKey  =f.ProductKey   WHERE d.ProductKey   IS NULL) AS orphan_product,
  (SELECT COUNT(*) FROM FactSales f LEFT JOIN DimCustomer  d ON d.CustomerKey =f.CustomerKey  WHERE d.CustomerKey  IS NULL) AS orphan_customer,
  (SELECT COUNT(*) FROM FactSales f LEFT JOIN DimGeography d ON d.GeographyKey=f.GeographyKey WHERE d.GeographyKey IS NULL) AS orphan_geography,
  (SELECT COUNT(*) FROM FactSales f LEFT JOIN DimShipMode  d ON d.ShipModeKey =f.ShipModeKey  WHERE d.ShipModeKey  IS NULL) AS orphan_shipmode,
  (SELECT COUNT(*) FROM FactSales f LEFT JOIN DimDate       d ON d.DateKey     =f.OrderDateKey WHERE d.DateKey      IS NULL) AS orphan_orderdate,
  (SELECT COUNT(*) FROM FactSales f LEFT JOIN DimDate       d ON d.DateKey     =f.ShipDateKey  WHERE d.DateKey      IS NULL) AS orphan_shipdate;
