# Giải thích 2 thuật toán Data Mining — tài liệu ôn bảo vệ

> Dựa trên kết quả chạy thật của `data_mining.py`.
> Triết lý chung: chọn **1 thuật toán có giám sát (supervised) + 1 không giám sát (unsupervised)** để bao quát cả hai nhánh chính của data mining → đây là điểm mạnh nên nói đầu tiên với mentor.

---

## THUẬT TOÁN 1 — Decision Tree (Phân lớp có giám sát)

### Bài toán
Dự đoán một **dòng đơn hàng** sẽ **Lãi (Profit > 0)** hay **Lỗ**, dựa trên:
- Biến số: `Sales`, `Quantity`, `Discount`
- Biến phân loại (one-hot): `Category`, `Sub-Category`, `Region`, `Segment`, `Ship Mode`

Đây là **phân lớp nhị phân (binary classification)**. Random Forest được train thêm để **đối chứng**.

### Vì sao chọn Decision Tree
1. **Diễn giải được (white-box):** bài toán kinh doanh cần biết *VÌ SAO* một đơn lỗ, không chỉ dự đoán. Cây cho ra luật if-then rõ ràng (vd: `Discount > 0.2 → Lỗ`). Mentor rất thích điều này.
2. **Không cần chuẩn hóa dữ liệu** (khác K-Means) — cây chia theo ngưỡng nên không quan tâm thang đo.
3. **Xử lý cả biến số lẫn phân loại**, bắt được **quan hệ phi tuyến** và **tương tác** giữa các biến.
4. Train nhanh, nhẹ.

### Điểm mạnh
- Trực quan, vẽ được, giải thích từng quyết định.
- Cho ra **feature importance** — biết yếu tố nào quyết định lãi/lỗ.
- Không cần scale, ít tiền xử lý.

### Điểm yếu (phải thuộc)
- **Dễ overfit** nếu cây sâu → ta giới hạn `max_depth=4` để chống overfit + dễ đọc.
- **Variance cao / không ổn định:** đổi chút dữ liệu → cây khác hẳn. → Chính là lý do đối chứng bằng **Random Forest** (ensemble nhiều cây, lấy trung bình → giảm variance).
- Ranh giới quyết định dạng **bậc thang** (song song trục), không mượt.
- **Thiên về lớp đa số** khi dữ liệu mất cân bằng (đúng case này).

### Random Forest dùng để làm gì
Ensemble 200 cây (bagging + chọn ngẫu nhiên feature). Thường **chính xác & ổn định hơn** 1 cây.
→ Kết quả: **RF = 0.9428 ≈ DT = 0.944**. RF *không* tốt hơn → nghĩa là **quan hệ trong dữ liệu khá đơn giản, 1 cây depth-4 đã đủ**. Lập luận với mentor: *"Vì mô hình đơn giản đã giải thích tốt, em ưu tiên Decision Tree vì tính diễn giải."*

### Giải thích OUTPUT (số thật)

**1) Class balance: 80.6% Lãi / 19.4% Lỗ → DỮ LIỆU MẤT CÂN BẰNG.**
→ Đây là điểm mentor HAY HỎI NHẤT. Vì 80.6% là lãi, một mô hình "ngu" đoán *tất cả là lãi* đã đạt 80.6% accuracy (gọi là **baseline / no-information rate**). Nên **accuracy đơn thuần dễ gây hiểu nhầm** — phải nhìn precision/recall/F1 cho lớp thiểu số (Lỗ).

**2) Accuracy = 0.944 (94.4%).** Cao hơn baseline 80.6% đáng kể → mô hình thực sự học được, không phải đoán bừa.

**3) Confusion Matrix** (hàng = thực tế, cột = dự đoán; lớp 0 = Lỗ, lớp 1 = Lãi), tập test 2.499 dòng:

|  | Đoán LỖ (0) | Đoán LÃI (1) |
|---|---|---|
| **Thực tế LỖ (0)** | **369** (đúng) | 115 (bỏ sót lỗ) |
| **Thực tế LÃI (1)** | 25 (báo nhầm lỗ) | **1990** (đúng) |

- 369 = đơn lỗ bắt đúng; 115 = đơn lỗ bị bỏ sót (tưởng lãi); 25 = đơn lãi bị báo nhầm thành lỗ; 1990 = đơn lãi đúng.

**4) Precision / Recall / F1:**
- **Lớp Lỗ (0):** precision **0.94** (trong các đơn mô hình nói "lỗ", 94% đúng), recall **0.76** (bắt được 76% số đơn lỗ thực tế, **bỏ sót 24% = 115/484**), F1 **0.84**.
- **Lớp Lãi (1):** precision **0.95**, recall **0.99** (gần như bắt hết), F1 **0.97**.
- **Macro avg = 0.90** (trung bình KHÔNG trọng số 2 lớp — chỉ số công bằng cho dữ liệu lệch). **Weighted avg = 0.94**.
→ Kết luận: mô hình rất tốt với lớp Lãi, **kém hơn ở lớp Lỗ** (recall 0.76) do mất cân bằng → bỏ sót một phần đơn lỗ.

**5) `feature_importance.png`:** xếp hạng biến quan trọng. Với Superstore thường **Discount** đứng đầu (giảm giá cao → lỗ), tiếp theo là vài `Sub-Category` (Tables, Bookcases, Binders hay lỗ), `Sales`, `Quantity`. → **Hãy mở file này xem top biến của chính bạn để nói cụ thể.**

**6) `decision_tree.png`:** đọc từ gốc xuống. Mỗi node có: điều kiện chia (vd `Discount <= 0.2`), `gini` (độ lẫn lớp, 0 = thuần), `samples`, `value=[số lỗ, số lãi]`, `class`. Lần theo nhánh đến lá `class = Loss` chính là **"công thức" của đơn lỗ**.

### Câu mentor có thể hỏi + cách trả lời
- *"Accuracy 94% có cao thật không?"* → So baseline 80.6%; nhìn thêm recall lớp Lỗ (0.76) mới đánh giá đúng.
- *"Dữ liệu mất cân bằng xử lý sao?"* → Có thể dùng `class_weight='balanced'`, SMOTE, chỉnh threshold; ở đây ta dùng `stratify` để giữ đúng tỷ lệ lớp khi chia train/test.
- *"Có rò rỉ dữ liệu (data leakage) không?"* → Không. `Sales`, `Discount` đều **biết tại thời điểm đặt hàng**, còn Profit phụ thuộc giá vốn + chiết khấu → Profit **không suy ra trực tiếp** từ feature → hợp lệ.
- *"Vì sao max_depth=4?"* → chống overfit + cây đủ nhỏ để đọc/giải thích.
- *"Cải thiện thế nào?"* → cross-validation, cân bằng lớp, thêm feature (lợi nhuận/đơn vị), tuning hyperparameter.

---

## THUẬT TOÁN 2 — K-Means trên RFM (Phân cụm không giám sát)

### Bài toán
Nhóm **793 khách hàng** theo hành vi mua, dùng 3 đặc trưng **RFM**:
- **Recency** = số ngày từ lần mua **gần nhất** (càng NHỎ càng tốt).
- **Frequency** = số đơn hàng riêng biệt (`nunique Order ID`) (càng CAO càng tốt).
- **Monetary** = tổng `Sales` (càng CAO càng tốt).

Mốc tính Recency: `snapshot = max(Order Date) + 1 ngày`.

### Vì sao chọn RFM + K-Means
1. **RFM** là khung **chuẩn ngành** đo giá trị khách hàng → dễ thuyết phục về kinh doanh.
2. **K-Means** là thuật toán phân cụm phổ biến nhất: nhanh, đơn giản, dễ giải thích, hợp khi cụm dạng cầu.
3. Là **unsupervised** (không cần nhãn) — đúng bản chất "khám phá phân khúc mà ta chưa biết trước".

### Vì sao PHẢI chuẩn hóa (StandardScaler) — mentor hay hỏi
R, F, M khác đơn vị và thang đo cực mạnh: Monetary tới hàng **nghìn $**, Frequency vài chục, Recency vài trăm ngày. K-Means dùng **khoảng cách Euclid** → nếu không chuẩn hóa, biến thang lớn (Monetary) sẽ **át** hai biến kia. Chuẩn hóa z-score đưa cả 3 về cùng thang → công bằng.

### Vì sao k = 4 (Elbow method)
`elbow.png` vẽ **inertia** (tổng bình phương khoảng cách trong cụm) theo k = 1..8. Inertia luôn giảm khi k tăng; ta chọn **"khuỷu tay"** — nơi inertia bắt đầu giảm chậm lại. Chọn **k=4** vì vừa nằm vùng khuỷu, vừa cho **4 phân khúc có ý nghĩa kinh doanh rõ ràng**. (Tham số `n_init=10`: chạy 10 lần với khởi tạo khác nhau lấy kết quả tốt nhất; `random_state=42`: tái lập được.)

### Điểm mạnh K-Means
- Nhanh, scale tốt với dữ liệu lớn, đơn giản, dễ diễn giải.
- Hội tụ nhanh.

### Điểm yếu (phải thuộc)
- **Phải chọn k trước** (ta dùng Elbow; có thể bổ sung **Silhouette score** cho chặt hơn).
- **Nhạy với khởi tạo** → khắc phục bằng `n_init=10`.
- Giả định **cụm hình cầu, kích thước tương đương** — sai nếu cụm dài/khác mật độ.
- **Nhạy với outlier:** khách chi cực lớn kéo lệch tâm cụm (Monetary có đuôi dài — xem Cluster 2).
- Chỉ dùng **biến số**.
- Thay thế khả dĩ: **Hierarchical clustering, DBSCAN, GMM**.

### Giải thích OUTPUT (số thật — 793 khách, 4 cụm)

| Cluster | Recency | Frequency | Monetary | Count | Tên phân khúc | Hành động |
|---|---|---|---|---|---|---|
| **2** | 123.7 | 8.3 | **9.479** | 64 | **VIP / Champions** — chi cao gấp ~3 lần | Chăm sóc đặc biệt, loyalty, upsell |
| **0** | **72.7** | **8.5** | 3.322 | 298 | **Trung thành / Active** — mua gần đây & thường xuyên nhất | Giữ chân, cross-sell, nâng lên VIP |
| **1** | 101.2 | 4.7 | 1.669 | 335 | **Phổ thông / Trung bình** — đông nhất | Khuyến mãi kích cầu, tăng tần suất |
| **3** | **559.5** | 3.7 | 1.470 | 96 | **Rời bỏ / Lost** — ~1.5 năm không mua | Chiến dịch win-back, hoặc buông nếu chi phí cao |

Tổng 64 + 298 + 335 + 96 = **793** ✓

`segments.png`: scatter **Frequency (x) vs Monetary (y)** tô màu theo cụm — Cluster 2 nằm trên cao (Monetary lớn), Cluster 3 dồn dưới thấp.

### Câu mentor có thể hỏi + cách trả lời
- *"Vì sao k=4?"* → Elbow + ý nghĩa kinh doanh (4 phân khúc rõ ràng).
- *"Vì sao chuẩn hóa?"* → khoảng cách Euclid, tránh Monetary lấn át.
- *"Đánh giá chất lượng cụm thế nào?"* → inertia (đã có), bổ sung **Silhouette score**.
- *"K-Means nhược điểm gì?"* → như trên; nêu thuật toán thay thế.
- *"Recency/Frequency/Monetary tính từ đâu?"* → snapshot = max(Order Date)+1; Frequency = số đơn riêng biệt; Monetary = tổng Sales.
- *"Sao Monetary dùng Sales mà không dùng Profit?"* → Sales = giá trị khách mang lại về doanh thu; nếu muốn xét lợi nhuận có thể đổi sang tổng Profit.

---

## Tóm tắt 30 giây để mở đầu khi bảo vệ
> "Em dùng 2 thuật toán đại diện 2 nhánh data mining: **Decision Tree** (có giám sát) để **phân lớp đơn hàng lãi/lỗ** — đạt accuracy 94.4%, và quan trọng là **diễn giải được** yếu tố gây lỗ (chủ yếu là Discount); và **K-Means trên RFM** (không giám sát) để **phân khúc 793 khách thành 4 nhóm** (VIP, Trung thành, Phổ thông, Rời bỏ) phục vụ marketing. Em cũng lưu ý dữ liệu phân lớp **mất cân bằng 80/20** nên đánh giá bằng precision/recall chứ không chỉ accuracy."
