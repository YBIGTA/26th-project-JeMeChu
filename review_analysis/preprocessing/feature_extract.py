import pandas as pd
import os
import ast
from sklearn.feature_extraction.text import TfidfVectorizer

### CSV 파일 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "database"))

csv_PATH = os.path.abspath(os.path.join(DATABASE_PATH, "preprocessed_naver.csv")) # str임
# 파일 로드
df = pd.read_csv(csv_PATH)



### 1) '편의시설 및 서비스'에서 공간적 특징 추출
def extract_features(service_info):
    if pd.isna(service_info) or service_info == "정보 없음":
        return []

    try:
        facilities = ast.literal_eval(service_info)
    except:
        facilities = []

    extracted_features = []
    if "단체 이용 가능" in facilities:
        extracted_features.append("단체 이용 가능")
    if "룸" in facilities or "프라이빗" in facilities:
        extracted_features.append("룸 있음")
    if "넓은 매장" in facilities or "좌석이 많음" in facilities:
        extracted_features.append("넓은 매장")

    return extracted_features

df["공간적 특징"] = df["편의시설 및 서비스"].apply(extract_features)

### 2) '주차 정보' 전처리
def classify_parking(info):
    if pd.isna(info) or "정보 없음" in str(info):
        return "주차 정보 없음"
    elif "불가" in info:
        return "주차 불가"
    elif "유료" in info:
        return "유료 주차 가능"
    elif "무료" in info:
        return "무료 주차 가능"
    elif "주차가능" in info:
        return "주차 가능"
    return "주차 정보 없음"

df["주차 여부"] = df["주차 정보"].apply(classify_parking)

### 3) TF-IDF를 활용한 공간 관련 키워드 분석
space_keywords = ["룸", "프라이빗", "좌석", "넓다", "공간", "단체", "조용", "아늑", "편안"]

vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["최신 300개 리뷰"].fillna(""))
feature_names = vectorizer.get_feature_names_out()

def check_space_keywords(text):
    text = str(text)
    detected = [word for word in space_keywords if word in text]
    return detected

df["공간 키워드"] = df["최신 300개 리뷰"].apply(check_space_keywords)

save_PATH = os.path.join(DATABASE_PATH, "processed_features.csv")
df.to_csv(save_PATH, index=False, encoding="utf-8-sig")

print("공간적 특징 및 키워드 분석 완료!")
# python review_analysis/preprocessing/feature_extract.py


