import joblib
import re
from pathlib import Path
import numpy as np
from app.nlp.preprocessor import preprocess_vietnamese_text

ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT / "models"

DOMAIN_KEYWORDS = {
    "digital_banking": ["đăng nhập", "dang nhap", "app", "ứng dụng", "ung dung", "mobile banking", "internet banking", "otp", "văng", "lỗi ứng dụng"],
    "card_account": ["thẻ", "the", "atm", "thẻ tín dụng", "thẻ ghi nợ", "nuốt thẻ", "khóa thẻ", "đổi pin", "tài khoản", "số dư"],
    "credit_savings": ["lãi suất", "lai suat", "tiết kiệm", "tiet kiem", "khoản vay", "khoan vay", "vay", "thế chấp", "trả góp", "sổ tiết kiệm"],
    "payment_transfer": ["chuyển tiền", "chuyen tien", "chuyển khoản", "chuyen khoan", "thanh toán", "thanh toan", "hóa đơn", "hoa don", "phí chuyển", "nạp tiền"]
}

POSITIVE_KEYWORDS = ["hài lòng", "hai long", "chu đáo", "chu dao", "nhanh chóng", "nhanh chong", "nhiệt tình", "nhiet tinh", "lịch sự", "lich su", "tuyệt vời", "tuyet voi", "xuất sắc", "xuat sac", "cảm ơn", "cam on", "khen"]
COMPLAINT_KEYWORDS = ["bực mình", "buc minh", "tệ", "te", "lỗi", "loi", "chờ lâu", "cho lau", "bị trừ tiền", "bi tru tien", "nuốt thẻ", "nuot the", "không thể", "khong the", "chưa tốt", "chua tot", "văng"]
INQUIRY_PATTERNS = [r"cho tôi hỏi", r"cho toi hoi", r"thủ tục", r"thu tuc", r"điều kiện", r"dieu kien", r"như thế nào", r"nhu the nao", r"bao nhiêu", r"bao nhieu", r"khi nào", r"khi nao"]

class FeedbackPredictor:
    """Module dự đoán phân loại lĩnh vực và phân tích cảm xúc phản hồi khách hàng (Hybrid ML + Rule Guard)."""

    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models_dir = models_dir
        self.topic_model = None
        self.sentiment_model = None
        self._load_models()

    def _load_models(self):
        topic_path = self.models_dir / "topic_model.joblib"
        sentiment_path = self.models_dir / "sentiment_model.joblib"

        if topic_path.exists():
            self.topic_model = joblib.load(topic_path)
        if sentiment_path.exists():
            self.sentiment_model = joblib.load(sentiment_path)

    def is_ready(self) -> bool:
        return self.topic_model is not None and self.sentiment_model is not None

    def predict_topic(self, text: str) -> dict:
        """Dự đoán lĩnh vực nghiệp vụ kết hợp ML TF-IDF + SVM và Domain Keyword Boosting."""
        cleaned = preprocess_vietnamese_text(text)
        lowered = text.lower()

        if self.topic_model:
            probas = self.topic_model.predict_proba([cleaned])[0]
            classes = list(self.topic_model.classes_)
            prob_dict = {str(c): float(p) for c, p in zip(classes, probas)}
        else:
            classes = ["card_account", "credit_savings", "customer_service", "digital_banking", "needs_review", "payment_transfer"]
            prob_dict = {c: 1.0 / len(classes) for c in classes}

        boosted_scores = prob_dict.copy()
        for dept, keywords in DOMAIN_KEYWORDS.items():
            if dept in boosted_scores:
                hit_count = sum(1 for kw in keywords if kw in lowered)
                if hit_count > 0:
                    boosted_scores[dept] += hit_count * 0.35

        total = sum(boosted_scores.values())
        norm_probs = {c: round(score / total, 4) for c, score in boosted_scores.items()}

        best_topic = max(norm_probs, key=norm_probs.get)
        best_confidence = norm_probs[best_topic]

        return {
            "topic": best_topic,
            "confidence": best_confidence,
            "probabilities": norm_probs
        }

    def predict_sentiment(self, text: str) -> dict:
        """Dự đoán cảm xúc kết hợp ML TF-IDF + SVM và Sentiment Guard."""
        cleaned = preprocess_vietnamese_text(text)
        lowered = text.lower()

        if self.sentiment_model:
            probas = self.sentiment_model.predict_proba([cleaned])[0]
            classes = list(self.sentiment_model.classes_)
            prob_dict = {str(c): float(p) for c, p in zip(classes, probas)}
        else:
            classes = ["negative", "neutral", "positive"]
            prob_dict = {c: 1.0 / len(classes) for c in classes}

        has_positive = any(kw in lowered for kw in POSITIVE_KEYWORDS)
        has_complaint = any(kw in lowered for kw in COMPLAINT_KEYWORDS)

        if has_positive and not has_complaint:
            prob_dict["positive"] = max(prob_dict.get("positive", 0), 0.85)
            prob_dict["negative"] = min(prob_dict.get("negative", 1), 0.10)

        has_inquiry = any(re.search(pat, lowered) for pat in INQUIRY_PATTERNS)
        if has_inquiry and not has_complaint and not has_positive:
            prob_dict["neutral"] = max(prob_dict.get("neutral", 0), 0.75)
            prob_dict["negative"] = min(prob_dict.get("negative", 1), 0.15)

        total = sum(prob_dict.values())
        norm_probs = {c: round(score / total, 4) for c, score in prob_dict.items()}

        best_sentiment = max(norm_probs, key=norm_probs.get)
        best_confidence = norm_probs[best_sentiment]

        return {
            "sentiment": best_sentiment,
            "confidence": best_confidence,
            "probabilities": norm_probs
        }

    def predict_all(self, text: str) -> dict:
        """Dự đoán tích hợp cả tác vụ Lĩnh vực & Cảm xúc."""
        topic_res = self.predict_topic(text)
        sentiment_res = self.predict_sentiment(text)
        return {
            "topic": topic_res["topic"],
            "topic_confidence": topic_res["confidence"],
            "topic_probabilities": topic_res["probabilities"],
            "sentiment": sentiment_res["sentiment"],
            "sentiment_confidence": sentiment_res["confidence"],
            "sentiment_probabilities": sentiment_res["probabilities"]
        }

_predictor_instance = FeedbackPredictor()

def get_predictor() -> FeedbackPredictor:
    return _predictor_instance
