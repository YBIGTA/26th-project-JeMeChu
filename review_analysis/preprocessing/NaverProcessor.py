import pandas as pd
import os
import json
import re
import ast
from datetime import datetime
from scipy.stats import zscore
from sklearn.feature_extraction.text import TfidfVectorizer
from review_analysis.preprocessing.base_processor import BaseDataProcessor
from bs4 import BeautifulSoup
from pykospacing import Spacing # pip install git+https://github.com/haven-jeon/PyKoSpacing.git
from soynlp.normalizer import repeat_normalize # pip install soynlp
from PyKomoran import Komoran, DEFAULT_MODEL # pip install PyKomoran

class NaverProcessor(BaseDataProcessor):

    STOPWORDS = {}

    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = pd.read_csv(input_path, na_values=["N/A"])
        self.pykomoran = Komoran(DEFAULT_MODEL['LIGHT'])
        self.punct = "/-'?!.,#$%\'()*+-/:;<=>@[\\]^_`{|}~" + '""“”’' + '∞θ÷α•à−β∅³π‘₹´°£€\×™√²—–&'
        self.punct_mapping = {"‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", "√": " sqrt ", "×": "x", "²": "2", "—": "-", "–": "-", "’": "'", "_": "-", "`": "'", '“': '"', '”': '"', '“': '"', "£": "e", '∞': 'infinity', 'θ': 'theta', '÷': '/', 'α': 'alpha', '•': '.', 'à': 'a', '−': '-', 'β': 'beta', '∅': '', '³': '3', 'π': 'pi', } 

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
        self.df_cleaned['좌표정보(X)'] = pd.to_numeric(self.df_cleaned['좌표정보(X)'], errors='coerce')
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

        # 주차 정보 전처리리
        self.df_cleaned['주차 정보'] = self.df_cleaned['주차 정보'].astype(str).apply(self.classify_parking)

        # 정상적으로 크롤링 됐는지 확인하는 열 삭제
        self.df_cleaned = self.df_cleaned.drop(columns=['Processed'], errors = 'ignore')

        # 소개에서 '정보없음' 결측치 처리
        self.df_cleaned['소개'] = self.df_cleaned['소개'].replace("정보 없음", pd.NA)

        # 편의시설 및 서비스 결측치 처리
        self.df_cleaned['편의시설 및 서비스'] = self.df_cleaned['편의시설 및 서비스'].apply(lambda x: pd.NA if isinstance(x, list) and len(x) == 0 else x)

        # 이런점이 좋았어요 결측치 처리
        self.df_cleaned['이런점이 좋았어요'] = self.df_cleaned['이런점이 좋았어요'].apply(lambda x: pd.NA if isinstance(x, list) and len(x) == 0 else x)

        # 좌석 정보 결측치 처리
        self.df_cleaned['좌석 정보'] = self.df_cleaned['좌석 정보'].apply(lambda x: pd.NA if isinstance(x, list) and len(x) == 0 else x)

# 결과 출력
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

    @staticmethod
    def clean(text, punct, mapping):
        for p in mapping:
            text = text.replace(p, mapping[p])
        
        for p in punct:
            text = text.replace(p, f' {p} ')
        
        specials = {'\u200b': ' ', '…': ' ... ', '\ufeff': '', 'करना': '', 'है': ''}
        for s in specials:
            text = text.replace(s, specials[s])
        
        return text.strip()

    @staticmethod
    def clean_str(text):
        pattern = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'  # E-mail 제거
        text = re.sub(pattern=pattern, repl='', string=text)
        pattern = r'(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        text = re.sub(pattern=pattern, repl='', string=text)
        pattern = r'([ㄱ-ㅎㅏ-ㅣ]+)'  # 한글 자음, 모음 제거
        text = re.sub(pattern=pattern, repl='', string=text)
        pattern = r'<[^>]*>'  # HTML 태그 제거
        text = re.sub(pattern=pattern, repl='', string=text)
        pattern = r'[^\w\s\n]'  # 특수기호 제거
        text = re.sub(pattern=pattern, repl='', string=text)
        text = re.sub(r'[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', string=text)
        text = re.sub(r'\n', '.', string=text)
        text = re.sub(r'[^가-힣\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text 

    def lemmatize(self, sentence):
        """
        KOMORAN을 활용한 표제어 추출  
        고유명사(NNP, NNG)는 그대로, 동사/형용사(VA, VV)는 어간에 '다'를 붙여 표제어화한다.
        """
        pos_list = self.pykomoran.pos(sentence)
        words = []
        for morph, tag in pos_list:
            if tag in ['NNP', 'NNG']:
                words.append(morph)
            elif tag in ['VA', 'VV']:
                words.append(morph + '다')
        return words
    
    
    def clean_review_texts(self, raw_text):
        try:
            # 먼저 json.loads 시도, 실패 시 ast.literal_eval 사용
            try:
                reviews = json.loads(raw_text)
            except Exception:
                reviews = ast.literal_eval(raw_text)

            processed_reviews = []

            for review in reviews:
                text = review.get('text', '')

                # 1. 띄어쓰기 교정
                text = Spacing(text)

                # 2. 정규표현식 기반 클렌징
                text = self.clean_str(text)
                text = self.clean(text, self.punct, self.punct_mapping)
                text = BeautifulSoup(text, 'html.parser').get_text()
                text = re.sub(r'\s+', ' ', text).strip()

                # 3. 소문자화 및 반복문자 정규화
                text = repeat_normalize(text, num_repeats=2)

                # 4. POS 태깅 및 표제어 추출 (KOMORAN 활용)
                pos_tokens = self.lemmatize(text)

                # 5. 불용어 제거
                pos_tokens = [token for token in pos_tokens if token not in self.STOPWORDS]
                pos_text = " ".join(pos_tokens)

                # pos_text가 비어있으면 해당 리뷰는 제외
                if pos_text.strip() == "":
                    continue

                processed_reviews.append({"cleaned": text, "pos": pos_text})

            # 리뷰들이 있으면, 각 리뷰의 cleaned 텍스트를 하나의 문자열로 합침
            if processed_reviews:
                return " ".join([r["cleaned"] for r in processed_reviews])
            else:
                return ""
        except Exception as e:
            print("전처리 오류 발생:", e)
            return ""


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
