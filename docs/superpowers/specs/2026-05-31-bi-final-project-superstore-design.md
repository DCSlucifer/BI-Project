# BI Final Project — Design Spec (Superstore)

> **Tài liệu gốc (master design)** cho đồ án cuối kỳ Business Intelligence.
> Ngày tạo: 2026-05-31 · Dataset: **Superstore** · Report: **Tiếng Anh** · Trình độ: **Beginner** (hướng dẫn từng bước).
> Stack: **Microsoft BI** (SQL Server 2022 + SSIS + SSAS Multidimensional + Power BI + Excel) + **Python** (data mining).

---

## 0. Mục tiêu & Tiêu chí "10 điểm"

Xây dựng trọn vẹn một giải pháp BI end-to-end trên dataset Superstore, đáp ứng 100% yêu cầu đề bài:

1. **SSIS process** — quy trình ETL chọn & nạp dữ liệu vào kho (warehouse).
2. **Analysis & reporting**
   - (a) Mô tả schema (star/snowflake) + quy trình dựng cube.
   - (b) Phân tích thủ công (SSAS browser) + báo cáo **10 câu hỏi** (SSAS & Power BI).
   - (c) Phân tích bằng **MDX**.
   - (d) Phân tích bằng **Pivot Table trong Excel**.
3. **Data mining** — **2 thuật toán** (Python).

Tiêu chí chấm cao: ETL có staging thật sự, schema được giải thích cả star lẫn snowflake, 10 câu hỏi trả lời song song trên SSAS + Power BI, MDX chạy được, Excel nối trực tiếp cube (OLAP), data mining có insight kinh doanh, report ≤100 trang chỉn chu + video bonus.

---

## 1. Môi trường & Phần mềm cần cài

**Đã có:** Windows 11 · Visual Studio 2022 · Power BI Desktop.

**Cần cài (theo thứ tự):**

| # | Phần mềm | Mục đích | Ghi chú sống còn |
|---|----------|----------|------------------|
| 1 | **SQL Server 2022 Developer Edition** (free) | Database Engine (kho DW) + chạy SSIS + **Analysis Services** | ⚠️ Trang *Analysis Services Configuration* phải chọn **`Multidimensional and Data Mining Mode`** — KHÔNG chọn Tabular. Sai → MDX/cube không làm được, phải gỡ cài lại instance. Tick feature: Database Engine Services + Analysis Services. Add Current User làm admin. |
| 2 | **SSMS** (SQL Server Management Studio, free) | Quản lý DB, viết SQL, chạy **MDX** trên cube | Tải riêng. |
| 3 | **VS2022 Extensions** (Extensions → Manage Extensions → Online) | Tạo project SSIS & SSAS | Cài 2 cái: `SQL Server Integration Services Projects 2022` + `Microsoft Analysis Services Projects`. VS sẽ đóng để cài VSIX. |
| 4 | **Anaconda (Python)** (free) | Data mining 2 thuật toán | Kèm sẵn Jupyter, pandas, scikit-learn, matplotlib, seaborn. |
| 5 | **Microsoft Excel** | Pivot Table nối cube (deliverable) | Cần xác nhận có Office. |
| 6 | Power BI Desktop | Dashboard 10 câu hỏi | ✅ Đã có. |

**Link tải:** SQL Server Developer (microsoft.com/sql-server/sql-server-downloads) · SSMS (learn.microsoft.com → Download SSMS) · Anaconda (anaconda.com/download).

---

## 2. Dataset

- **Nguồn:** Kaggle — *Superstore Dataset (Final)* của `vivek468` → file `Sample - Superstore.csv` (9.994 dòng, 21 cột).
- **Lưu tại:** `d:\BI project\dataset\Sample - Superstore.csv`
- **Encoding:** thường `latin-1 / Windows-1252` → cần xử lý khi nạp bằng SSIS và đọc bằng Python (`encoding='latin-1'`).
- **Cột:** Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name, Segment, Country, City, State, Postal Code, Region, Product ID, Category, Sub-Category, Product Name, **Sales, Quantity, Discount, Profit**.

---

## 3. Kiến trúc & Luồng dữ liệu (Phương án A — Staging → DW)

```
Sample - Superstore.csv
   │  SSIS: Extract
   ▼
[SuperstoreStaging]  →  stg_Orders (dữ liệu thô, đúng kiểu CSV)
   │  SSIS: Transform (làm sạch, khử trùng lặp, sinh khóa, tính DateKey & DeliveryDays)
   ▼
[SuperstoreDW]  →  DimDate, DimProduct, DimCustomer, DimGeography, DimShipMode, FactSales
   │
   ├─►  [SSAS Multidimensional]  SuperstoreCube  ─►  Browse thủ công + MDX (SSMS)
   │                                              └►  Excel PivotTable (kết nối OLAP)
   ├─►  [Power BI]  nối SuperstoreDW (Import) → dashboard 10 câu hỏi
   └─►  [Python]    đọc dữ liệu đã làm sạch → 2 thuật toán data mining
```

**Lý do chọn Phương án A:** thể hiện đầy đủ "quy trình chọn dữ liệu cho warehouse" (yêu cầu mục 1), tách bạch các bước nên người mới dễ theo, và ăn điểm phần SSIS.

---

## 4. Star Schema — `SuperstoreDW`

**Grain của FactSales:** 1 dòng sản phẩm trong 1 đơn hàng (= 1 dòng CSV).

### 4.1 Bảng Fact

**FactSales**
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| OrderDateKey | INT (FK→DimDate) | từ Order Date |
| ShipDateKey | INT (FK→DimDate) | role-playing cùng DimDate |
| ProductKey | INT (FK→DimProduct) | |
| CustomerKey | INT (FK→DimCustomer) | |
| GeographyKey | INT (FK→DimGeography) | |
| ShipModeKey | INT (FK→DimShipMode) | |
| OrderID | NVARCHAR | degenerate dimension |
| Sales | MONEY | measure |
| Quantity | INT | measure |
| Discount | FLOAT | measure |
| Profit | MONEY | measure |
| DeliveryDays | INT | = ShipDate − OrderDate (derived) |

### 4.2 Bảng Dimension

| Dimension | Cột |
|-----------|-----|
| **DimDate** | DateKey (yyyymmdd), FullDate, Day, Month, MonthName, Quarter, Year, Weekday |
| **DimProduct** | ProductKey (surrogate), ProductID, ProductName, SubCategory, Category |
| **DimCustomer** | CustomerKey (surrogate), CustomerID, CustomerName, Segment |
| **DimGeography** | GeographyKey (surrogate), Country, Region, State, City, PostalCode |
| **DimShipMode** | ShipModeKey (surrogate), ShipMode |

### 4.3 Star vs Snowflake (cho mục 2a)
- **Triển khai: STAR** (các Dim phẳng) — đơn giản, hiệu năng tốt, dễ dựng cube.
- **Trong report mô tả thêm SNOWFLAKE:** tách `Category → SubCategory → Product` và `Country → Region → State → City` thành các bảng chuẩn hóa riêng; vẽ sơ đồ + so sánh ưu/nhược (chuẩn hóa giảm trùng lặp vs nhiều JOIN/hiệu năng). → Trình bày được cả hai mà không làm cube phức tạp.

---

## 5. SSIS ETL — chi tiết

**DB cần tạo trước (bằng SSMS):** `SuperstoreStaging`, `SuperstoreDW`.

**Control Flow / Data Flow (gợi ý):**
1. **Stage:** Flat File Source (`Sample - Superstore.csv`, code page latin-1) → chỉnh kiểu dữ liệu → OLE DB Destination `stg_Orders`.
2. **Load DimDate:** sinh bảng ngày (script SQL từ min(Order Date) → max(Ship Date)) hoặc Script/Execute SQL Task.
3. **Load các Dim** (Product, Customer, Geography, ShipMode): từ `stg_Orders` dùng `SELECT DISTINCT` → mỗi Dim nhận surrogate key (IDENTITY). Kỹ thuật: Execute SQL hoặc Data Flow + Lookup để tránh trùng.
4. **Load FactSales:** đọc `stg_Orders` → **Lookup** từng Dim để lấy surrogate key (Date theo DateKey, Product theo ProductID, Customer theo CustomerID, Geography theo Country+Region+State+City+PostalCode, ShipMode theo ShipMode) → Derived Column tính `DeliveryDays` → OLE DB Destination `FactSales`.
5. **Xử lý chất lượng dữ liệu:** trim khoảng trắng, ép kiểu Sales/Profit/Discount, kiểm tra null Postal Code (vài dòng thiếu) → để mặc định/ghi log.

Report ghi rõ: vì sao chọn các cột này cho warehouse, quyết định grain, cách sinh surrogate key, cách xử lý role-playing date.

---

## 6. Cube `SuperstoreCube` (SSAS Multidimensional)

1. **Data Source** → `SuperstoreDW`.
2. **Data Source View (DSV)** → kéo FactSales + 5 Dim, nối quan hệ khóa (tạo 2 quan hệ tới DimDate cho Order/Ship — role-playing).
3. **Dimensions + Hierarchies:**
   - Date: `Year → Quarter → Month → Date`
   - Product: `Category → Sub-Category → Product`
   - Geography: `Country → Region → State → City`
   - Customer: `Segment → Customer`
   - Ship Mode: phẳng.
4. **Measures:** `Sum(Sales)`, `Sum(Quantity)`, `Sum(Profit)`, `Sum(Discount)`.
5. **Calculated Members:** `Profit Margin = [Profit]/[Sales]`, `Avg Delivery Days = Avg(DeliveryDays)`.
6. **Deploy → Process** (Full). Kiểm tra trong tab Browser.

---

## 7. 10 Câu hỏi phân tích (trả lời trên cả SSAS + Power BI)

1. Tổng **Sales & Profit theo Year/Quarter** (xu hướng thời gian).
2. **Sales & Profit theo Region và State** (hiệu quả theo địa lý).
3. **Top 10 sản phẩm** theo Sales và theo Profit.
4. **Sales & Profit theo Category và Sub-Category.**
5. **Profit & Profit Margin theo Customer Segment.**
6. **Ảnh hưởng của mức Discount đến Profit** (giảm giá có gây lỗ?).
7. **Sales & số đơn theo Ship Mode.**
8. **Tăng trưởng Sales theo năm (YoY %).**
9. **Top 10 khách hàng theo Sales.**
10. **Thời gian giao hàng trung bình (Ship − Order)** theo Region & Ship Mode.

Mỗi câu: ảnh SSAS browser + truy vấn MDX + biểu đồ Power BI.

---

## 8. MDX (mục 2c)

~8–10 truy vấn ánh xạ các câu hỏi trên, chạy trong SSMS (kết nối tới Analysis Services → cube). Ví dụ:

```mdx
-- Top 10 sản phẩm theo Sales
SELECT [Measures].[Sales] ON COLUMNS,
TOPCOUNT([Product].[Product].[Product].MEMBERS, 10, [Measures].[Sales]) ON ROWS
FROM [SuperstoreCube];
```
```mdx
-- Sales & Profit theo Năm
SELECT { [Measures].[Sales], [Measures].[Profit] } ON COLUMNS,
[Date].[Year].MEMBERS ON ROWS
FROM [SuperstoreCube];
```

---

## 9. Power BI & Excel

- **Power BI (mục 2b):** Get Data → SQL Server → `SuperstoreDW` (Import) → dựng lại quan hệ star → tạo measure DAX (YoY %, Profit Margin) → dashboard nhiều trang trả lời 10 câu hỏi (slicer theo Year/Region/Category/Segment).
- **Excel (mục 2d):** Data → Get Data → From Database → **From Analysis Services** → `SuperstoreCube` → PivotTable + PivotChart + Slicer trả lời các câu hỏi tiêu biểu (vd: Sales theo Category × Region, Profit theo Segment × Year).

---

## 10. Data Mining — Python, 2 thuật toán (mục 3)

**Thuật toán 1 — Phân lớp (Decision Tree, so sánh Random Forest):**
- Mục tiêu: dự đoán đơn hàng **Lãi/Lỗ** (`label = Profit > 0`).
- Features: Discount, Category, Sub-Category, Quantity, Sales, Region, Segment, Ship Mode (one-hot encode biến phân loại).
- Output: train/test split, accuracy, confusion matrix, classification report, **feature importance**, vẽ cây quyết định.
- Insight: ngưỡng Discount gây lỗ, nhóm sản phẩm rủi ro.

**Thuật toán 2 — Phân cụm (K-Means, RFM):**
- Tính **Recency / Frequency / Monetary** cho mỗi Customer → chuẩn hóa (StandardScaler) → **Elbow method** chọn k → K-Means.
- Output: profile từng cụm, đặt tên (VIP / Trung thành / Nguy cơ rời bỏ / Giá trị thấp), scatter/biểu đồ.

**Giao nộp:** `data_mining.ipynb` + `.py` xuất ra + thư mục ảnh biểu đồ. Đọc CSV với `encoding='latin-1'`.

---

## 11. Deliverables — Cấu trúc Google Drive

Share quyền **"Anyone with the link → Viewer"**.

```
BI_Final_Project/
├── 1. Report/              report.docx + report.pdf  (≤100 trang)
├── 2. Dataset/             Sample - Superstore.csv (+ bản đã làm sạch)
├── 3. SSIS project/        toàn bộ solution SSIS (.dtsx, .sln)
├── 4. SSAS/                SSAS project + Superstore.pbix + Superstore.xlsx
├── 5. Data mining/         data_mining.ipynb + .py + ảnh outputs
└── 6. Videos/  (bonus)     clip demo từng phần
```

---

## 12. Bố cục Report (Tiếng Anh, ≤100 trang) — bám đúng đề

1. **Introduction** — mục tiêu, mô tả dataset, các business question.
2. **SSIS Process** — phân tích nguồn, lý do chọn cột cho warehouse, thiết kế ETL, screenshot Control/Data Flow, staging → DW.
3. **Analysis & Reporting**
   - 3a. **Schema** (star vs snowflake — sơ đồ + giải thích) + **quy trình dựng cube** (DSV, dimensions, hierarchies, measures, deploy/process).
   - 3b. **Manual analysis (SSAS browser) + 10 câu hỏi** (ảnh SSAS + dashboard Power BI).
   - 3c. **MDX** — truy vấn + kết quả.
   - 3d. **Excel Pivot Table** — ảnh + nhận xét.
4. **Data Mining** — 2 thuật toán: phương pháp, code, kết quả, insight kinh doanh.
5. **Conclusion** + Appendix.

---

## 13. Lộ trình 9 Giai đoạn

| Phase | Nội dung | Output |
|-------|----------|--------|
| 0 | Cài phần mềm + tải dataset | Môi trường sẵn sàng |
| 1 | Tạo DB Staging + DW (schema SQL) | 2 database, các bảng rỗng |
| 2 | SSIS ETL (stage → dim → fact) | DW có dữ liệu, project SSIS |
| 3 | Dựng cube SSAS + deploy/process | SuperstoreCube chạy được |
| 4 | Browse thủ công + viết MDX (10 câu) | Ảnh SSAS + file MDX |
| 5 | Power BI dashboard (10 câu) | Superstore.pbix |
| 6 | Excel PivotTable nối cube | Superstore.xlsx |
| 7 | Python data mining (2 thuật toán) | .ipynb + .py + ảnh |
| 8 | Viết report (English) + quay video | report.docx/pdf + videos |
| 9 | Upload + share Google Drive | Link nộp bài |

---

## 14. Rủi ro & Lưu ý

- **SSAS cài nhầm Tabular mode** → không có MDX/cube. Phải đúng Multidimensional. (Rủi ro lớn nhất.)
- **Encoding CSV (latin-1)** → ký tự lỗi nếu đọc UTF-8. Khai báo đúng ở SSIS Flat File & Python.
- **Postal Code thiếu vài dòng** → xử lý null trong ETL.
- **Role-playing date** (Order vs Ship) → tạo 2 quan hệ tới DimDate trong DSV/cube.
- **Quyền share Drive** phải là "Anyone with the link" trước khi nộp.
- Data mining theo deliverable dùng **Python** (không bắt buộc dùng SSAS Data Mining).
```
