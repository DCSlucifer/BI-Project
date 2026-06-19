# Business Intelligence Final Project: Superstore

## Tổng quan

Dự án xây dựng một giải pháp Business Intelligence end-to-end trên bộ dữ liệu Superstore. Luồng chính gồm nạp dữ liệu từ CSV, xây dựng staging và data warehouse, xử lý ETL bằng SSIS, dựng cube bằng SSAS Multidimensional, phân tích bằng MDX, Power BI, Excel PivotTable và thực hiện data mining bằng Python.

Mục tiêu của dự án là tạo một hệ thống phân tích có thể trả lời các câu hỏi kinh doanh về doanh thu, lợi nhuận, khu vực, sản phẩm, khách hàng, phương thức giao hàng và phân khúc khách hàng.

## Kiến trúc

```text
Sample - Superstore.csv
    -> SQL Server Staging database
    -> SQL Server Data Warehouse
    -> SSIS ETL package
    -> SSAS Multidimensional cube
    -> MDX, Power BI, Excel PivotTable
    -> Python data mining
```

Data warehouse sử dụng star schema với một bảng fact và năm bảng dimension:

| Thành phần | Mô tả |
| --- | --- |
| FactSales | Lưu dữ liệu giao dịch bán hàng ở mức từng dòng sản phẩm trong đơn hàng |
| DimDate | Lưu thông tin ngày đặt hàng và ngày giao hàng |
| DimProduct | Lưu thông tin sản phẩm, danh mục và nhóm sản phẩm |
| DimCustomer | Lưu thông tin khách hàng và phân khúc |
| DimGeography | Lưu thông tin quốc gia, vùng, bang, thành phố và mã bưu chính |
| DimShipMode | Lưu thông tin phương thức giao hàng |

## Cấu trúc thư mục

```text
.
|-- DataMining/     Mã Python và kết quả data mining
|-- dataset/        Bộ dữ liệu Superstore gốc
|-- docs/           Tài liệu thiết kế và kế hoạch triển khai
|-- Excel/          File Excel PivotTable
|-- mdx/            Truy vấn MDX
|-- PowerBI/        File Power BI Desktop
|-- Report/         Tài liệu, hình ảnh và nội dung báo cáo
|-- sql/            Script tạo staging, data warehouse và kiểm tra ETL
|-- SSAS/           Project SSAS Multidimensional
`-- SSIS/           Project SSIS ETL
```

## Công nghệ sử dụng

| Nhóm | Công cụ |
| --- | --- |
| Database | SQL Server 2022 Developer Edition |
| ETL | SQL Server Integration Services |
| OLAP | SQL Server Analysis Services Multidimensional |
| Query | SQL, MDX |
| Dashboard | Power BI Desktop |
| Pivot analysis | Microsoft Excel |
| Data mining | Python, pandas, scikit-learn, matplotlib |
| IDE | Visual Studio 2022, SQL Server Management Studio |

## Yêu cầu môi trường

1. SQL Server 2022 Developer Edition có cài Database Engine và Analysis Services.
2. Analysis Services phải chạy ở chế độ Multidimensional and Data Mining Mode.
3. SQL Server Management Studio.
4. Visual Studio 2022 với hai extension:
   - SQL Server Integration Services Projects 2022
   - Microsoft Analysis Services Projects
5. Power BI Desktop.
6. Microsoft Excel.
7. Python 3 hoặc Anaconda, kèm các thư viện:
   - pandas
   - numpy
   - matplotlib
   - scikit-learn

## Thiết lập database

Chạy các script trong thư mục `sql` bằng SQL Server Management Studio theo thứ tự sau:

```text
sql/01_create_staging.sql
sql/02_create_dw.sql
sql/03_populate_dimdate.sql
```

Sau khi chạy xong, hệ thống sẽ có hai database:

| Database | Mục đích |
| --- | --- |
| SuperstoreStaging | Lưu dữ liệu thô được nạp từ file CSV |
| SuperstoreDW | Lưu data warehouse theo mô hình star schema |

## Chạy ETL bằng SSIS

1. Mở solution trong thư mục `SSIS/Integration Services Project1`.
2. Kiểm tra lại các connection manager:
   - `OLEDB_Staging` trỏ đến database `SuperstoreStaging`.
   - `OLEDB_DW` trỏ đến database `SuperstoreDW`.
   - Flat File Connection trỏ đến `dataset/Sample - Superstore.csv`.
3. Đảm bảo file CSV được đọc với encoding Windows-1252 hoặc Latin-1.
4. Chạy package `ETL_Main.dtsx`.
5. Kiểm tra kết quả bằng script:

```text
sql/06_verify.sql
```

Kết quả hợp lệ khi số dòng, tổng Sales và tổng Profit giữa staging và fact table khớp nhau, đồng thời các kiểm tra orphan key đều bằng 0.

## Dựng cube SSAS

1. Mở solution trong thư mục `SSAS/SuperstoreSSAS`.
2. Kiểm tra data source trỏ đến database `SuperstoreDW`.
3. Kiểm tra các dimension, hierarchy và measure trong project.
4. Deploy và process project trên SSAS instance local.
5. Mở cube bằng SSMS hoặc Visual Studio để kiểm tra dữ liệu theo năm, khu vực, sản phẩm và khách hàng.

## Phân tích bằng MDX

Các truy vấn MDX nằm trong file:

```text
mdx/queries.mdx
```

File này bao gồm các truy vấn cho các nhóm phân tích chính:

| Nhóm phân tích | Nội dung |
| --- | --- |
| Thời gian | Sales và Profit theo năm, quý; tăng trưởng YoY |
| Địa lý | Sales và Profit theo region, state |
| Sản phẩm | Top sản phẩm, category, sub-category |
| Khách hàng | Segment, top khách hàng theo doanh thu |
| Giao hàng | Ship mode và thời gian giao hàng trung bình |
| Lợi nhuận | Profit margin và tác động của discount |

## Power BI và Excel

File Power BI:

```text
PowerBI/Superstore.pbix
```

File Excel:

```text
Excel/Superstore.xlsx
```

Power BI được dùng để xây dựng dashboard trực quan cho các câu hỏi phân tích. Excel được dùng để kết nối cube và tạo PivotTable hoặc PivotChart phục vụ phần phân tích OLAP.

## Data mining

Mã nguồn data mining nằm trong:

```text
DataMining/data_mining.py
```

Chạy script từ thư mục `DataMining`:

```powershell
cd DataMining
python data_mining.py
```

Script thực hiện hai nhóm thuật toán:

| Thuật toán | Mục tiêu |
| --- | --- |
| Decision Tree Classification | Dự đoán dòng đơn hàng có lợi nhuận hay bị lỗ dựa trên Sales, Quantity, Discount và các thuộc tính phân loại |
| K-Means Clustering | Phân cụm khách hàng theo RFM gồm Recency, Frequency và Monetary |

Kết quả được tạo trong thư mục `DataMining/outputs`, bao gồm biểu đồ, bảng profile phân cụm và file dữ liệu khách hàng sau khi phân cụm.

## Kiểm tra nhanh

Sau khi hoàn tất ETL và triển khai cube, nên kiểm tra các điểm sau:

| Hạng mục | Kỳ vọng |
| --- | --- |
| `SuperstoreStaging.dbo.stg_Orders` | Có 9,994 dòng dữ liệu |
| `SuperstoreDW.dbo.FactSales` | Có 9,994 dòng dữ liệu |
| `sql/06_verify.sql` | Tổng Sales, Profit khớp giữa staging và fact |
| SSAS cube | Browse được Sales, Profit theo năm hoặc category |
| MDX | Các truy vấn trong `mdx/queries.mdx` trả về dữ liệu |
| Python | Script chạy xong và sinh kết quả trong `DataMining/outputs` |

## Ghi chú về quản lý mã nguồn

File `.gitignore` được cấu hình để loại bỏ cache, file build, file tạm và cấu hình local. Các deliverable chính như dataset CSV, Power BI, Excel, SQL script, MDX, SSIS source, SSAS source và kết quả trong `DataMining/outputs` không bị ignore để có thể lưu cùng dự án khi cần nộp bài hoặc chia sẻ.
