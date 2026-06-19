# BI Final Project (Superstore) — Implementation Plan

> **For agentic workers:** This is a **GUI-heavy Microsoft BI project** executed on the user's Windows machine. Most tasks are performed manually by the user in Visual Studio (SSIS/SSAS designers), Power BI Desktop, and Excel — a subagent cannot click these. File-producible artifacts (SQL scripts, Python data-mining code, report skeleton) CAN be generated directly. Each task uses checkbox (`- [ ]`) tracking and ends with a **Verify** step (run a query / check a row count / view a result) — that is the "test" for this domain.

**Goal:** Build a complete end-to-end BI solution on the Superstore dataset (ETL → data warehouse → OLAP cube → MDX/Power BI/Excel reporting → Python data mining) that satisfies 100% of the final-project requirements at top marks.

**Architecture:** CSV → SSIS loads a Staging DB → SSIS transforms into a star-schema Data Warehouse → SSAS Multidimensional cube → analysis via manual browse, MDX, Power BI, and Excel PivotTable → Python for 2 data-mining algorithms.

**Tech Stack:** SQL Server 2022 (Database Engine + Analysis Services Multidimensional), SSIS, SSMS, Visual Studio 2022, Power BI Desktop, Excel, Python (pandas, scikit-learn).

**Spec:** [2026-05-31-bi-final-project-superstore-design.md](../specs/2026-05-31-bi-final-project-superstore-design.md)

**Folder layout (under `d:\BI project\`):**
```
dataset\Sample - Superstore.csv
sql\        01_create_staging.sql … 06_verify.sql
SSIS\       SuperstoreETL\ (VS solution)
SSAS\       SuperstoreSSAS\ (VS solution)
mdx\        queries.mdx
PowerBI\    Superstore.pbix
Excel\      Superstore.xlsx
DataMining\ data_mining.ipynb + outputs\
Report\     report.docx / report.pdf
```

---

## PHASE 0 — Environment Setup

### Task 0.1: Install software (manual, user)

- [ ] **Step 1: SQL Server 2022 Developer Edition.** Download (Developer edition) → run **Custom** install → Feature Selection: tick **Database Engine Services** + **Analysis Services**.
- [ ] **Step 2 (CRITICAL): Analysis Services mode.** On the *Analysis Services Configuration* page choose **`Multidimensional and Data Mining Mode`** (NOT Tabular). Click "Add Current User".
- [ ] **Step 3: SSMS.** Install SQL Server Management Studio.
- [ ] **Step 4: VS2022 extensions.** VS2022 → Extensions → Manage Extensions → Online → install `SQL Server Integration Services Projects 2022` and `Microsoft Analysis Services Projects`. Restart VS to finish VSIX install.
- [ ] **Step 5: Anaconda.** Install Anaconda (Python).
- [ ] **Step 6: Verify Excel** present.
- [ ] **Verify:** Open SSMS → connect to `localhost` (Database Engine) — success. In SSMS *Connect → Analysis Services* → server `localhost` → in Object Explorer the server should report **Multidimensional** mode (right-click server → Properties → shows mode). If it says Tabular, reinstall the SSAS instance.

### Task 0.2: Download dataset (manual, user)

- [ ] **Step 1:** Download `Sample - Superstore.csv` from Kaggle (`vivek468/superstore-dataset-final`).
- [ ] **Step 2:** Save to `d:\BI project\dataset\Sample - Superstore.csv`.
- [ ] **Verify:** Open in Notepad — first line is the header `Row ID,Order ID,Order Date,...,Profit`; ~9,995 lines total (1 header + 9,994 rows).

---

## PHASE 1 — Databases & Star Schema (SQL via SSMS)

> All scripts are run in SSMS. I (Claude) generate these `.sql` files for you; you run them.

### Task 1.1: Create Staging database & table

**Files:** Create `sql\01_create_staging.sql`

- [ ] **Step 1: Create the script** with this content:

```sql
-- 01_create_staging.sql
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
```

- [ ] **Step 2: Run it** in SSMS (F5).
- [ ] **Verify:** `SELECT name FROM sys.databases WHERE name='SuperstoreStaging';` returns 1 row; `SELECT COUNT(*) FROM SuperstoreStaging.dbo.stg_Orders;` returns 0.

### Task 1.2: Create Data Warehouse & star-schema tables

**Files:** Create `sql\02_create_dw.sql`

- [ ] **Step 1: Create the script** with this content:

```sql
-- 02_create_dw.sql
IF DB_ID('SuperstoreDW') IS NULL CREATE DATABASE SuperstoreDW;
GO
USE SuperstoreDW;
GO
IF OBJECT_ID('dbo.FactSales')   IS NOT NULL DROP TABLE dbo.FactSales;
IF OBJECT_ID('dbo.DimDate')     IS NOT NULL DROP TABLE dbo.DimDate;
IF OBJECT_ID('dbo.DimProduct')  IS NOT NULL DROP TABLE dbo.DimProduct;
IF OBJECT_ID('dbo.DimCustomer') IS NOT NULL DROP TABLE dbo.DimCustomer;
IF OBJECT_ID('dbo.DimGeography')IS NOT NULL DROP TABLE dbo.DimGeography;
IF OBJECT_ID('dbo.DimShipMode') IS NOT NULL DROP TABLE dbo.DimShipMode;
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
```

- [ ] **Step 2: Run it** (F5).
- [ ] **Verify:** `SELECT name FROM SuperstoreDW.sys.tables ORDER BY name;` returns exactly 6 tables (DimCustomer, DimDate, DimGeography, DimProduct, DimShipMode, FactSales).

### Task 1.3: Populate DimDate

**Files:** Create `sql\03_populate_dimdate.sql`

- [ ] **Step 1: Create the script** with this content:

```sql
-- 03_populate_dimdate.sql
USE SuperstoreDW;
GO
TRUNCATE TABLE dbo.DimDate;  -- safe: no FK rows yet on first run
GO
DECLARE @start DATE = '2014-01-01';
DECLARE @end   DATE = '2018-12-31';
;WITH d AS (
    SELECT @start AS dt
    UNION ALL
    SELECT DATEADD(DAY,1,dt) FROM d WHERE dt < @end
)
INSERT INTO dbo.DimDate (DateKey, FullDate, [Day],[Month],MonthName,[Quarter],[Year],WeekdayName)
SELECT
    YEAR(dt)*10000 + MONTH(dt)*100 + DAY(dt),
    dt, DAY(dt), MONTH(dt), DATENAME(MONTH,dt),
    DATEPART(QUARTER,dt), YEAR(dt), DATENAME(WEEKDAY,dt)
FROM d
OPTION (MAXRECURSION 0);
```

- [ ] **Step 2: Run it** (F5).
- [ ] **Verify:** `SELECT COUNT(*) FROM SuperstoreDW.dbo.DimDate;` returns **1826** (5 years incl. 2016 leap day). `SELECT * FROM DimDate WHERE DateKey=20161108;` returns the row for 2016-11-08.

---

## PHASE 2 — SSIS ETL (Visual Studio, manual + guided)

> Goal of this phase per the rubric: demonstrate a real ETL process. We use Data Flow tasks (Flat File source, Lookups, Derived Column) so the report has strong screenshots.

### Task 2.1: Create the SSIS project & connection managers

- [ ] **Step 1:** VS2022 → Create New Project → search **"Integration Services Project"** → name `SuperstoreETL`, location `d:\BI project\SSIS\` → Create.
- [ ] **Step 2:** In Solution Explorer rename `Package.dtsx` → `ETL_Main.dtsx`.
- [ ] **Step 3:** Right-click **Connection Managers** (bottom pane) → New OLE DB Connection → New → Server `localhost`, choose **SuperstoreStaging** → OK. Rename it `OLEDB_Staging`.
- [ ] **Step 4:** Repeat for **SuperstoreDW** → rename `OLEDB_DW`.
- [ ] **Step 5:** Right-click Connection Managers → New Flat File Connection → Browse to `d:\BI project\dataset\Sample - Superstore.csv`; Format = Delimited; **Code page = `1252 (ANSI - Latin I)`**; tick "Column names in the first data row"; set Locale = **English (United States)**. Rename `FF_Superstore`.
- [ ] **Step 6:** In the Flat File CM → **Advanced** page → set data types: `Order Date` and `Ship Date` → `date [DT_DBDATE]`; `Sales`,`Discount`,`Profit` → `decimal [DT_DECIMAL]`; `Quantity`,`Row ID` → `four-byte signed integer [DT_I4]`; `Postal Code` → `Unicode string [DT_WSTR]` width 20; the rest → `Unicode string [DT_WSTR]` with width ≥ the table column.
- [ ] **Verify:** Flat File CM → "Preview" shows the grid with dates parsed (e.g., 11/8/2016) and no red errors.

> ⚠️ **Fallback** if dates won't parse: set `Order Date`/`Ship Date` to `string [DT_WSTR]` in the Flat File CM, change `stg_Orders.OrderDate/ShipDate` to `NVARCHAR(50)`, and in Task 2.5 use `TRY_CONVERT(date, OrderDate, 101)`.

### Task 2.2: Control Flow — truncate tasks

- [ ] **Step 1:** Drag an **Execute SQL Task** onto the Control Flow → rename "SQL Truncate Staging" → Connection `OLEDB_Staging` → SQLStatement: `TRUNCATE TABLE dbo.stg_Orders;`
- [ ] **Step 2:** Drag another **Execute SQL Task** → "SQL Reset DW" → Connection `OLEDB_DW` → SQLStatement:

```sql
DELETE FROM dbo.FactSales;
DELETE FROM dbo.DimProduct;
DELETE FROM dbo.DimCustomer;
DELETE FROM dbo.DimGeography;
DELETE FROM dbo.DimShipMode;
DBCC CHECKIDENT('dbo.DimProduct', RESEED, 0);
DBCC CHECKIDENT('dbo.DimCustomer', RESEED, 0);
DBCC CHECKIDENT('dbo.DimGeography', RESEED, 0);
DBCC CHECKIDENT('dbo.DimShipMode', RESEED, 0);
DBCC CHECKIDENT('dbo.FactSales', RESEED, 0);
```

- [ ] **Verify:** Both tasks present; we will wire precedence (green arrows) as we add the data flows.

### Task 2.3: Data Flow — Stage Load (CSV → stg_Orders)

- [ ] **Step 1:** Drag a **Data Flow Task** → rename "DFT Stage Load". Connect green arrow: SQL Truncate Staging → DFT Stage Load.
- [ ] **Step 2:** Double-click into it → add **Flat File Source** using `FF_Superstore`.
- [ ] **Step 3:** Add **OLE DB Destination** using `OLEDB_Staging`, table `dbo.stg_Orders`. Connect source → destination. On **Mappings**, map CSV columns to table columns (names match except spaces, e.g., `Order ID`→`OrderID`, `Sub-Category`→`SubCategory`, `Postal Code`→`PostalCode`). Map by hand where auto-map misses.
- [ ] **Verify:** Right-click the package → Execute Task on "DFT Stage Load" (or run package). Then in SSMS: `SELECT COUNT(*) FROM SuperstoreStaging.dbo.stg_Orders;` returns **9994**. `SELECT TOP 5 OrderDate, Sales, Profit FROM stg_Orders;` shows real dates and numbers.

### Task 2.4: Data Flows — Load the 4 surrogate-key dimensions

> One Data Flow per dimension. Each: OLE DB Source (a `SELECT DISTINCT` query) → OLE DB Destination. Connect "SQL Reset DW" → these 4 flows.

- [ ] **Step 1: DFT Load DimProduct.** Source `OLEDB_Staging`, *SQL command*:
  `SELECT DISTINCT ProductID, ProductName, SubCategory, Category FROM dbo.stg_Orders;`
  Destination `OLEDB_DW` table `dbo.DimProduct` (map ProductID/ProductName/SubCategory/Category; leave ProductKey unmapped — it is IDENTITY).
- [ ] **Step 2: DFT Load DimCustomer.** Source query:
  `SELECT DISTINCT CustomerID, CustomerName, Segment FROM dbo.stg_Orders;`
  Destination `dbo.DimCustomer`.
- [ ] **Step 3: DFT Load DimGeography.** Source query:
  `SELECT DISTINCT Country, Region, [State], City, ISNULL(PostalCode,'N/A') AS PostalCode FROM dbo.stg_Orders;`
  Destination `dbo.DimGeography`.
- [ ] **Step 4: DFT Load DimShipMode.** Source query:
  `SELECT DISTINCT ShipMode FROM dbo.stg_Orders;`
  Destination `dbo.DimShipMode`.
- [ ] **Verify (after running these 4):**
  `SELECT COUNT(*) FROM SuperstoreDW.dbo.DimProduct;` ≈ **1862**;
  `DimCustomer` ≈ **793**; `DimShipMode` = **4**; `DimGeography` ≈ **630+** (distinct geography combos). Exact dim counts may vary slightly — they just must be > 0 and far less than 9994.

### Task 2.5: Data Flow — Load FactSales (Lookups + Derived Column)

- [ ] **Step 1:** Drag **Data Flow Task** "DFT Load FactSales". Connect all 4 dim flows → this flow (so it runs last; use precedence arrows).
- [ ] **Step 2: OLE DB Source** `OLEDB_Staging`, *SQL command*:
  `SELECT OrderID, OrderDate, ShipDate, ShipMode, CustomerID, Country, Region, [State], City, ISNULL(PostalCode,'N/A') AS PostalCode, ProductID, Sales, Quantity, Discount, Profit FROM dbo.stg_Orders;`
- [ ] **Step 3: Lookup "LKP Product"** — connection `OLEDB_DW`, *Use results of SQL query*: `SELECT ProductKey, ProductID FROM dbo.DimProduct;` → on Columns tab join `ProductID`=`ProductID`, output `ProductKey`. Set "Redirect rows to no match output" OFF (Fail component — all should match).
- [ ] **Step 4: Lookup "LKP Customer"** — `SELECT CustomerKey, CustomerID FROM dbo.DimCustomer;` join on `CustomerID`, output `CustomerKey`.
- [ ] **Step 5: Lookup "LKP ShipMode"** — `SELECT ShipModeKey, ShipMode FROM dbo.DimShipMode;` join on `ShipMode`, output `ShipModeKey`.
- [ ] **Step 6: Lookup "LKP Geography"** — `SELECT GeographyKey, Country, Region, [State], City, PostalCode FROM dbo.DimGeography;` join on all 5 columns (Country, Region, State, City, PostalCode), output `GeographyKey`.
- [ ] **Step 7: Derived Column "DRV Keys"** — add 3 columns:
  - `OrderDateKey` = `YEAR(OrderDate) * 10000 + MONTH(OrderDate) * 100 + DAY(OrderDate)`
  - `ShipDateKey`  = `YEAR(ShipDate) * 10000 + MONTH(ShipDate) * 100 + DAY(ShipDate)`
  - `DeliveryDays` = `DATEDIFF("Dd", OrderDate, ShipDate)`
- [ ] **Step 8: OLE DB Destination** `OLEDB_DW` table `dbo.FactSales`. Map: OrderDateKey, ShipDateKey, ProductKey, CustomerKey, GeographyKey, ShipModeKey, OrderID, Sales, Quantity, Discount, Profit, DeliveryDays. Leave FactSalesID unmapped (IDENTITY).
- [ ] **Step 9: Run the whole package** (right-click `ETL_Main.dtsx` → Execute Package). All tasks turn green.
- [ ] **Verify:** `SELECT COUNT(*) FROM SuperstoreDW.dbo.FactSales;` returns **9994**. Run the reconciliation query in Task 2.6.

### Task 2.6: ETL reconciliation check

**Files:** Create `sql\06_verify.sql`

- [ ] **Step 1: Create the script** with this content:

```sql
-- 06_verify.sql  (totals must match between staging and the warehouse)
SELECT 'staging' AS src, COUNT(*) rows_, SUM(Sales) sales_, SUM(Profit) profit_
FROM SuperstoreStaging.dbo.stg_Orders
UNION ALL
SELECT 'fact', COUNT(*), SUM(Sales), SUM(Profit)
FROM SuperstoreDW.dbo.FactSales;
-- orphan check: any fact row whose keys don't resolve? expect 0
SELECT COUNT(*) AS orphan_fact
FROM SuperstoreDW.dbo.FactSales f
LEFT JOIN SuperstoreDW.dbo.DimProduct p ON p.ProductKey=f.ProductKey
WHERE p.ProductKey IS NULL;
```

- [ ] **Step 2: Run it.**
- [ ] **Verify:** Both rows show identical `rows_` (9994), `sales_`, and `profit_`; `orphan_fact` = 0. ✅ ETL is correct.

---

## PHASE 3 — SSAS Multidimensional Cube (Visual Studio, manual + guided)

### Task 3.1: Create SSAS project + Data Source + DSV

- [ ] **Step 1:** VS2022 → New Project → **"Analysis Services Multidimensional and Data Mining Project"** → name `SuperstoreSSAS`, location `d:\BI project\SSAS\`.
- [ ] **Step 2:** Right-click project → Properties → Deployment → Server = your SSAS instance (`localhost` if default; or `localhost\InstanceName`). Database = `SuperstoreSSAS`.
- [ ] **Step 3:** Right-click **Data Sources** → New → New connection → Provider **Native OLE DB\SQL Server Native Client / Microsoft OLE DB Driver** → Server `localhost`, DB `SuperstoreDW`. Impersonation: **Use the service account** (dev-friendly).
- [ ] **Step 4:** Right-click **Data Source Views** → New → pick the data source → add **FactSales** and all 5 Dim tables → Finish. The designer auto-draws FK relationships (incl. both FactSales→DimDate via OrderDateKey & ShipDateKey).
- [ ] **Verify:** DSV diagram shows FactSales in the center joined to all 5 dimensions; DimDate has two lines from FactSales (Order + Ship).

### Task 3.2: Build the 5 dimensions with hierarchies

- [ ] **Step 1: DimDate.** Right-click Dimensions → New → from existing table DimDate, key = DateKey. Add attributes: Year, Quarter, Month (use `MonthName` as name, `Month` as key/order), FullDate. Create hierarchy **Calendar**: Year → Quarter → MonthName → FullDate. Set attribute relationships so each level rolls up.
- [ ] **Step 2: DimProduct.** Key ProductKey; attributes Category, SubCategory, ProductName. Hierarchy **Products**: Category → SubCategory → ProductName.
- [ ] **Step 3: DimGeography.** Key GeographyKey; attributes Country, Region, State, City. Hierarchy **Geography**: Country → Region → State → City.
- [ ] **Step 4: DimCustomer.** Key CustomerKey; attributes Segment, CustomerName. Hierarchy **Customers**: Segment → CustomerName.
- [ ] **Step 5: DimShipMode.** Key ShipModeKey; attribute ShipMode (flat).
- [ ] **Verify:** Each dimension → Browser tab → expand the hierarchy and confirm members appear (e.g., Products shows Furniture/Office Supplies/Technology → sub-categories → products).

### Task 3.3: Build the cube, measures & role-playing date

- [ ] **Step 1:** Right-click Cubes → New Cube → use existing tables → measure group table **FactSales** → measures: Sales, Quantity, Profit, Discount, DeliveryDays, plus the auto "FactSales Count". Add all 5 dimensions.
- [ ] **Step 2: Role-playing date.** On the **Dimension Usage** tab, add DimDate twice — once linked via **OrderDateKey** (rename cube dimension "Order Date") and once via **ShipDateKey** (rename "Ship Date").
- [ ] **Step 3: Measure aggregations.** Sales/Quantity/Profit/Discount → `Sum`. DeliveryDays → `Sum` (we average it via a calc). Format Sales/Profit/Discount as Currency.
- [ ] **Step 4: Calculated members.** On the **Calculations** tab add:
  - `[Measures].[Profit Margin]` = `IIF([Measures].[Sales]=0, NULL, [Measures].[Profit]/[Measures].[Sales])`, format `Percent`.
  - `[Measures].[Avg Delivery Days]` = `IIF([Measures].[FactSales Count]=0, NULL, [Measures].[DeliveryDays]/[Measures].[FactSales Count])`.
- [ ] **Step 5: Deploy.** Build → Deploy `SuperstoreSSAS`. Wait for "Deployment Completed Successfully" and processing to finish.
- [ ] **Verify:** In SSMS → Connect to Analysis Services → expand `SuperstoreSSAS` → Cubes → SuperstoreCube → Browse. Drag Sales onto values, Order Date.Calendar (Year) onto rows → totals appear by year (2014–2017). Grand total Sales ≈ **2,297,200** (matches FactSales SUM).

---

## PHASE 4 — Manual Analysis + MDX (the 10 questions)

### Task 4.1: Manual browse (screenshots for report section 3b)

- [ ] **Step 1:** In the cube Browser (SSMS or VS), build a pivot for each of the 10 questions (drag dimensions to rows, measures to values) and screenshot each. (Questions listed in spec §7.)
- [ ] **Verify:** You have 10 labelled screenshots saved under `Report\screenshots\ssas\`.

### Task 4.2: Write the 10 MDX queries

**Files:** Create `mdx\queries.mdx`

- [ ] **Step 1: Create the file** with these queries (run each in SSMS → MDX query window against `SuperstoreSSAS`):

```mdx
-- Q1: Sales & Profit by Year and Quarter
SELECT { [Measures].[Sales], [Measures].[Profit] } ON COLUMNS,
NON EMPTY [Order Date].[Calendar].[Year].MEMBERS * [Order Date].[Calendar].[Quarter].MEMBERS ON ROWS
FROM [SuperstoreCube];

-- Q2: Sales & Profit by Region and State
SELECT { [Measures].[Sales], [Measures].[Profit] } ON COLUMNS,
NON EMPTY [Geography].[Geography].[State] ON ROWS
FROM [SuperstoreCube];

-- Q3: Top 10 Products by Sales
SELECT [Measures].[Sales] ON COLUMNS,
TOPCOUNT([Product].[Products].[ProductName].MEMBERS, 10, [Measures].[Sales]) ON ROWS
FROM [SuperstoreCube];

-- Q4: Sales & Profit by Category and Sub-Category
SELECT { [Measures].[Sales], [Measures].[Profit] } ON COLUMNS,
NON EMPTY [Product].[Products].[SubCategory].MEMBERS ON ROWS
FROM [SuperstoreCube];

-- Q5: Profit & Profit Margin by Customer Segment
SELECT { [Measures].[Profit], [Measures].[Profit Margin] } ON COLUMNS,
[Customer].[Customers].[Segment].MEMBERS ON ROWS
FROM [SuperstoreCube];

-- Q6: Sales & Profit by Discount band (discount as a dimension proxy via Sub-Category drill is limited;
-- here we show Profit vs Discount total per Category)
SELECT { [Measures].[Discount], [Measures].[Profit] } ON COLUMNS,
[Product].[Products].[Category].MEMBERS ON ROWS
FROM [SuperstoreCube];

-- Q7: Sales & order count by Ship Mode
SELECT { [Measures].[Sales], [Measures].[FactSales Count] } ON COLUMNS,
[Ship Mode].[ShipMode].MEMBERS ON ROWS
FROM [SuperstoreCube];

-- Q8: Year-over-Year Sales (current vs previous year)
WITH MEMBER [Measures].[Sales PY] AS
  ([Measures].[Sales], PARALLELPERIOD([Order Date].[Calendar].[Year],1,[Order Date].[Calendar].CurrentMember))
MEMBER [Measures].[YoY %] AS
  IIF([Measures].[Sales PY]=0, NULL, ([Measures].[Sales]-[Measures].[Sales PY])/[Measures].[Sales PY]), FORMAT_STRING='Percent'
SELECT { [Measures].[Sales], [Measures].[Sales PY], [Measures].[YoY %] } ON COLUMNS,
[Order Date].[Calendar].[Year].MEMBERS ON ROWS
FROM [SuperstoreCube];

-- Q9: Top 10 Customers by Sales
SELECT [Measures].[Sales] ON COLUMNS,
TOPCOUNT([Customer].[Customers].[CustomerName].MEMBERS, 10, [Measures].[Sales]) ON ROWS
FROM [SuperstoreCube];

-- Q10: Avg Delivery Days by Region and Ship Mode
SELECT [Ship Mode].[ShipMode].MEMBERS ON COLUMNS,
[Geography].[Geography].[Region].MEMBERS ON ROWS
WHERE [Measures].[Avg Delivery Days]
FROM [SuperstoreCube];
```

- [ ] **Verify:** Each query returns a non-empty grid in SSMS. (Member path names like `[Product].[Products].[ProductName]` must match the exact dimension/hierarchy/level names you created in Task 3.2 — adjust if you named them differently.)

---

## PHASE 5 — Power BI dashboards (10 questions)

### Task 5.1: Connect & model

- [ ] **Step 1:** Power BI Desktop → Get Data → SQL Server → Server `localhost`, Database `SuperstoreDW`, **Import** → select all 6 tables → Load.
- [ ] **Step 2:** Model view → confirm relationships auto-created from FKs. Add the second DimDate relationship (ShipDateKey) as **inactive** (Order Date is the active one).
- [ ] **Verify:** Model view shows the star with FactSales linked to all dims.

### Task 5.2: DAX measures

- [ ] **Step 1:** Create measures (New Measure):

```DAX
Total Sales = SUM ( FactSales[Sales] )
Total Profit = SUM ( FactSales[Profit] )
Total Quantity = SUM ( FactSales[Quantity] )
Profit Margin = DIVIDE ( [Total Profit], [Total Sales] )
Avg Delivery Days = AVERAGE ( FactSales[DeliveryDays] )
Sales PY = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( DimDate[FullDate] ) )
YoY % = DIVIDE ( [Total Sales] - [Sales PY], [Sales PY] )
```

- [ ] **Verify:** Dropping `Total Sales` into a card shows ≈ 2.3M.

### Task 5.3: Build report pages for the 10 questions

- [ ] **Step 1:** Build visuals (one per question, grouped on ~3 pages): line chart Sales/Profit by Year-Quarter (Q1); map/bar by State (Q2); bar Top-10 products (Q3); matrix Category→SubCategory (Q4); bar by Segment + Margin (Q5); scatter Discount vs Profit (Q6); donut by Ship Mode (Q7); line YoY% (Q8); bar Top-10 customers (Q9); matrix Avg Delivery Days by Region×ShipMode (Q10). Add slicers (Year, Region, Category, Segment).
- [ ] **Step 2:** Save as `d:\BI project\PowerBI\Superstore.pbix`.
- [ ] **Verify:** Each of the 10 questions has a corresponding visual; slicers filter all visuals.

---

## PHASE 6 — Excel PivotTable (connected to the cube)

### Task 6.1: Connect Excel to SSAS cube

- [ ] **Step 1:** Excel → Data → Get Data → From Database → **From Analysis Services** → Server = SSAS instance → select database `SuperstoreSSAS` → cube `SuperstoreCube` → PivotTable Report.
- [ ] **Step 2:** Build 3–4 pivots answering representative questions, e.g.: Sales by Category (rows) × Region (columns); Profit by Segment × Year; Top products via value filter. Add a **PivotChart** and **Slicers** (Year, Region).
- [ ] **Step 3:** Save as `d:\BI project\Excel\Superstore.xlsx`.
- [ ] **Verify:** Pivot grand-total Sales matches the cube (~2.3M); slicers update the pivot live.

---

## PHASE 7 — Data Mining in Python (2 algorithms)

> I (Claude) generate the full notebook/script for you; you run it in Jupyter (Anaconda) and paste charts/metrics into the report.

### Task 7.1: Create the data-mining notebook

**Files:** Create `DataMining\data_mining.py` (and/or `.ipynb`)

- [ ] **Step 1: Create the script** with this content:

```python
# data_mining.py — Superstore: (1) Decision Tree classification, (2) K-Means RFM clustering
import pandas as pd, numpy as np, matplotlib.pyplot as plt, os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

OUT = "outputs"; os.makedirs(OUT, exist_ok=True)
df = pd.read_csv(r"../dataset/Sample - Superstore.csv", encoding="latin-1")
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"]  = pd.to_datetime(df["Ship Date"])

# ---------- Algorithm 1: classify order line as Profitable (Profit>0) ----------
df["Profitable"] = (df["Profit"] > 0).astype(int)
feat_num = ["Sales", "Quantity", "Discount"]
feat_cat = ["Category", "Sub-Category", "Region", "Segment", "Ship Mode"]
X = pd.get_dummies(df[feat_num + feat_cat], columns=feat_cat)
y = df["Profitable"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

dt = DecisionTreeClassifier(max_depth=4, random_state=42).fit(Xtr, ytr)
print("Decision Tree accuracy:", round(accuracy_score(yte, dt.predict(Xte)), 4))
print(classification_report(yte, dt.predict(Xte)))
print("Confusion matrix:\n", confusion_matrix(yte, dt.predict(Xte)))

rf = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)
print("Random Forest accuracy:", round(accuracy_score(yte, rf.predict(Xte)), 4))

imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
imp.iloc[::-1].plot.barh(); plt.title("Top 10 feature importances (RF)"); plt.tight_layout()
plt.savefig(f"{OUT}/feature_importance.png"); plt.close()

plt.figure(figsize=(20,8)); plot_tree(dt, feature_names=X.columns, class_names=["Loss","Profit"],
    filled=True, fontsize=7, max_depth=3); plt.savefig(f"{OUT}/decision_tree.png"); plt.close()

# ---------- Algorithm 2: K-Means RFM customer segmentation ----------
snapshot = df["Order Date"].max() + pd.Timedelta(days=1)
rfm = df.groupby("Customer ID").agg(
    Recency=("Order Date", lambda s: (snapshot - s.max()).days),
    Frequency=("Order ID", "nunique"),
    Monetary=("Sales", "sum")).reset_index()

Xr = StandardScaler().fit_transform(rfm[["Recency","Frequency","Monetary"]])
inertia = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xr).inertia_ for k in range(1,9)]
plt.plot(range(1,9), inertia, "o-"); plt.xlabel("k"); plt.ylabel("inertia")
plt.title("Elbow method"); plt.savefig(f"{OUT}/elbow.png"); plt.close()

km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(Xr)
rfm["Cluster"] = km.labels_
profile = rfm.groupby("Cluster")[["Recency","Frequency","Monetary"]].mean().round(1)
profile["Count"] = rfm["Cluster"].value_counts().sort_index()
print("\nRFM cluster profile:\n", profile)
profile.to_csv(f"{OUT}/rfm_profile.csv")

plt.scatter(rfm["Frequency"], rfm["Monetary"], c=rfm["Cluster"], cmap="viridis", s=15)
plt.xlabel("Frequency"); plt.ylabel("Monetary"); plt.title("Customer segments (K-Means)")
plt.savefig(f"{OUT}/segments.png"); plt.close()
print("\nDone. Charts saved to ./outputs/")
```

- [ ] **Step 2: Run it** from `d:\BI project\DataMining\`: `python data_mining.py` (or run cells in Jupyter).
- [ ] **Verify:** Console prints Decision Tree accuracy (~0.85+), Random Forest accuracy, the confusion matrix, and the 4-cluster RFM profile; `outputs\` contains `feature_importance.png`, `decision_tree.png`, `elbow.png`, `segments.png`, `rfm_profile.csv`.

### Task 7.2: Interpret results (for report section 4)

- [ ] **Step 1:** Write 1 paragraph per algorithm: classification → which features drive loss (expect high Discount + certain Sub-Categories) and the discount threshold from the tree; clustering → name the 4 segments (VIP / Loyal / At-risk / Low-value) from the RFM profile and give an action per segment.
- [ ] **Verify:** Each algorithm has a results table/chart + a business-insight paragraph.

---

## PHASE 8 — Report (English) + Videos

### Task 8.1: Write the report

**Files:** Create `Report\report.docx` (draft skeleton can be generated as `Report\report-outline.md` first)

- [ ] **Step 1:** Follow the spec §12 outline. Section mapping to rubric: §2 SSIS process; §3a schema+cube; §3b 10 questions (SSAS + Power BI screenshots); §3c MDX; §3d Excel; §4 data mining. Insert the screenshots collected in Phases 4–7.
- [ ] **Step 2:** Keep ≤100 pages. Export to PDF (`report.pdf`).
- [ ] **Verify:** Every rubric item from the assignment maps to a labelled section; both `report.docx` and `report.pdf` exist.

### Task 8.2: Record videos (bonus)

- [ ] **Step 1:** Screen-record short demos: SSIS run, cube browse, Power BI, Excel pivot, Python run. Save to `Report\..\Videos\` (or a `Videos\` folder).
- [ ] **Verify:** Each phase has a clip.

---

## PHASE 9 — Package & Submit (Google Drive)

### Task 9.1: Assemble & share

- [ ] **Step 1:** Create the Drive folder structure (spec §11): `1. Report`, `2. Dataset`, `3. SSIS project`, `4. SSAS`, `5. Data mining`, `6. Videos`.
- [ ] **Step 2:** Copy artifacts in: report.docx/pdf; CSV; SSIS solution; SSAS solution + Superstore.pbix + Superstore.xlsx; data_mining.ipynb/.py + outputs; videos.
- [ ] **Step 3:** Share → "Anyone with the link → Viewer".
- [ ] **Verify:** Open the share link in a private/incognito browser (logged out) — all folders are visible and downloadable. Submit the link.

---

## Self-Review notes (coverage of spec)

- Spec §1 (install) → Phase 0. §2 (dataset) → Task 0.2. §3 (architecture) → Phases 1–2. §4 (star schema) → Tasks 1.2–1.3, 2.x. §5 (SSIS detail) → Phase 2. §6 (cube) → Phase 3. §7 (10 questions) → Tasks 4.1, 5.3, MDX 4.2. §8 (MDX) → Task 4.2. §9 (Power BI/Excel) → Phases 5–6. §10 (data mining) → Phase 7. §11 (deliverables) → Phase 9. §12 (report) → Phase 8. §13 (roadmap) → phase order. §14 (risks) → SSAS mode (Task 0.1 Step 2), encoding (Task 2.1 Step 5 + Python read), null postal code (Task 2.4/2.5 ISNULL), role-playing date (Task 3.3), Drive share (Task 9.1). ✅ All sections covered.
