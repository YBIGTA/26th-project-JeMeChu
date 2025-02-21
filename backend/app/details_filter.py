from database import get_db_connection
import openai
import json
import os
from dotenv import load_dotenv

# .env 파일 로딩하여 OpenAI API Key 가져오기
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY_QUERY") ## 이건 query 재생성용 api key라서 본인 것과 다를 수 있음

def regenerate_query(details_input):
    """
    사용자의 검색어를 기반으로 관련 개념을 확장하여 JSON 형식으로 변환.
    예: "조용하고 주차 가능한 곳" -> {'시설': ['조용한 분위기', '방음'], '주차': ['주차 가능']}
    """
    system_prompt = """
    사용자의 검색어를 기반으로 관련 개념을 확장하여 JSON 형식으로 반환하세요.
    예시:
    - 입력: "조용하고 주차 가능한 곳"
    - 출력: {"시설": ["조용한 분위기", "방음"], "주차": ["주차 가능"]}
    
    - 입력: "아이와 함께 갈 만한 곳"
    - 출력: {"시설": ["유아 의자", "키즈존"], "이런 점이 좋았어요": ["가족 친화적"]}
    
    - 입력: "단체석 있고 와인 추천 잘해주는 곳"
    - 출력: {"시설": ["단체석", "와인 추천"]}
    
    JSON 형식으로만 출력하세요.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": details_input}]
        )

        expanded_query = json.loads(response["choices"][0]["message"]["content"])
        return expanded_query

    except Exception as e:
        print("OpenAI API 요청 실패:", e)
        return {}  # 실패 시 빈 딕셔너리 반환


def filter_by_expanded_query(filtered_data, expanded_query):
    """
    1차 필터링된 데이터(filtered_data)에서 Query 재생성을 기반으로 세부 필터링 수행.
    - filtered_data: `menu_filter.py`에서 필터링된 식당 리스트
    - expanded_query: JSON 형식의 필터 기준
    """
    if not filtered_data:
        print("1차 필터링 결과가 비어 있음 → 추가 필터링 없이 반환")
        return []  # 빈 리스트 반환하여 오류 방지
    conn = get_db_connection()
    if conn is None:
        return []

    matched_restaurants = []

    for res in filtered_data:
        name = res["name"]
        facilities = res["facilities"]
        parking = res["parking"]
        highlights = res["very_good"]

        matched_details = {
            "식당명": name,
            "편의시설": [f for f in expanded_query.get("시설", []) if f in facilities],
            "주차": [p for p in expanded_query.get("주차", []) if p in parking],
            "이런 점이 좋았어요": [h for h in expanded_query.get("이런 점이 좋았어요", []) if h in highlights],
        }

        if any(matched_details.values()):
            matched_restaurants.append(matched_details)

    return matched_restaurants


# 직접 실행할 경우 테스트 코드 추가
if __name__ == "__main__":
    from menu_filter import filter_restaurants

    # 1차 필터링 (메뉴/카테고리 기반)
    user_input = "김치찌개"  # 테스트용 입력값
    filtered_data = filter_restaurants(user_input)

    # 2차 필터링 (세부사항 기반)
    details_test = "조용하고 주차 가능한 곳"
    expanded_query = regenerate_query(details_test)

    print(f"\n'{details_test}'에 대한 확장 쿼리:")
    print(expanded_query)

    print(f"\n최종 필터링된 식당 리스트:")
    print(filter_by_expanded_query(filtered_data, expanded_query))
