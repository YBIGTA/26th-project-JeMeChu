import pandas as pd
import ast  # 문자열로 저장된 리스트를 변환하기 위해 사용
import os
from Constants import DATABASE_PATH

# CSV 데이터 경로
CSV_PATH = os.path.join(DATABASE_PATH, "preprocessed_naver.csv")
OUTPUT_PATH = os.path.join(DATABASE_PATH, "restaurant_features.csv")

# 데이터 로드
df = pd.read_csv(CSV_PATH)

# 주요 키워드 및 리뷰 개수 처리
def extract_keywords(keyword_data):
    """키워드와 개수를 추출하여 정리"""
    if isinstance(keyword_data, str):
        try:
            keyword_list = ast.literal_eval(keyword_data)  # 문자열을 리스트로 변환
            keyword_summary = {k[0]: k[1] for k in keyword_list if isinstance(k, list) and len(k) == 2}
            return keyword_summary
        except Exception as e:
            print(f"키워드 변환시 오류 발생: {e}")
            return {}
    return {}

# 이용 가능 시설 처리
def process_facilities(facility_data):
    """이용 가능한 시설을 리스트로 변환"""
    if isinstance(facility_data, str):
        try:
            return ast.literal_eval(facility_data)
        except:
            return []
    return [] # str이 아닌 경우 빈 리스트 반환

# 주차 정보 처리
def process_parking(parking_data):
    """주차 가능 여부 추출"""
    if isinstance(parking_data, str):
        return "무료" in parking_data.lower()
    return False

# df에 새로운 컬럼 추가
df["Keyword_Review_Summary"] = df["이런점이 좋았어요"].apply(extract_keywords)
df["Facility_Available"] = df["편의시설 및 서비스"].apply(process_facilities)
df["Parking_Available"] = df["주차 정보"].apply(process_parking)

# 정리된 데이터 저장
df[["사업장명", "Keyword_Review_Summary", "Facility_Available", "Parking_Available"]].to_csv(OUTPUT_PATH, index=False)

print(f"리뷰 키워드 및 이용 정보 정리 완료! 결과 저장: {OUTPUT_PATH}")
