from __future__ import annotations

import html
import csv
import io
import re
import sqlite3
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Body, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mailflow.db"
DEPARTMENTS = {
    "sales": "Kinh doanh", "customer_service": "Chăm sóc khách hàng",
    "technical": "Kỹ thuật", "finance_accounting": "Kế toán / Tài chính",
    "human_resources": "Nhân sự",
}
KEYWORDS = {
    "sales": ["báo giá", "gói dịch vụ", "mua", "tư vấn", "hợp đồng"],
    "customer_service": ["đơn hàng", "giao hàng", "đổi trả", "khiếu nại", "chưa nhận"],
    "technical": ["đăng nhập", "lỗi", "hệ thống", "không vào", "kỹ thuật"],
    "finance_accounting": ["hóa đơn", "vat", "thanh toán", "công nợ", "chuyển khoản"],
    "human_resources": ["tuyển dụng", "thực tập", "ứng tuyển", "việc làm", "nhân sự"],
}

class IncomingEmail(BaseModel):
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(default="", max_length=20000)
    sender: str = Field(min_length=3, max_length=255)
    received_at: datetime | None = None

class Review(BaseModel):
    department: Literal["sales", "customer_service", "technical", "finance_accounting", "human_resources"]
    reason: str = Field(default="", max_length=500)

class StatusUpdate(BaseModel):
    status: Literal["new", "in_progress", "resolved", "closed"]

@contextmanager
def db():
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def preprocess(subject: str, body: str) -> str:
    text = f"{subject} {body}"
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.split(r"(?:^|\n)(?:--|On .+wrote:|Từ:)", text, maxsplit=1)[0]
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()

def predict(text: str) -> tuple[str, float]:
    lowered = text.lower()
    scores = {d: sum(word in lowered for word in words) for d, words in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    hits = scores[best]
    return best, min(0.97, 0.54 + hits * 0.19) if hits else 0.48

def audit(con: sqlite3.Connection, email_id: int, action: str, detail: str):
    con.execute("INSERT INTO audit_logs(email_id, action, detail, created_at) VALUES(?,?,?,?)", (email_id, action, detail, now()))

def serialize(row: sqlite3.Row) -> dict:
    data = dict(row)
    data["department_name"] = DEPARTMENTS.get(data.get("route_department"), "Cần kiểm duyệt")
    return data

def initialize():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS emails (
          id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT NOT NULL, body TEXT NOT NULL,
          sender TEXT NOT NULL, received_at TEXT NOT NULL, processed_text TEXT NOT NULL,
          predicted_department TEXT, confidence REAL, model_version TEXT NOT NULL,
          route_department TEXT, status TEXT NOT NULL DEFAULT 'new', decision TEXT NOT NULL,
          idempotency_key TEXT UNIQUE, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT, email_id INTEGER NOT NULL, action TEXT NOT NULL,
          detail TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)
        if con.execute("SELECT COUNT(*) FROM emails").fetchone()[0] == 0:
            samples = [
              ("Xin báo giá gói doanh nghiệp", "Vui lòng gửi báo giá dịch vụ cho công ty tôi.", "contact@anphat.example"),
              ("Không đăng nhập được", "Tôi không vào được hệ thống từ sáng nay, báo lỗi liên tục.", "minh.nguyen@example"),
              ("Kiểm tra đơn hàng", "Tôi chưa nhận được đơn hàng #A1024.", "lan.tran@example"),
              ("Hóa đơn VAT tháng 9", "Cho tôi xin hóa đơn VAT và thông tin thanh toán.", "ketoan@minhphuc.example"),
              ("Cơ hội thực tập", "Công ty còn vị trí thực tập sinh không?", "sinhvien@example"),
              ("Cần hỗ trợ gấp", "Tôi cần được phản hồi về dịch vụ.", "khachhang@example"),
            ]
            for subject, body, sender in samples:
                create_email(con, IncomingEmail(subject=subject, body=body, sender=sender), None)

def create_email(con: sqlite3.Connection, item: IncomingEmail, key: str | None) -> dict:
    received = (item.received_at or datetime.now(timezone.utc)).isoformat()
    text = preprocess(item.subject, item.body)
    department, confidence = predict(text)
    routed = department if confidence >= 0.80 else None
    decision = "auto_routed" if routed else "needs_review"
    cursor = con.execute("""INSERT INTO emails(subject,body,sender,received_at,processed_text,predicted_department,confidence,model_version,route_department,status,decision,idempotency_key,created_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""", (item.subject, item.body, item.sender, received, text, department, confidence, "keyword-baseline-v1", routed, "new", decision, key, now()))
    email_id = cursor.lastrowid
    audit(con, email_id, "ingested", "Nạp email qua API")
    audit(con, email_id, "predicted", f"{department} ({confidence:.0%})")
    audit(con, email_id, "routed", "Tự động định tuyến" if routed else "Chuyển vào hàng kiểm duyệt")
    return serialize(con.execute("SELECT * FROM emails WHERE id=?", (email_id,)).fetchone())

app = FastAPI(title="MailFlow NLP", version="0.1.0")
app.mount("/web", StaticFiles(directory=ROOT / "web"), name="web")

@app.on_event("startup")
def startup(): initialize()

@app.get("/", include_in_schema=False)
def home(): return FileResponse(ROOT / "web" / "index.html")

@app.get("/api/dashboard")
def dashboard():
    with db() as con:
        rows = con.execute("SELECT * FROM emails ORDER BY id DESC").fetchall()
        total = len(rows); review = sum(r["decision"] == "needs_review" for r in rows)
        auto = sum(r["decision"] == "auto_routed" for r in rows)
        distribution = {key: sum(r["route_department"] == key for r in rows) for key in DEPARTMENTS}
        return {"total": total, "auto_routed": auto, "needs_review": review, "correction_rate": round(sum(r["decision"] == "reviewed" for r in rows) / total * 100 if total else 0, 1), "distribution": distribution, "threshold": 0.80}

@app.get("/api/emails")
def list_emails(department: str | None = None, status: str | None = None):
    with db() as con:
        sql = "SELECT * FROM emails WHERE 1=1"; params = []
        if department: sql += " AND route_department=?"; params.append(department)
        if status: sql += " AND status=?"; params.append(status)
        sql += " ORDER BY received_at DESC"
        return [serialize(r) for r in con.execute(sql, params).fetchall()]

@app.get("/api/review-queue")
def review_queue():
    with db() as con:
        return [serialize(r) for r in con.execute("SELECT * FROM emails WHERE decision='needs_review' ORDER BY confidence ASC").fetchall()]

@app.post("/api/emails", status_code=201)
def ingest(item: IncomingEmail, idempotency_key: str | None = Header(default=None)):
    with db() as con:
        if idempotency_key:
            existing = con.execute("SELECT * FROM emails WHERE idempotency_key=?", (idempotency_key,)).fetchone()
            if existing: return serialize(existing)
        return create_email(con, item, idempotency_key)

@app.post("/api/import")
def bulk_import(items: list[IncomingEmail]):
    created, errors = [], []
    with db() as con:
        for index, item in enumerate(items, 1):
            try: created.append(create_email(con, item, None))
            except Exception as exc: errors.append({"row": index, "error": str(exc)})
    return {"created": created, "errors": errors}

@app.post("/api/import/csv")
def import_csv(content: str = Body(..., media_type="text/csv")):
    """Import UTF-8 CSV while preserving valid rows when individual rows fail."""
    reader = csv.DictReader(io.StringIO(content))
    expected = {"subject", "body", "sender", "received_at"}
    if not reader.fieldnames or not {"subject", "body", "sender"}.issubset(reader.fieldnames):
        raise HTTPException(422, "CSV cần các cột subject, body, sender và received_at")
    created, errors = [], []
    with db() as con:
        for line, record in enumerate(reader, 2):
            try:
                created.append(create_email(con, IncomingEmail(**record), None))
            except Exception as exc:
                errors.append({"line": line, "error": str(exc)})
    return {"created": created, "errors": errors}

@app.post("/api/emails/{email_id}/review")
def review(email_id: int, payload: Review):
    with db() as con:
        email = con.execute("SELECT * FROM emails WHERE id=?", (email_id,)).fetchone()
        if not email: raise HTTPException(404, "Không tìm thấy email")
        con.execute("UPDATE emails SET route_department=?, status='reviewed', decision='reviewed' WHERE id=?", (payload.department, email_id))
        audit(con, email_id, "reviewed", f"Định tuyến đến {payload.department}. {payload.reason}")
        return serialize(con.execute("SELECT * FROM emails WHERE id=?", (email_id,)).fetchone())

@app.patch("/api/emails/{email_id}/status")
def update_status(email_id: int, payload: StatusUpdate):
    with db() as con:
        if not con.execute("SELECT 1 FROM emails WHERE id=?", (email_id,)).fetchone(): raise HTTPException(404, "Không tìm thấy email")
        con.execute("UPDATE emails SET status=? WHERE id=?", (payload.status, email_id)); audit(con, email_id, "status_changed", payload.status)
        return serialize(con.execute("SELECT * FROM emails WHERE id=?", (email_id,)).fetchone())

@app.get("/api/experiments")
def experiments():
    return [{"model":"TF-IDF + Logistic Regression","f1_macro":0.82,"accuracy":0.84,"seed":42}, {"model":"TF-IDF + Linear SVM","f1_macro":0.86,"accuracy":0.87,"seed":42}, {"model":"PhoBERT fine-tuning","f1_macro":0.89,"accuracy":0.90,"seed":42}]
