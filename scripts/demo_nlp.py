"""
Script demo kiểm tra trực tiếp khả năng phân loại lĩnh vực & cảm xúc của mô hình NLP.
Chạy: .\.venv\Scripts\python.exe scripts/demo_nlp.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.nlp.predictor import get_predictor
from app.nlp.preprocessor import preprocess_vietnamese_text

def run_demo():
    predictor = get_predictor()
    if not predictor.is_ready():
        print("Chưa tìm thấy file mô hình trong thư mục models/. Vui lòng chạy scripts/train_models.py trước!")
        return

    sample_feedbacks = [
    "Tôi không thể đăng nhập vào ứng dụng ngân hàng dù đã nhập đúng mật khẩu, hệ thống cứ báo thông tin không hợp lệ.",

    "Tôi vừa thực hiện chuyển khoản nhưng giao dịch vẫn đang ở trạng thái chờ xử lý, mong ngân hàng kiểm tra giúp.",

    "Nhân viên tổng đài hỗ trợ rất nhanh chóng và giải thích vấn đề của tôi một cách rõ ràng.",

    "Tôi muốn biết điều kiện để đăng ký khoản vay tiêu dùng và mức lãi suất hiện đang áp dụng.",

    "Tôi vừa nhận được thông báo giao dịch bằng thẻ mà tôi không thực hiện, ngân hàng có thể kiểm tra giúp tôi không?",

    "Tại sao tài khoản của tôi lại bị trừ phí khi thực hiện giao dịch chuyển tiền?",

    "Tôi muốn đăng ký mở tài khoản tiết kiệm trực tuyến, cần chuẩn bị những thông tin gì?",

    "Ứng dụng ngân hàng có giao diện dễ sử dụng nhưng thời gian tải thông tin số dư đôi lúc khá lâu.",

    "Tôi rất hài lòng với chương trình ưu đãi dành cho khách hàng sử dụng thẻ tín dụng.",

    "Mã OTP xác thực giao dịch không được gửi về điện thoại của tôi, tôi phải làm thế nào?",

    "Tôi muốn thay đổi hạn mức thanh toán trực tuyến của thẻ thì cần thực hiện ở đâu?",

    "Tôi đã thanh toán hóa đơn thành công nhưng hệ thống vẫn hiển thị trạng thái chưa thanh toán.",

    "Cho tôi hỏi lãi suất tiền gửi kỳ hạn 12 tháng hiện nay được tính như thế nào?",

    "Tôi đã liên hệ với bộ phận hỗ trợ nhưng phải chờ khá lâu mới được phản hồi, trải nghiệm này chưa tốt.",

    "Tôi muốn biết ngân hàng có hỗ trợ chuyển tiền quốc tế qua ứng dụng hay không?"
]

    print("=" * 75)
    print("DEMO DỰ ĐOÁN PHÂN LOẠI LĨNH VỰC & CẢM XÚC PHẢN HỒI KHÁCH HÀNG NGÂN HÀNG")
    print("=" * 75)

    for idx, text in enumerate(sample_feedbacks, 1):
        clean_text = preprocess_vietnamese_text(text)
        res = predictor.predict_all(text)
        
        print(f"\n📝 [Phản hồi #{idx}]: {text}")
        print(f"[Sau tiền xử lý]: {clean_text}")
        print(f"[Lĩnh vực dự đoán]: {res['topic']} (Tin cậy: {res['topic_confidence']:.2%})")
        print(f"[Cảm xúc dự đoán]: {res['sentiment']} (Tin cậy: {res['sentiment_confidence']:.2%})")
        print("-" * 75)

if __name__ == "__main__":
    run_demo()
