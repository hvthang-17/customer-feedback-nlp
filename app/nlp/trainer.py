import json
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

from app.nlp.preprocessor import preprocess_vietnamese_text

ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"

def build_model_pipeline():
    """Tạo Pipeline TF-IDF + SVM Calibrated Classifier với cân bằng trọng số lớp."""
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        min_df=1,
        sublinear_tf=True
    )
    base_svc = LinearSVC(C=1.0, class_weight="balanced", random_state=42, max_iter=3000)
    calibrated_svc = CalibratedClassifierCV(estimator=base_svc, cv=5)
    
    return Pipeline([
        ("tfidf", tfidf),
        ("clf", calibrated_svc)
    ])

def train_and_evaluate_task(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    text_col: str,
    target_col: str,
    task_name: str
) -> tuple[Pipeline, dict]:
    """Huấn luyện và đánh giá mô hình cho 1 tác vụ cụ thể."""
    print("\n" + "=" * 60)
    print(f"HUẤN LUYỆN VÀ ĐÁNH GIÁ TÁC VỤ: {task_name.upper()}")
    print("=" * 60)

    # Preprocess text
    X_train = [preprocess_vietnamese_text(t) for t in train_df[text_col]]
    y_train = train_df[target_col].values
    
    X_test = [preprocess_vietnamese_text(t) for t in test_df[text_col]]
    y_test = test_df[target_col].values

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)
    max_confidences = np.max(y_proba, axis=1)

    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    
    classes = pipeline.classes_.tolist()
    cm = confusion_matrix(y_test, y_pred, labels=pipeline.classes_).tolist()
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "task_name": task_name,
        "accuracy": round(float(acc), 4),
        "precision_macro": round(float(prec), 4),
        "recall_macro": round(float(rec), 4),
        "f1_macro": round(float(f1), 4),
        "mean_confidence": round(float(np.mean(max_confidences)), 4),
        "classes": classes,
        "confusion_matrix": cm,
        "report": report
    }

    print(f"Accuracy:        {acc:.4f}")
    print(f"Precision (Macro): {prec:.4f}")
    print(f"Recall (Macro):    {rec:.4f}")
    print(f"F1-Macro:         {f1:.4f}  (Mục tiêu PRD >= 0.80)")
    print("\n--- Chi tiết Classification Report ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    return pipeline, metrics

def run_training_pipeline(
    raw_data_path: Path = DATA_DIR / "uts2017_bank_raw.csv",
    output_dir: Path = MODELS_DIR
) -> dict:
    """Thực hiện huấn luyện cả 2 tác vụ: Phân loại lĩnh vực & Phân tích cảm xúc."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_dir = DATA_DIR / "processed"
    if (processed_dir / "train.csv").exists() and (processed_dir / "test.csv").exists():
        train_df = pd.read_csv(processed_dir / "train.csv")
        test_df = pd.read_csv(processed_dir / "test.csv")
    else:
        print("Chưa có file train/test trong data/processed. Đang đọc trực tiếp dữ liệu thô...")
        from scripts.prepare_uts2017_bank import map_labels, split_dataset, download_uts2017_bank_from_huggingface
        if not raw_data_path.exists():
            df_raw = download_uts2017_bank_from_huggingface(raw_data_path)
        else:
            df_raw = pd.read_csv(raw_data_path)
        df_mapped = map_labels(df_raw)
        split_dataset(df_mapped, processed_dir)
        train_df = pd.read_csv(processed_dir / "train.csv")
        test_df = pd.read_csv(processed_dir / "test.csv")

    # Task 1: Phân loại Lĩnh vực (Topic Classification -> target_queue)
    topic_pipeline, topic_metrics = train_and_evaluate_task(
        train_df=train_df,
        test_df=test_df,
        text_col="text",
        target_col="target_queue",
        task_name="topic_classification"
    )
    joblib.dump(topic_pipeline, output_dir / "topic_model.joblib")

    # Task 2: Phân tích Cảm xúc (Sentiment Analysis -> sentiment)
    sentiment_pipeline, sentiment_metrics = train_and_evaluate_task(
        train_df=train_df,
        test_df=test_df,
        text_col="text",
        target_col="sentiment",
        task_name="sentiment_analysis"
    )
    joblib.dump(sentiment_pipeline, output_dir / "sentiment_model.joblib")

    all_metrics = {
        "topic_classification": topic_metrics,
        "sentiment_analysis": sentiment_metrics
    }
    
    with open(output_dir / "evaluation_metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)
        
    print("\nĐã lưu thành công mô hình và báo cáo vào:", output_dir)
    return all_metrics

if __name__ == "__main__":
    run_training_pipeline()
