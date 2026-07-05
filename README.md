# Superstore Business Intelligence Final Project

## Overview

This project implements an end-to-end Business Intelligence solution for the Superstore retail dataset using the Microsoft BI stack and Python data mining. The submitted database is `SuperstoreDW`.

The current pipeline does **not** use a separate staging database. The source CSV is loaded into `SuperstoreDW.dbo.stg_Orders`, an internal landing table inside the main warehouse database. The dimensional warehouse is then populated from this landing table into five dimensions and the central fact table `FactSales`.

`FactSales` is not a temporary table. It is the central fact table of the star schema and stores the additive business measures used by SSAS, MDX, Power BI, and Excel.

## Architecture

```text
Sample - Superstore.csv
    -> SSIS ETL
    -> SuperstoreDW.dbo.stg_Orders        internal landing table
    -> SuperstoreDW star schema           FactSales + five dimensions
    -> SSAS Multidimensional cube
    -> MDX, Power BI, Excel PivotTables
    -> Python data mining
```

The analytical star schema contains:

| Table | Role |
| --- | --- |
| `FactSales` | Central fact table at order-line grain. Stores Sales, Quantity, Discount, Profit, DeliveryDays, and foreign keys to all dimensions. |
| `DimDate` | Calendar dimension used as a role-playing dimension for order date and ship date. |
| `DimProduct` | Product hierarchy: Product, Sub-Category, Category. |
| `DimCustomer` | Customer identity and Segment. |
| `DimGeography` | Country, Region, State, City, and PostalCode. |
| `DimShipMode` | Shipping mode descriptions. |
| `stg_Orders` | Internal CSV landing table inside `SuperstoreDW`; used only by ETL and verification, not by SSAS or Power BI reports. |

## Repository Structure

```text
.
|-- DataMining/     Python script, model outputs, and algorithm explanation
|-- dataset/        Original Superstore CSV source file
|-- Excel/          Excel workbook with OLAP PivotTables
|-- mdx/            MDX analytical query file
|-- PowerBI/        Power BI Desktop report
|-- Report/         Report materials, diagrams, screenshots, and slides
|-- sql/            SQL scripts for landing table, star schema, date dimension, and verification
|-- SSAS/           SSAS Multidimensional project
`-- SSIS/           SSIS ETL project
```

## Tools

| Layer | Tool |
| --- | --- |
| Database engine | SQL Server 2022 Developer Edition |
| ETL | SQL Server Integration Services (SSIS) |
| OLAP | SQL Server Analysis Services Multidimensional |
| Query | SQL and MDX |
| Dashboard | Power BI Desktop |
| Pivot analysis | Microsoft Excel |
| Data mining | Python, pandas, scikit-learn, matplotlib |
| IDE | Visual Studio 2022, SQL Server Management Studio |

## Environment Requirements

1. SQL Server 2022 Developer Edition with Database Engine.
2. SQL Server Analysis Services installed in Multidimensional and Data Mining mode.
3. SQL Server Management Studio.
4. Visual Studio 2022 with:
   - SQL Server Integration Services Projects 2022.
   - Microsoft Analysis Services Projects.
5. Power BI Desktop.
6. Microsoft Excel.
7. Python 3 or Anaconda with:
   - pandas
   - numpy
   - matplotlib
   - scikit-learn

## SQL Setup

Run the SQL scripts in this order from SQL Server Management Studio:

```text
sql/01_create_landing_table.sql
sql/02_create_dw.sql
sql/03_populate_dimdate.sql
```

These scripts create:

| Object | Purpose |
| --- | --- |
| `SuperstoreDW.dbo.stg_Orders` | Internal landing table for CSV rows inside the main warehouse database. |
| `DimDate`, `DimProduct`, `DimCustomer`, `DimGeography`, `DimShipMode` | Descriptive dimensions for analytical slicing and filtering. |
| `FactSales` | Central fact table for Sales, Quantity, Discount, Profit, and DeliveryDays measures. |

## SSIS ETL

Open the SSIS project:

```text
SSIS/Integration Services Project1
```

Use the main package:

```text
SSIS/Integration Services Project1/ETL_Main.dtsx
```

Expected connection managers:

| Connection | Purpose |
| --- | --- |
| `OLEDB_DW` | Project-level connection to `SuperstoreDW`; used for both `dbo.stg_Orders` and the dimensional star schema. |
| `FF_Superstore` | Flat File connection to `dataset/Sample - Superstore.csv`, using Windows-1252 compatible encoding. |

The main SSIS package performs:

1. Clear the internal landing table.
2. Load the CSV into `SuperstoreDW.dbo.stg_Orders`.
3. Reset/load dimensional warehouse tables.
4. Load `DimProduct`, `DimCustomer`, `DimGeography`, and `DimShipMode`.
5. Load `FactSales` by resolving surrogate keys from all dimensions.

`ETL_DirectCSV.dtsx`, if present in the SSIS folder, is a demo-only package and is not part of the submitted main pipeline.

## ETL Verification

After running `ETL_Main.dtsx`, execute:

```text
sql/06_verify.sql
```

Expected validation:

| Check | Expected result |
| --- | --- |
| `SuperstoreDW.dbo.stg_Orders` row count | 9,994 rows |
| `SuperstoreDW.dbo.FactSales` row count | 9,994 rows |
| Sales total comparison | Landing table and fact table totals match |
| Profit total comparison | Landing table and fact table totals match |
| Orphan foreign-key checks | All counts are 0 |

The reconciliation source is the internal landing table `SuperstoreDW.dbo.stg_Orders`, not a separate staging database.

## SSAS Cube

Open the SSAS project:

```text
SSAS/SuperstoreSSAS
```

The SSAS data source must point to `SuperstoreDW`. The Data Source View includes only the curated analytical star schema: `FactSales` and the five dimension tables. It should not expose `dbo.stg_Orders` to cube users.

The cube includes:

| Component | Content |
| --- | --- |
| Measure group | `Fact Sales` |
| Base measures | Sales, Quantity, Discount, Profit, DeliveryDays, Fact Sales Count |
| Calculated members | Profit Margin, Avg Delivery Days |
| Dimensions | Date, Product, Customer, Geography, Ship Mode |

Deploy and process the cube before running MDX, Excel PivotTables, or cube browser screenshots.

## MDX Analysis

MDX queries are stored in:

```text
mdx/queries.mdx
```

The file contains representative analytical queries for:

| Area | Example analysis |
| --- | --- |
| Time | Sales and Profit by Year and Quarter; Year-over-Year Sales Growth |
| Product | Top products, Category, Sub-Category |
| Customer | Segment-level Profit and Profit Margin; Top customers |
| Geography | Regional and state-level Sales and Profit |
| Shipping | Average Delivery Days by Region and Ship Mode |
| Profitability | Discount impact on Profit |

## Power BI and Excel

Power BI file:

```text
PowerBI/Superstore.pbix
```

Excel workbook:

```text
Excel/Superstore.xlsx
```

Power BI connects to `SuperstoreDW` and imports only the analytical tables required for reporting. Excel connects to the SSAS cube and uses cube measures and dimensions in PivotTables.

## Data Mining

Main script:

```text
DataMining/data_mining.py
```

Run:

```powershell
cd DataMining
python data_mining.py
```

The script implements two complementary methods:

| Method | Purpose |
| --- | --- |
| Decision Tree Classification | Predict whether each order line is profitable or loss-making and extract interpretable loss-risk rules. |
| K-Means RFM Segmentation | Segment customers by Recency, Frequency, and Monetary value. |

Key final outputs:

| Output | Value |
| --- | --- |
| Decision Tree test accuracy | 0.9440 |
| Decision Tree macro F1-score | 0.9033 |
| Cross-validation accuracy | 0.9444 +/- 0.0020 |
| Strongest loss rule | `Discount > 0.25 AND Category != Technology -> Loss` |
| Strongest rule precision | 99.37% on 318 held-out test records |
| K-Means cluster count | 4 |
| K-Means silhouette score | 0.3554 |

Stable customer segment labels:

| Cluster | Segment |
| --- | --- |
| 0 | `Trung thanh / Active` |
| 1 | `Pho thong / Trung binh` |
| 2 | `VIP / Champions` |
| 3 | `Roi bo / Lost` |

Outputs are generated in:

```text
DataMining/outputs
```

## Final Review Checklist

Before submission, verify:

| Layer | Check |
| --- | --- |
| SQL Server | Only `SuperstoreDW` is required for the submitted pipeline. |
| Landing table | `SuperstoreDW.dbo.stg_Orders` exists and has 9,994 rows after SSIS runs. |
| Fact table | `SuperstoreDW.dbo.FactSales` exists and has 9,994 rows. |
| Verification | `sql/06_verify.sql` returns matching row counts, matching Sales/Profit totals, and zero orphan keys. |
| SSIS | `ETL_Main.dtsx` runs successfully with green ticks. |
| SSAS | Cube deploys, processes, and browses successfully. |
| MDX | Queries in `mdx/queries.mdx` return data. |
| Power BI | Report connects to `SuperstoreDW` and uses the star schema. |
| Excel | PivotTables connect to the SSAS cube. |
| Data Mining | Python script regenerates outputs under `DataMining/outputs`. |

## Important Submission Notes

- Do not delete `FactSales`; it is the central fact table of the star schema.
- Do not submit `SuperstoreStaging` or `CSVImportDemo` as part of the main pipeline.
- Do not describe `dbo.stg_Orders` as a separate staging database. It is an internal landing table inside `SuperstoreDW`.
- The submitted main flow is: CSV -> internal landing table in `SuperstoreDW` -> dimensions and `FactSales` -> SSAS cube -> MDX, Power BI, Excel, and Python data mining.
