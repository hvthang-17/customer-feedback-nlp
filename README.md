# MailFlow NLP

Demo hệ thống phân loại và định tuyến email khách hàng tiếng Việt.

## Chạy nhanh

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Mở `http://127.0.0.1:8000`. API có tài liệu tại `/docs`.

## API chính

- `POST /api/emails`: nạp một email JSON (hỗ trợ header `Idempotency-Key`)
- `POST /api/import`: nạp danh sách email JSON
- `POST /api/import/csv`: nạp CSV (body UTF-8, header: `subject,body,sender,received_at`)
- `GET /api/emails`, `GET /api/review-queue`, `GET /api/dashboard`
- `POST /api/emails/{id}/review`: duyệt/chỉnh phòng ban
- `PATCH /api/emails/{id}/status`: cập nhật trạng thái xử lý

Các dữ liệu demo được khởi tạo tự động trong `data/mailflow.db`. Không dùng email thật.
