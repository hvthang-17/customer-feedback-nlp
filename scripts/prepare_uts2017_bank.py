"""
Script xử lý bộ dữ liệu UTS2017_Bank:
1. Nạp và khám phá phân bố 14 nhãn gốc và nhãn cảm xúc.
2. Ánh xạ 14 nhãn gốc sang 5 hàng đợi nghiệp vụ + 1 hàng đợi kiểm duyệt (theo PRD Section 10).
3. Thống kê độ mất cân bằng dữ liệu (Imbalanced Data) trước và sau ánh xạ.
4. Phân chia dữ liệu (Train 70%, Val 15%, Test 15%) sử dụng Stratified Splitting để duy trì tỷ lệ nhãn.
"""

import json
import os
from collections import Counter
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

LABEL_MAPPING = {
    "CUSTOMER_SUPPORT": "customer_service",
    "CARD": "card_account",
    "ACCOUNT": "card_account",
    "INTERNET_BANKING": "digital_banking",
    "SECURITY": "digital_banking",
    "LOAN": "credit_savings",
    "SAVING": "credit_savings",
    "INTEREST_RATE": "credit_savings",
    "MONEY_TRANSFER": "payment_transfer",
    "PAYMENT": "payment_transfer",
    "DISCOUNT": "payment_transfer",
    "TRADEMARK": "needs_review",
    "PROMOTION": "needs_review",
    "OTHER": "needs_review"
}

QUEUE_NAMES = {
    "customer_service": "Chăm sóc khách hàng",
    "card_account": "Thẻ & Tài khoản",
    "digital_banking": "Ngân hàng số",
    "credit_savings": "Tín dụng & Tiết kiệm",
    "payment_transfer": "Thanh toán & Chuyển tiền",
    "needs_review": "Cần kiểm duyệt"
}

def analyze_dataset(df: pd.DataFrame):
    """Phân tích thống kê dữ liệu gốc và dữ liệu sau ánh xạ."""
    print("=" * 60)
    print("1. THỐNG KÊ DỮ LIỆU GỐC UTS2017_BANK")
    print("=" * 60)
    print(f"Tổng số bản ghi: {len(df)}")
    
    if "label" in df.columns:
        print("\n--- Phân bố 14 nhãn gốc ---")
        label_counts = df["label"].value_counts()
        for label, count in label_counts.items():
            pct = (count / len(df)) * 100
            print(f"  • {label:<20}: {count:>5} mẫu ({pct:>5.2f}%)")
            
    if "sentiment" in df.columns:
        print("\n--- Phân bố cảm xúc (Sentiment) ---")
        sent_counts = df["sentiment"].value_counts()
        for sent, count in sent_counts.items():
            pct = (count / len(df)) * 100
            print(f"  • {sent:<20}: {count:>5} mẫu ({pct:>5.2f}%)")

def map_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Ánh xạ nhãn gốc sang hàng đợi định tuyến."""
    df = df.copy()
    if "label" in df.columns:
        df["target_queue"] = df["label"].map(LABEL_MAPPING).fillna("needs_review")
        df["queue_name"] = df["target_queue"].map(QUEUE_NAMES)
        
        print("\n" + "=" * 60)
        print("2. THỐNG KÊ PHÂN BỐ SAU KHI ÁNH XẠ SANG HÀNG ĐỢI")
        print("=" * 60)
        queue_counts = df["target_queue"].value_counts()
        for queue, count in queue_counts.items():
            q_name = QUEUE_NAMES.get(queue, queue)
            pct = (count / len(df)) * 100
            print(f"  • {queue:<20} ({q_name:<22}): {count:>5} mẫu ({pct:>5.2f}%)")
            
    return df

def split_dataset(df: pd.DataFrame, output_dir: Path):
    """
    Chia dataset thành Train (70%), Val (15%), Test (15%)
    Sử dụng Stratified Split để bảo toàn tỷ lệ nhãn ở cả 3 tập.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["target_queue"] if "target_queue" in df.columns else None
    )
    
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["target_queue"] if "target_queue" in temp_df.columns else None
    )
    
    print("\n" + "=" * 60)
    print("3. KẾT QUẢ PHÂN CHIA DỮ LIỆU (STRATIFIED SPLIT)")
    print("=" * 60)
    print(f"  • Tập Train (70%):      {len(train_df)} mẫu")
    print(f"  • Tập Validation (15%): {len(val_df)} mẫu")
    print(f"  • Tập Test (15%):       {len(test_df)} mẫu")
    
    train_df.to_csv(output_dir / "train.csv", index=False, encoding="utf-8-sig")
    val_df.to_csv(output_dir / "val.csv", index=False, encoding="utf-8-sig")
    test_df.to_csv(output_dir / "test.csv", index=False, encoding="utf-8-sig")
    
    print(f"\nĐã xuất các tệp dữ liệu vào thư mục: {output_dir}")

def download_uts2017_bank_from_huggingface(output_path: Path) -> pd.DataFrame:
    """Tải bộ dữ liệu UTS2017_Bank gốc từ Hugging Face (undertheseanlp/UTS2017_Bank)."""
    print("Đang tải bộ dữ liệu UTS2017_Bank từ Hugging Face Hub (undertheseanlp/UTS2017_Bank)...")
    
    url_cls_train = "https://huggingface.co/datasets/undertheseanlp/UTS2017_Bank/resolve/refs%2Fconvert%2Fparquet/classification/train/0000.parquet"
    url_cls_test = "https://huggingface.co/datasets/undertheseanlp/UTS2017_Bank/resolve/refs%2Fconvert%2Fparquet/classification/test/0000.parquet"
    url_snt_train = "https://huggingface.co/datasets/undertheseanlp/UTS2017_Bank/resolve/refs%2Fconvert%2Fparquet/sentiment/train/0000.parquet"
    url_snt_test = "https://huggingface.co/datasets/undertheseanlp/UTS2017_Bank/resolve/refs%2Fconvert%2Fparquet/sentiment/test/0000.parquet"
    
    try:
        df_cls_train = pd.read_parquet(url_cls_train)
        df_cls_test = pd.read_parquet(url_cls_test)
        df_cls = pd.concat([df_cls_train, df_cls_test], ignore_index=True)
        
        df_snt_train = pd.read_parquet(url_snt_train)
        df_snt_test = pd.read_parquet(url_snt_test)
        df_snt = pd.concat([df_snt_train, df_snt_test], ignore_index=True)
        
        df_merged = pd.merge(df_cls, df_snt, on="text", how="left")
        df_merged["source"] = "UTS2017_Bank"
        df_merged["received_at"] = "2017-12-31T00:00:00Z"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_merged.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"Tải thành công {len(df_merged)} mẫu từ Hugging Face và lưu vào: {output_path}")
        return df_merged
    except Exception as e:
        print(f"Không thể tải từ Hugging Face ({e}). Chuyển sang tạo dữ liệu mẫu...")
        return create_sample_uts2017_data(output_path)

def create_sample_uts2017_data(sample_path: Path):
    """Tạo bộ dữ liệu mẫu UTS2017_Bank chuẩn 14 nhãn nếu chưa có file thực tế."""
    sample_data = [
        {"text": "Ứng dụng ngân hàng hay bị văng khi đăng nhập vào buổi sáng", "label": "INTERNET_BANKING", "sentiment": "negative", "source": "mobile_app", "received_at": "2026-03-01T08:30:00Z"},
        {"text": "Thẻ ATM của tôi bị nuốt tại cây rút tiền đường Lê Lợi", "label": "CARD", "sentiment": "negative", "source": "call_center", "received_at": "2026-03-01T09:15:00Z"},
        {"text": "Tôi muốn kiểm tra lại số dư tài khoản tiết kiệm online", "label": "ACCOUNT", "sentiment": "neutral", "source": "web", "received_at": "2026-03-01T10:00:00Z"},
        {"text": "Lãi suất vay thế chấp bất động sản hiện tại là bao nhiêu?", "label": "LOAN", "sentiment": "neutral", "source": "chat", "received_at": "2026-03-01T10:30:00Z"},
        {"text": "Dịch vụ hỗ trợ của nhân viên phòng giao dịch rất tận tình và chu đáo", "label": "CUSTOMER_SUPPORT", "sentiment": "positive", "source": "survey", "received_at": "2026-03-01T11:00:00Z"},
        {"text": "Tôi chuyển khoản thành công nhưng bên nhận chưa thấy tiền", "label": "MONEY_TRANSFER", "sentiment": "negative", "source": "mobile_app", "received_at": "2026-03-01T11:45:00Z"},
        {"text": "Thanh toán hóa đơn điện nước bị lỗi hệ thống trừ tiền 2 lần", "label": "PAYMENT", "sentiment": "negative", "source": "mobile_app", "received_at": "2026-03-01T12:15:00Z"},
        {"text": "Cho tôi hỏi thủ tục mở sổ tiết kiệm kỳ hạn 12 tháng", "label": "SAVING", "sentiment": "neutral", "source": "web", "received_at": "2026-03-01T13:00:00Z"},
        {"text": "Tại sao mã OTP không gửi về điện thoại của tôi?", "label": "SECURITY", "sentiment": "negative", "source": "call_center", "received_at": "2026-03-01T13:30:00Z"},
        {"text": "Chương trình hoàn tiền 5% cho thẻ tín dụng áp dụng đến khi nào?", "label": "DISCOUNT", "sentiment": "neutral", "source": "chat", "received_at": "2026-03-01T14:00:00Z"},
        {"text": "Đổi quà khuyến mãi mua sắm cuối năm ở đâu?", "label": "PROMOTION", "sentiment": "neutral", "source": "facebook", "received_at": "2026-03-01T14:30:00Z"},
        {"text": "Logo và thương hiệu mới của ngân hàng trông rất hiện đại", "label": "TRADEMARK", "sentiment": "positive", "source": "facebook", "received_at": "2026-03-01T15:00:00Z"},
        {"text": "Thời tiết hôm nay đẹp quá", "label": "OTHER", "sentiment": "neutral", "source": "facebook", "received_at": "2026-03-01T15:30:00Z"},
        {"text": "Tư vấn cho tôi về mức lãi suất tiền gửi bậc thang", "label": "INTEREST_RATE", "sentiment": "neutral", "source": "web", "received_at": "2026-03-01T16:00:00Z"}
    ]
    df_sample = pd.DataFrame(sample_data * 20)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    df_sample.to_csv(sample_path, index=False, encoding="utf-8-sig")
    print(f"Đã tạo file dữ liệu mẫu UTS2017_Bank tại: {sample_path}")
    return df_sample

if __name__ == "__main__":
    import sys
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    raw_file = data_dir / "uts2017_bank_raw.csv"
    processed_dir = data_dir / "processed"

    force_download = "--download" in sys.argv

    if not raw_file.exists() or force_download:
        df_raw = download_uts2017_bank_from_huggingface(raw_file)
    else:
        df_raw = pd.read_csv(raw_file)

    analyze_dataset(df_raw)
    df_mapped = map_labels(df_raw)
    split_dataset(df_mapped, processed_dir)

