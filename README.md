# Invoice Extraction & Accounting Approval Agent 🚀

> **"Nó không chỉ dừng ở OCR. Nó nói cho bạn biết hóa đơn này có nên trả tiền không, và sai ở đâu."**

Hệ thống Agent tự động trích xuất thông tin hóa đơn (PDF/ảnh), chuẩn hóa cấu trúc dữ liệu kèm điểm tin cậy (_confidence), và **thực thi bộ quy tắc kế toán doanh nghiệp (Rule Engine)** để đưa ra quyết định phê duyệt thanh toán: **APPROVE**, **REVIEW**, hoặc **REJECT**.

---

## 🌟 Tính năng nổi bật

1. **Trích xuất thông minh & Điểm tin cậy (Confidence Score)**:
   - Trích xuất đầy đủ: Số hóa đơn, ngày phát hành, hạn thanh toán, nhà cung cấp, mã số thuế (MST), mã PO, bảng line items chi tiết, thuế, tổng tiền.
   - Tính toán `confidence` từng trường. Nếu confidence < 70% trên trường quan trọng, hệ thống tự động chuyển sang trạng thái `REVIEW`.

2. **Lớp kiểm tra hình thức & Số học (Validator)**:
   - Tự động phát hiện lỗi số học `MATH_ERROR`:
     - $quantity \times unit\_price \neq amount$ trên từng dòng hàng.
     - $\sum line\_items \neq subtotal$.
     - $subtotal + tax\_amount \neq total\_amount$.

3. **Bộ quy tắc nghiệp vụ 10 Rules đối chiếu Master Data**:
   - `VENDOR_UNKNOWN` (blocker): Nhà cung cấp không có trong hệ thống.
   - `VENDOR_BLOCKED` (blocker): Nhà cung cấp đang trong danh sách bị khóa / đình chỉ.
   - `TAX_ID_MISMATCH` (blocker): Mã số thuế trên hóa đơn không khớp hồ sơ đăng ký.
   - `PO_NOT_FOUND` (blocker): Mã PO không tồn tại trong hệ thống mua hàng.
   - `PO_VENDOR_MISMATCH` (blocker): Đơn đặt hàng thuộc về vendor khác.
   - `AMOUNT_EXCEEDS_PO` (blocker): Tổng tiền vượt ngân sách PO quá dung sai cho phép (2%).
   - `MATH_ERROR` (blocker): Sai lệch phép tính tiền hàng hoặc thuế.
   - `DUPLICATE_INVOICE` (blocker): Trùng lặp hóa đơn đã từng được thanh toán.
   - `LOW_CONFIDENCE` (warning): Điểm tin cậy OCR trường bắt buộc < 0.70.
   - `PAYMENT_TERMS_ODD` (warning): Kỳ hạn thanh toán lệch bất thường so với hợp đồng chuẩn của nhà cung cấp.

4. **Bộ 20 hóa đơn mẫu thực tế (ReportLab)**:
   - 10 hóa đơn hợp lệ chuẩn doanh nghiệp (được duyệt `APPROVE`).
   - 10 hóa đơn được thiết kế cố ý vi phạm từng rule cụ thể để kiểm thử và demo tức thì.

5. **Bộ Test tự động hồi quy (Pytest)**:
   - Đạt 24/24 tests tự động (100% pass rate) cho tất cả các rule, validator và quy trình end-to-end.

---

## 🏗 Kiến trúc hệ thống

```
[Upload PDF/Image]
       │
       ▼
[Ingest & Normalize]     (Tách trang, đọc nội dung, kiểm tra định dạng)
       │
       ▼
[Extraction Service]     (Model Vision / Smart Parser → JSON Schema + Confidence)
       │
       ▼
[Validator Service]      (Kiểm tra trường bắt buộc, tính đúng đắn số học)
       │
       ▼
[Rule Engine Service]    (Đối chiếu 10 rule với Master Data Vendors & POs)
       │
       ▼
[Decision Maker]         (Có blocker → REJECT | Có warning → REVIEW | Không lỗi → APPROVE)
       │
       ▼
[Audit Log & UI View]    (Lưu lịch sử & Hiển thị Dashboard trực quan)
```

---

## ⚡ Hướng dẫn cài đặt & Khởi chạy

### Cách 1: Chạy bằng Docker Compose (Khuyên dùng - 1 lệnh duy nhất)

```bash
docker compose up --build
```
- Backend API: `http://localhost:8000` (Tài liệu Swagger: `http://localhost:8000/docs`)
- Frontend Web App: `http://localhost:3000`

---

### Cách 2: Chạy trực tiếp trên máy bằng Virtual Environment (`venv`)

#### 1. Backend (FastAPI + Python trong `venv` cô lập)

**Cách nhanh (Windows 1-click):**
- Bấm đúp chuột chạy file: [`backend/run_backend.bat`](backend/run_backend.bat) (tự động kích hoạt venv và chạy server).
- Hoặc chạy test: [`backend/run_test.bat`](backend/run_test.bat).

**Hoặc chạy thủ công qua dòng lệnh:**
```bash
cd backend

# Kích hoạt môi trường ảo venv đã được tạo sẵn
.\venv\Scripts\activate

# Khởi chạy server FastAPI
python -m uvicorn app.main:app --reload --port 8000
```

#### 2. Chạy bộ kiểm thử tự động (Pytest trong `venv`)

```bash
cd backend
.\venv\Scripts\python.exe -m pytest tests -v
```
*Kết quả: 24/24 tests passed.*

#### 3. Frontend (Next.js 16 + Tailwind CSS)

```bash
cd frontend
npm install
npm run dev
```
Mở trình duyệt tại `http://localhost:3000`.

---

## 📡 API Endpoints chính

| Phương thức | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/extract` | Nhận file PDF/ảnh → Trả `InvoiceDocument` có cấu trúc & confidence |
| `POST` | `/api/review` | Thẩm định toàn diện → Trả `Decision` (APPROVE, REVIEW, REJECT) & Violations |
| `GET` | `/api/samples` | Danh sách 20 hóa đơn mẫu có sẵn để demo 1-click |
| `GET` | `/api/samples/{filename}/download` | Xem / Tải file PDF mẫu |
| `POST` | `/api/samples/{filename}/run` | Thẩm định trực tiếp hóa đơn mẫu theo tên file |
| `GET` | `/api/vendors` | Tra cứu Master Data nhà cung cấp |
| `GET` | `/api/pos` | Tra cứu danh sách Đơn đặt hàng (Purchase Orders) |
| `GET` | `/api/history` | Lịch sử các hóa đơn đã được xử lý (Audit log) |

---

## 📁 Cấu trúc thư mục

```
invoice-extraction-agent/
├── backend/
│   ├── app/
│   │   ├── api/routes.py            # API routes (extract, review, samples, master data)
│   │   ├── models/
│   │   │   ├── schema.py            # Pydantic schemas (InvoiceDocument, Violation, Decision)
│   │   │   └── database.py          # SQLAlchemy models (Vendors, POs, ProcessedInvoices)
│   │   ├── services/
│   │   │   ├── extractor.py         # Trích xuất PDF & tính điểm tin cậy
│   │   │   ├── validator.py         # Kiểm tra tính đúng đắn số học & hình thức
│   │   │   ├── rule_engine.py       # 10 business rules kế toán
│   │   │   ├── decision.py          # Bộ gộp quyết định phê duyệt
│   │   │   └── seed_data.py         # Seed 10 vendors và 20 POs
│   │   └── main.py                  # FastAPI Application
│   ├── sample_data/invoices/        # 20 file PDF hóa đơn mẫu
│   ├── scripts/
│   │   └── generate_sample_invoices.py # Script sinh hóa đơn bằng ReportLab
│   ├── tests/
│   │   ├── test_rules.py            # Unit tests cho từng rule
│   │   ├── test_validator.py        # Unit tests kiểm tra MATH_ERROR
│   │   └── test_pipeline.py         # Test hồi quy 20 file mẫu
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                        # Next.js 16 Web Dashboard
├── docker-compose.yml
└── README.md
```
