"""
"restaurant.csv" 파일을 CP949 인코딩으로 읽어 UTF-8로 변환한 후,
선택한 데이터(서교동, 합정에 위치하며 '영업' 중인 식당)에서 불필요한 업체를 제거하고,
사업장명에서 괄호 내 텍스트를 삭제하는 전처리를 수행하여
최종 결과를 "restaurant_df.csv" 파일로 저장합니다.
"""

import pandas as pd
import re
from typing import List
import os


def convert_file_encoding(input_file: str, output_file: str,
                          input_encoding: str = "CP949",
                          output_encoding: str = "UTF-8") -> None:
    """
    파일의 인코딩을 변환합니다.
    
    Args:
        input_file: 원본 파일 경로.
        output_file: 변환 후 저장할 파일 경로.
        input_encoding: 원본 파일의 인코딩.
        output_encoding: 저장할 파일의 인코딩.
    """
    with open(input_file, "r", encoding=input_encoding, errors="replace") as f:
        data = f.read()
    
    with open(output_file, "w", encoding=output_encoding) as f:
        f.write(data)
    print(f"'{input_file}'의 인코딩을 {output_encoding}로 변환하여 '{output_file}'에 저장하였습니다.")


def filter_restaurant_data(input_csv: str, output_csv: str) -> None:
    """
    CSV 파일을 로드한 후 데이터를 필터링 및 전처리하여 최종 CSV 파일로 저장합니다.
    
    Args:
        input_csv: 입력 CSV 파일 경로.
        output_csv: 출력 CSV 파일 경로.
    """
    # CSV 파일 로드 (UTF-8 인코딩)
    df = pd.read_csv(input_csv, encoding="UTF-8")
    
    # 선택할 컬럼 목록
    columns_to_select: List[str] = [
        "상세영업상태명", "전화번호", "소재지면적", "소재지우편번호",
        "지번주소", "도로명주소", "도로명우편번호", "사업장명",
        "업태구분명", "좌표정보(X)", "좌표정보(Y)"
    ]
    df_selected = df[columns_to_select]
    
    # '서교동'이 포함된 지번주소 필터링 후 영업 상태("영업") 데이터 선택
    df_seo = df_selected[df_selected["지번주소"].str.contains("서교동", na=False)]
    df_seo_fil = df_seo.loc[df_seo["상세영업상태명"] == "영업"]
    
    # '합정'이 포함된 지번주소 필터링 후 영업 상태("영업") 데이터 선택
    df_hap = df_selected[df_selected["지번주소"].str.contains("합정", na=False)]
    df_hap_fil = df_hap.loc[df_hap["상세영업상태명"] == "영업"]
    
    # 서교동과 합정 데이터를 결합
    df_combined = pd.concat([df_seo_fil, df_hap_fil], ignore_index=True)
    
    # 제외할 업태 구분명: "까페", "출장조리", "기타"
    df_combined_fil = df_combined[~df_combined["업태구분명"].isin(["까페", "출장조리", "기타"])]
    
    # 최종적으로 필요한 컬럼만 선택
    df_final = df_combined_fil[[
        "소재지면적", "지번주소", "도로명주소", "사업장명",
        "업태구분명", "좌표정보(X)", "좌표정보(Y)"
    ]]
    
    # '사업장명'에서 괄호 내 텍스트 제거 후 양쪽 공백 제거
    df_final["사업장명"] = df_final["사업장명"].str.replace(r"\(.*?\)", "", regex=True).str.strip()
    
    # 최종 CSV 파일로 저장
    df_final.to_csv(output_csv, index=False, encoding="UTF-8")
    print(f"최종 데이터가 '{output_csv}' 파일로 저장되었습니다.")


def main() -> None:
    """
    메인 함수:
      1. 원본 파일("restaurant.csv")을 CP949에서 UTF-8로 변환하여 "restaurant_utf8.csv"로 저장합니다.
      2. 변환된 파일을 로드하여 데이터를 필터링 및 전처리한 후 "restaurant_df.csv"로 저장합니다.
    """
    input_file: str = "restaurant.csv"
    utf8_file: str = "restaurant_utf8.csv"
    output_file: str = "restaurant_df.csv"
    
    # 파일 인코딩 변환
    convert_file_encoding(input_file, utf8_file, input_encoding="CP949", output_encoding="UTF-8")
    
    # 데이터 필터링 및 최종 CSV 저장
    filter_restaurant_data(utf8_file, output_file)

    # 작업 완료 후 restaurant_utf8.csv 삭제
    if os.path.exists(utf8_file):
        os.remove(utf8_file)
        print(f"임시 파일 '{utf8_file}' 삭제 완료.")

if __name__ == "__main__":
    main()
