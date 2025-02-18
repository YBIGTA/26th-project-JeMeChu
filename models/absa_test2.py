from transformers import BertTokenizer, BertForSequenceClassification
# from kobert_tokenizer import KoBERTTokenizer # pip install kobert-transformers
import torch
from torch.nn.functional import softmax
import pandas as pd
import os
from konlpy.tag import Okt  # 한국어 형태소 분석기
from collections import defaultdict
from Constants import DATABASE_PATH # Constants.py


device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("device:", device)

# 모델 로드
MODEL_NAME = "monologg/kobert"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME) # BERT
# tokenizer = KoBERTTokenizer.from_pretrained(MODEL_NAME) # KoBERT인데 오류가 너무 많이남.. 직접 설치 필요할 듯
print("KoBERT tokenizer loaded successfully!")
model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=3)
model.to(device)

# 한국어 형태소 분석기 (Aspect 추출) 
okt = Okt() # java install 필요함

# aspect 사전정의 -> constant화
COMMON_ASPECTS = ["음식", "서비스", "가격", "분위기", "청결", "조명", "직원", "커피", "와인"]  

def extract_aspects(text):
    """문장에서 키워드(Aspect) 추출"""
    nouns = okt.nouns(text)  # 명사 추출
    extracted_aspects = [word for word in nouns if word in COMMON_ASPECTS]
    return extracted_aspects if extracted_aspects else ["기타"]

def predict_sentiment(text):
    """BERT 감성 분석"""
    model.eval()
    encoding = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    encoding = {key: val.to(device) for key, val in encoding.items()}
    
    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
        probabilities = softmax(logits, dim=1)

    labels = ["Negative", "Neutral", "Positive"]
    sentiment_scores = probabilities[0].tolist()
    # print(predicted_label)

    predicted_label = labels[torch.argmax(probabilities)] # 최고 점수로 label 설정

    # # 임계값으로 label 설정 
    # if sentiment_scores[2] > 0.33:  # Positive (0.33 이상)
    #     predicted_label = "Positive"
    # elif sentiment_scores[0] > 0.33:  # Negative (0.33 이상)
    #     predicted_label = "Negative"
    # else:
    #     predicted_label = "Neutral"

    # if sentiment_scores

    return predicted_label, sentiment_scores

def split_sentences(review): # absa_result7.csv ver
    """리뷰를 문장 단위로 분리"""
    return review.replace("!", ".").replace("?", ".").split(". ")


# CSV 데이터 로드
CSV_PATH = os.path.join(DATABASE_PATH, "absa_test.csv")
OUTPUT_PATH = os.path.join(DATABASE_PATH, "absa_results7.csv")

df = pd.read_csv(CSV_PATH)
results = [] # 분석 결과 저장 리스트
store_sentiment_summary = defaultdict(lambda: {"Positive": 0, "Neutral": 0, "Negative": 0, "Total": 0}) # 매장별 감성 점수 저장용(ver4부터)


for _, row in df.iterrows():
    restaurant_name = row["사업장명"]
    review_text = row["리뷰"]

    aspects = extract_aspects(review_text)  # 키워드(Aspect) 추출
    aspect_sentiments = {}

    # 문장 단위로 분리 후 분석 ver7~
    sentences = split_sentences(review_text)

    for sentence in sentences:
        for aspect in aspects:
            sentiment, score = predict_sentiment(sentence)
            aspect_sentiments[aspect] = {"sentiment": sentiment, "score": score}

        # 매장별 감성 점수 누적
        store_sentiment_summary[restaurant_name][sentiment] += 1
        store_sentiment_summary[restaurant_name]["Total"] += 1

    results.append({
        "사업장명": restaurant_name,
        "리뷰": review_text,
        "Aspect_Sentiment": aspect_sentiments
    })

# 매장별 종합 감성 분석 결과 추가 -> ver4 부터 종합점수 추가
summary_results = []
for restaurant, sentiment_counts in store_sentiment_summary.items():
    total_sentences = sentiment_counts["Total"] # 문장 단위로 잘라서 문장이 몇 개인지를 카운트하개 됨 (ver7~)
    summary_results.append({
        "사업장명": restaurant,
        "리뷰": "매장 종합 감성 분석",
        "Aspect_Sentiment": {
            "Positive": f"{sentiment_counts['Positive']} ({sentiment_counts['Positive'] / total_sentences * 100:.2f}%)",
            "Neutral": f"{sentiment_counts['Neutral']} ({sentiment_counts['Neutral'] / total_sentences * 100:.2f}%)",
            "Negative": f"{sentiment_counts['Negative']} ({sentiment_counts['Negative'] / total_sentences * 100:.2f}%)",
            "Total_Sentences": total_sentences
        }
    })

# 데이터프레임 변환 후 저장
df_results = pd.DataFrame(results + [{}] + summary_results)
df_results.to_csv(OUTPUT_PATH, index=False)

print(f"ABSA 분석 완료! 결과 저장: {OUTPUT_PATH}")
