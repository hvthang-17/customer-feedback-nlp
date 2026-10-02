"""
Script huấn luyện và đánh giá mô hình TF-IDF + SVM:
1. Phân loại Lĩnh vực (Topic Classification) -> 5 Hàng đợi nghiệp vụ + Hàng đợi kiểm duyệt.
2. Phân tích Cảm xúc (Sentiment Analysis) -> positive, negative, neutral.
3. Xuất kết quả đánh giá (F1-Macro, Precision, Recall, Confusion Matrix) ra models/evaluation_metrics.json.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.nlp.trainer import run_training_pipeline

if __name__ == "__main__":
    print("Đang khởi chạy Pipeline Huấn luyện Mô hình TF-IDF + SVM...")
    run_training_pipeline()
