import html
import re
import unicodedata

try:
    from pyvi import ViTokenizer
    HAS_PYVI = True
except ImportError:
    HAS_PYVI = False

BANKING_STOPWORDS = {
    "dạ", "ơi", "à", "ừ", "nhé", "nha", "ạ", "thì", "mà", "là", "và", "hoặc",
    "cho", "với", "của", "tại", "theo", "bởi", "vì", "nên", "nếu", "nhưng",
    "này", "khi", "được", "bị", "bởi_vì", "do_đó", "thế_nên"
}

class VietnameseTextPreprocessor:
    """Pipeline tiền xử lý văn bản tiếng Việt cho bài toán phân loại và cảm xúc phản hồi ngân hàng."""

    def __init__(self, use_word_segmentation: bool = True, remove_stopwords: bool = True):
        self.use_word_segmentation = use_word_segmentation
        self.remove_stopwords = remove_stopwords

    def clean_html_and_urls(self, text: str) -> str:
        """Xóa HTML, URL, email và nhiễu văn bản."""
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"\S+@\S+", " ", text)
        text = re.sub(r"(?:^|\n)(?:--|On .+wrote:|Từ:).*", "", text, flags=re.DOTALL)
        return text

    def normalize_unicode(self, text: str) -> str:
        """Chuẩn hóa Unicode chuẩn NFC tiếng Việt."""
        return unicodedata.normalize("NFC", text)

    def clean_punctuation(self, text: str) -> str:
        """Giữ lại chữ cái, chữ số và khoảng trắng."""
        text = re.sub(r"[^\w\s_]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def segment_words(self, text: str) -> str:
        """Tách từ tiếng Việt bằng pyvi ViTokenizer."""
        if self.use_word_segmentation and HAS_PYVI:
            tokenized = ViTokenizer.tokenize(text)
            return re.sub(r"\s+", " ", tokenized).strip()
        return text

    def filter_stopwords(self, text: str) -> str:
        """Loại bỏ stopwords không mang ý nghĩa nghiệp vụ."""
        if not self.remove_stopwords:
            return text
        words = text.split()
        filtered = [w for w in words if w.lower() not in BANKING_STOPWORDS]
        return " ".join(filtered)

    def preprocess(self, text: str) -> str:
        """Luồng tiền xử lý hoàn chỉnh."""
        if not text:
            return ""
        text = self.clean_html_and_urls(text)
        text = self.normalize_unicode(text)
        text = text.lower()
        # Clean punctuation BEFORE segmenting words so pyvi tokens never stick together
        text = self.clean_punctuation(text)
        text = self.segment_words(text)
        text = self.filter_stopwords(text)
        return text

_default_preprocessor = VietnameseTextPreprocessor()

def preprocess_vietnamese_text(text: str) -> str:
    """Hàm wrapper cho luồng tiền xử lý chuẩn."""
    return _default_preprocessor.preprocess(text)
