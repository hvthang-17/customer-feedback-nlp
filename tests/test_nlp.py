import unittest
import os
from pathlib import Path
from app.nlp.preprocessor import preprocess_vietnamese_text, VietnameseTextPreprocessor
from app.nlp.predictor import FeedbackPredictor

class NLPModuleTests(unittest.TestCase):
    def test_preprocessor_pipeline(self):
        raw = "<p>Dạ cho hỏi <b>lãi suất</b> gửi tiết kiệm ngân hàng là bao nhiêu vậy ạ?</p>"
        processed = preprocess_vietnamese_text(raw)
        self.assertNotIn("<p>", processed)
        self.assertNotIn("dạ", processed.split())
        self.assertIn("lãi_suất", processed)

    def test_predictor_model_inference(self):
        predictor = FeedbackPredictor()
        if predictor.is_ready():
            res_topic = predictor.predict_topic("Ứng dụng bị lỗi không thể đăng nhập")
            self.assertIn("topic", res_topic)
            self.assertIn("confidence", res_topic)
            self.assertGreaterEqual(res_topic["confidence"], 0.0)
            self.assertLessEqual(res_topic["confidence"], 1.0)

            res_sent = predictor.predict_sentiment("Dịch vụ tuyệt vời, nhân viên hỗ trợ nhiệt tình")
            self.assertIn("sentiment", res_sent)
            self.assertIn(res_sent["sentiment"], ["positive", "negative", "neutral"])

if __name__ == "__main__":
    unittest.main()