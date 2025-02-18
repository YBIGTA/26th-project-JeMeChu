from transformers import BertTokenizer, BertForSequenceClassification
import torch
from torch.nn.functional import softmax
import pandas as pd
import os
from Constants import DATABASE_PATH

# mac(M1/M2) GPU임 -> 자기 개발환경 확인하고 쓰기
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# ABSA 모델 로드 (KoBERT 사용)
MODEL_NAME = "monologg/kobert"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=3)  # Negative, Neutral, Positive
model.to(device)

# 감성 분석 함수
def predict_sentiment(text):
    """BERT 기반 감성 분석"""
    model.eval()
    encoding = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    
    # MPS 디바이스로 이동
    encoding = {key: val.to(device) for key, val in encoding.items()}
    
    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
        probabilities = softmax(logits, dim=1)

    labels = ["Negative", "Neutral", "Positive"]
    predicted_label = labels[torch.argmax(probabilities)]
    sentiment_score = probabilities[0].tolist()

    return predicted_label, sentiment_score

# 데이터 로드 및 처리
CSV_PATH = os.path.join(DATABASE_PATH, "absa_test.csv")  # 테스트용 CSV 파일
OUTPUT_PATH = os.path.join(DATABASE_PATH, "absa_results1.csv")

df = pd.read_csv(CSV_PATH)

# 감성 분석 실행 및 결과 저장
results = []

for _, row in df.iterrows():
    restaurant_name = row["사업장명"]
    review_text = row["리뷰"]

    # 감성 분석 수행
    sentiment, score = predict_sentiment(review_text)

    # 결과 저장
    results.append({
        "사업장명": restaurant_name,
        "리뷰": review_text,
        "감성": sentiment,
        "점수": score
    })

# 결과를 DataFrame으로 변환 및 CSV 저장
result_df = pd.DataFrame(results)
result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print(f"ABSA 감성 분석 완료! 결과 저장: {OUTPUT_PATH}")
