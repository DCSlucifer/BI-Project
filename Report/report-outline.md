# Business Intelligence Final Project — Superstore
### Report skeleton (English). Fill each section, paste screenshots, then export to .docx and .pdf. Target ≤ 100 pages.

---

## Cover page
Title, course, student name & ID, instructor, date. Google Drive link (set to "Anyone with the link").

## Table of Contents
(Auto-generate in Word.)

## 1. Introduction
- 1.1 Project objective and the business questions to answer.
- 1.2 Dataset description: source (Kaggle – Superstore), grain (one product line per order), 9,994 rows, 21 columns, the measures (Sales, Quantity, Discount, Profit) and descriptive attributes.
- 1.3 Solution overview & architecture diagram (CSV → SSIS → DW → SSAS cube → MDX/Power BI/Excel → Python mining).
- 1.4 Tools used (SQL Server 2022, SSIS, SSAS Multidimensional, SSMS, Power BI, Excel, Python).

## 2. SSIS Process — choosing data for the warehouse  *(Requirement 1)*
- 2.1 Source analysis: what each CSV column means; which columns become dimensions vs measures; data-quality issues (encoding, nulls in Postal Code).
- 2.2 Why these columns belong in the warehouse; grain decision; surrogate-key strategy.
- 2.3 ETL design: Staging → DW. Screenshots of the SSIS Control Flow.
- 2.4 Data Flows — Stage load (Flat File → stg_Orders), dimension loads (SELECT DISTINCT), Fact load (Lookups + Derived Column). Screenshots.
- 2.5 ETL validation: reconciliation (staging totals = fact totals) and orphan-key check (`06_verify.sql` output).

## 3. Analysis & Reporting  *(Requirement 2)*

### 3a. Schema & Cube  *(Requirement 2a)*
- Star schema diagram (FactSales + 5 dims). Table definitions.
- Star vs Snowflake: show the snowflake alternative (Category→SubCategory→Product, Country→Region→State→City) with a diagram; compare pros/cons (normalisation vs join cost/performance); justify the chosen star.
- Cube build process: Data Source, Data Source View, dimensions & hierarchies, measures, role-playing date (Order vs Ship), calculated members (Profit Margin, Avg Delivery Days), deploy & process. Screenshots.

### 3b. Manual analysis + 10 reports (SSAS & Power BI)  *(Requirement 2b)*
For EACH of the 10 questions: state the question, show the SSAS browser screenshot, and the Power BI visual, plus a 1–2 sentence insight.
1. Sales & Profit by Year/Quarter (trend)
2. Sales & Profit by Region/State
3. Top 10 products by Sales / Profit
4. Sales & Profit by Category / Sub-Category
5. Profit & Profit Margin by Customer Segment
6. Discount vs Profit (does discounting cause losses?)
7. Sales & order count by Ship Mode
8. Year-over-Year sales growth (%)
9. Top 10 customers by Sales
10. Average delivery time by Region & Ship Mode

### 3c. MDX analysis  *(Requirement 2c)*
- Paste each MDX query from `mdx/queries.mdx` with its result screenshot and a short explanation of the MDX functions used (TOPCOUNT, PARALLELPERIOD, calculated members).

### 3d. Excel PivotTable analysis  *(Requirement 2d)*
- How Excel connects to the SSAS cube (From Analysis Services). Screenshots of 3–4 PivotTables/PivotCharts with slicers and a short interpretation each.

## 4. Data Mining  *(Requirement 3 — 2 algorithms)*
- 4.1 Algorithm 1 — Decision Tree (vs Random Forest) classification of Profitable vs Loss orders: features, train/test split, accuracy, confusion matrix, feature-importance chart, tree visualisation. Business insight (which discount level / sub-categories drive losses).
- 4.2 Algorithm 2 — K-Means RFM customer segmentation: RFM definition, scaling, elbow method, the 4-cluster profile table, segment scatter plot. Name each segment (VIP / Loyal / At-risk / Low-value) and recommend an action per segment.

## 5. Conclusion
- Key findings, what the BI solution enables, limitations, possible future work.

## Appendix
- SQL scripts list, MDX file, Python file reference, full screenshot index.
