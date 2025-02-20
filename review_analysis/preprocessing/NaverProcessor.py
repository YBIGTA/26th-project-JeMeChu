import pandas as pd
import os
import json
import re
from datetime import datetime
from scipy.stats import zscore
from review_analysis.preprocessing.base_processor import BaseDataProcessor
from bs4 import BeautifulSoup
from soynlp.normalizer import repeat_normalize # pip install soynlp

class NaverProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = pd.read_csv(input_path, na_values=["N/A"])
        self.STOPWORDS = {}

    def preprocess(self):
        """
        1. 결측값 제거
        2. 이상치 제거
        3. 날짜 변환 및 정리
        4. 리뷰 텍스트 전처리
        """
        # 컬럼명 변경
        self.df.rename(columns={
            '사업장명': 'name',
            '지번주소': 'jibun_address',
            '도로명주소': 'road_address',
            '업태구분명': 'category',
            '전화번호': 'phone',
            '운영시간': 'business_hours',
            '총 리뷰 개수': 'review_count',
            '소개': 'description',
            '편의시설 및 서비스': 'facilities',
            '주차 정보': 'parking',
            '좌석 정보': 'seat_info',
            '최신 300개 리뷰': 'latest_reviews',
            '소재지면적': 'size',
            '이런점이 좋았어요': 'very_good',
            '좌표정보(X)': 'latitude',
            '좌표정보(Y)': 'longitude'
        }, inplace=True)

        # 결측값 제거
        self.df_cleaned = self.df.dropna()

        # 좌표 정보 type변환 (str -> float)
        self.df_cleaned['latitude'] = pd.to_numeric(self.df_cleaned['latitude'], errors='coerce')
        # errors='coerce': 변환 불가능한 건 NaN으로, 가능한 건 수치로 처리함.. 

        # 좌표 정보 이상치 제거
        self.df_cleaned = self.df_cleaned[(self.df_cleaned['latitude'] > 100000) & 
                                          (self.df_cleaned['longitude'] > 100000)]

        # 리뷰 개수가 30개 이하거나 비정상적으로 큰 값 제거
        self.df_cleaned = self.df_cleaned[(self.df_cleaned['review_count'] >= 30) & 
                                          (self.df_cleaned['review_count'] <= 5000)]

        # 전화번호 형식 정리 (050, 02로 시작하는 번호만 유지)
        self.df_cleaned['phone'] = self.df_cleaned['phone'].apply(lambda x: x if str(x).startswith("050") or str(x).startswith("02") else None)

        # 운영시간 JSON 파싱 및 정리
        self.df_cleaned['business_hours'] = self.df_cleaned['business_hours'].apply(self.parse_operating_hours)

        # 최신 300개 리뷰 텍스트 정리 (JSON 형식 → 리스트 변환 후 텍스트 정리)
        self.df_cleaned['latest_reviews'] = self.df_cleaned['latest_reviews'].apply(self.clean_review_texts)

        # 주차 정보 전처리
        self.df_cleaned['parking'] = self.df_cleaned['parking'].astype(str).apply(self.classify_parking)

        # 정상적으로 크롤링 됐는지 확인하는 열 삭제
        self.df_cleaned = self.df_cleaned.drop(columns=['Processed'], errors = 'ignore')

        # 소개에서 '정보없음' 결측치 처리
        self.df_cleaned['description'] = self.df_cleaned['description'].replace("정보 없음", pd.NA)

        # 편의시설 및 서비스 결측치 처리
        self.df_cleaned['facilities'] = self.df_cleaned['facilities'].apply(lambda x: pd.NA if isinstance(x, list) and len(x) == 0 else x)

        # 이런점이 좋았어요 결측치 처리
        self.df_cleaned['very_good'] = self.df_cleaned['very_good'].apply(lambda x: pd.NA if isinstance(x, list) and len(x) == 0 else x)

        # 좌석 정보 결측치 처리
        self.df_cleaned['seat_info'] = self.df_cleaned['seat_info'].apply(lambda x: pd.NA if isinstance(x, list) and len(x) == 0 else x)

    def feature_engineering(self):
        """
        기존 TF-IDF 벡터화 삭제.
        대신 OpenAI 임베딩을 적용하기 위해 리뷰 텍스트만 정리.
        """
        # 필요 없는 컬럼 제거
        if 'tfidf_features' in self.df_cleaned.columns:
            self.df_cleaned.drop(columns=['tfidf_features'], inplace=True, errors='ignore')

    def save_to_database(self):
        """
        처리된 데이터를 CSV로 저장
        """
        file_name = "preprocessed_naver.csv"
        file_path = os.path.join(self.output_dir, file_name)
        if isinstance(self.df_cleaned, pd.DataFrame):
            self.df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")

    ### 보조 함수 (JSON 처리 및 텍스트 전처리)
    def parse_operating_hours(self, raw_hours):
        """
        '운영시간' 필드에서 JSON 문자열을 파싱하고 정리
        """
        try:
            hours_dict = eval(raw_hours)  # JSON 변환
            formatted_hours = [f"{day}: {time}" for day, time in hours_dict.items()]
            return "; ".join(formatted_hours)
        except:
            return None

    def clean_review_texts(self, raw_text):
        """
        최신 300개 리뷰 데이터를 정리 (JSON 문자열 → 텍스트)
        """
        stopwords = {}

        try:
            reviews = eval(raw_text)  # JSON 문자열을 파이썬 객체로 변환
            cleaned_reviews = []

            for review in reviews:
                # 1. 텍스트 추출
                text = review['text']
                # 2. 한글(가-힣)과 공백만 남기고 모두 제거
                text = re.sub(r'[^가-힣\s]', '', text)
                # 3. 토큰(단어) 분리
                tokens = text.split()
                # 4. 불용어 제거
                tokens = [token for token in tokens if token not in stopwords]
                # 5. 정제 후 한 문장으로 합치거나(token 단위 유지도 가능) 리스트에 저장
                cleaned_text = " ".join(tokens)
                cleaned_reviews.append(cleaned_text)

            return cleaned_reviews
        
        except:
            return None
        
    def classify_parking(self, info):
        """주차 정보 정리 (유료 주차 가능, 무료 주차 가능, 주차 가능, 주차 불가)"""
        if pd.isna(info) or "정보 없음" in str(info):
            return None
        elif "불가" in info:
            return "주차 불가"
        elif "유료" in info:
            return "유료 주차 가능"
        elif "무료" in info:
            return "무료 주차 가능"
        elif "주차가능" in info:
            return "주차 가능"
        return None
    
### DataFrameProcessor (DataFrame 기반) -> 나중에 db 연결 시 필요
# class DataFrameProcessor(NaverProcessor) :
#     def __init__(self, df: pd.DataFrame):
#         self.df = df
#         self.df_cleaned = pd.DataFrame()

#     def get_cleaned_dataframe(self):
#         """
#         최종 전처리된 데이터프레임 반환
#         """
#         return self.df_cleaned
