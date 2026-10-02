import unittest
import os
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app, db, initialize

class DataIngestionTests(unittest.TestCase):
    def setUp(self):
        initialize()
        self.client = TestClient(app)

    def test_single_ingestion_with_idempotency_key(self):
        payload = {
            "text": "Ứng dụng bị lỗi không thể chuyển tiền vào buổi sáng",
            "source": "mobile_app"
        }
        headers = {"Idempotency-Key": "test-key-12345"}
        
        # First request
        res1 = self.client.post("/api/emails", json=payload, headers=headers)
        self.assertEqual(res1.status_code, 201)
        data1 = res1.json()
        
        # Second request with identical Idempotency-Key
        res2 = self.client.post("/api/emails", json=payload, headers=headers)
        self.assertEqual(res2.status_code, 201)
        data2 = res2.json()
        
        # Must return existing record without duplicating in database
        self.assertEqual(data1["id"], data2["id"])

    def test_bulk_json_import_with_row_error_handling(self):
        payload = [
            {"text": "Tôi cần xin lại hóa đơn VAT", "source": "web"},
            {"text": "Tài khoản tiết kiệm online", "source": "mobile_app"}
        ]
        res = self.client.post("/api/import", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["created"]), 2)
        self.assertEqual(len(data["errors"]), 0)

    def test_csv_import_row_level_errors(self):
        csv_content = "text,source\nYêu cầu hỗ trợ về thẻ ATM,call_center\nNội dung khiếu nại cước dịch vụ,web"
        res = self.client.post("/api/import/csv", content=csv_content, headers={"Content-Type": "text/csv"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["created"]), 2)

if __name__ == "__main__":
    unittest.main()