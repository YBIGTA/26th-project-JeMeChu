import pandas as pd
import os
import json
import re
from datetime import datetime
from scipy.stats import zscore
from sklearn.feature_extraction.text import TfidfVectorizer
from review_analysis.preprocessing.base_processor import BaseDataProcessor

class NaverProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = pd.read_csv(input_path, na_values=["N/A"])

    def preprocess(self):
        """
        1. 결측값 제거
        2. 이상치 제거
        3. 날짜 변환 및 정리
        4. 리뷰 텍스트 전처리
        """
        # 결측값 제거
        self.df_cleaned = self.df.dropna()

        # 좌표 정보 type변환 (str -> float)
        self.dr_cleaned['좌표정보(X)'] = pd.to_numeric(self.df_cleaned['좌표정보(X)'], errors='coerce')
        # errors='coerce': 변환 불가능한 건 NaN으로, 가능한 건 수치로 처리함.. 

        # 좌표 정보 이상치 제거
        self.df_cleaned = self.df_cleaned[(self.df_cleaned['좌표정보(X)'] > 100000) & 
                                          (self.df_cleaned['좌표정보(Y)'] > 100000)]

        # 리뷰 개수가 30개 이하거나 비정상적으로 큰 값 제거
        self.df_cleaned = self.df_cleaned[(self.df_cleaned['총 리뷰 개수'] >= 30) & 
                                          (self.df_cleaned['총 리뷰 개수'] <= 5000)]

        # 전화번호 형식 정리 (050, 02로 시작하는 번호만 유지)
        self.df_cleaned['전화번호'] = self.df_cleaned['전화번호'].apply(lambda x: x if str(x).startswith("050") or str(x).startswith("02") else None)

        # 운영시간 JSON 파싱 및 정리
        self.df_cleaned['운영시간'] = self.df_cleaned['운영시간'].apply(self.parse_operating_hours)

        # 최신 300개 리뷰 텍스트 정리 (JSON 형식 → 리스트 변환 후 텍스트 정리)
        self.df_cleaned['최신 300개 리뷰'] = self.df_cleaned['최신 300개 리뷰'].apply(self.clean_review_texts)

    def feature_engineering(self):
        """
        1. 텍스트 데이터에서 유의미한 특징 추출
        2. TF-IDF 벡터화
        3. 주차 정보, 편의시설 등 정리
        """
        # TF-IDF 벡터화 수행 (리뷰 기반)
        vectorizer = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.df_cleaned['최신 300개 리뷰'])
        tfidf_feature_names = vectorizer.get_feature_names_out()

        # TF-IDF 벡터를 문자열 형태로 저장
        self.df_cleaned['tfidf_features'] = [
            ', '.join(f"{word}:{tfidf:.2f}" for word, tfidf in zip(tfidf_feature_names, row) if tfidf > 0)
            for row in tfidf_matrix.toarray()
        ]
        
        # 불필요한 데이터 삭제
        self.df_cleaned = self.df_cleaned[self.df_cleaned['tfidf_features'] != '']

    def save_to_database(self):
        """
        처리된 데이터를 CSV로 저장
        """
        file_name = "preprocessed_navertemp.csv"
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
        try:
            reviews = eval(raw_text)  # JSON 변환
            cleaned_reviews = [re.sub(r'[^\w\s]', '', review['text']) for review in reviews]
            return " ".join(cleaned_reviews)
        except:
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
