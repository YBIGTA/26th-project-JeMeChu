import os
import pandas as pd
from gensim.models import Word2Vec # pip install genism


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "database"))

csv_PATH = os.path.abspath(os.path.join(DATABASE_PATH, "processed_features.csv")) # str임

# 파일 로드
df = pd.read_csv(csv_PATH)



# database 디렉토리의 절대 경로 설정

# 원하는 저장 파일명 지정 (예: "my_custom_output.csv")
csv_filename = "my_custom_output.csv"  # 원하는 파일명으로 변경 가능

# 최종 저장 경로 생성

# 데이터 저장
df.to_csv(csv_PATH, index=False, encoding="utf-8-sig")

print(f"파일이 저장 완료: {csv_PATH}")


# 리뷰를 단어 리스트로 변환
tokenized_reviews = df["최신 300개 리뷰"].apply(lambda x: str(x).split())

# Word2Vec 모델 학습
w2v_model = Word2Vec(sentences=tokenized_reviews, vector_size=100, window=5, min_count=3, workers=4)

def find_similar_restaurants(restaurant_name):
    if restaurant_name in w2v_model.wv:
        similar = w2v_model.wv.most_similar(restaurant_name, topn=5)
        return [x[0] for x in similar]
    return []

df["유사 공간 특징 맛집"] = df["사업장명"].apply(find_similar_restaurants)

save_PATH = os.path.join(DATABASE_PATH, "final_recommendations.csv")
df.to_csv(save_PATH, index=False, encoding="utf-8-sig")

print("Word2Vec 추천 시스템 적용 완료")

# python review_analysis/preprocessing/word2vec_recommend.py

