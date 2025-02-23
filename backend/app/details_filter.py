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
    facilities: 단체 이용 가능, 예약, 무선 인터넷, 와인 페어링, 전문 소믈리에, 포장, 배달, 남/녀 화장실 구분, 장애인 휠체어 이용가능, 출입구 휠체어 이용가능, 콜키지 가능, 생일 혜택, 유아의자, 노키즈존, 비건 메뉴, 반려동물 동반, 대기공간, 좌석 휠체어 이용가능, 테이크아웃 할인, 방문접수/출장, 장애인 주차구역, 무한 리필, 글루텐프리 메뉴, 유기농 메뉴, 유아시설 (놀이방), 핸드드립
    parking: 주차 불가, 무료 주차 가능, 유료 주차 가능, 주차 가능
    very_good: 음식이 맛있어요, 인테리어가 멋져요, 친절해요, 대화하기 좋아요, 술이 다양해요, 음악이 좋아요, 재료가 신선해요, 양이 많아요, 혼밥하기 좋아요, 특별한 메뉴가 있어요, 가성비가 좋아요, 고기 질이 좋아요, 직접 잘 구워줘요, 기본 안주가 좋아요, 단체모임 하기 좋아요, 디저트가 맛있어요, 음료가 맛있어요, 커피가 맛있어요, 특별한 날 가기 좋아요, 매장이 넓어요, 매장이 청결해요, 아늑해요, 컨셉이 독특해요, 현지 맛에 가까워요, 혼술하기 좋아요, 야외공간이 멋져요, 오래 머무르기 좋아요, 반찬이 잘 나와요, 품질이 좋아요, 종류가 다양해요, 빵이 맛있어요, 시설이 깔끔해요, 게임 종류가 다양해요, 침구가 좋아요, 조용히 쉬기 좋아요, 깨끗해요, 메뉴 구성이 알차요, 차가 맛있어요, 마사지가 시원해요, 맞춤 케어를 잘해줘요, 분위기가 편안해요, 뷰가 좋아요
    seat_info: 카운터석, 입식, 바테이블, 룸, 단체석, 테라스, 좌식, 1인석, 연인석, 루프탑


    - 입력: "많을 사람들과 함께 예약을 해서 주차 가능한 곳"
    - 출력: {"facilities": ["단체 이용 가능"], "주차": ["주차 가능"]}
    
    - 입력: "아이와 함께 갈 만한 곳"
    - 출력: {"시설": ["유아 의자"], "이런 점이 좋았어요": ["친절해요"]}
    
    - 입력: "단체석 있고 와인 추천 잘해주는 곳"
    - 출력: {"시설": ["단체 이용 가능", "전문 소믈리에"]}
    
    이런식으로 중요해보이는거 사용자의 검색어에서 중요해보이는 개념 2가지를 뽑아줘

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
    - filtered_data: `ctgy_filter.py`에서 필터링된 식당 리스트
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
    from ctgy_filter import filter_ctgy

    # 1차 필터링 (메뉴/카테고리 기반)
    user_input = "한식"  # 테스트용 입력값
    filtered_data = filter_ctgy(user_input)

    # 2차 필터링 (세부사항 기반)
    details_test = "조용하고 주차 가능한 곳"
    details_test = "김치찌개 조용하고 주차할 수 있는 데서 먹고 싶어"
    expanded_query = regenerate_query(details_test)

    print(f"\n'{details_test}'에 대한 확장 쿼리:")
    print(expanded_query)

    print(f"\n최종 필터링된 식당 리스트:")
    print(filter_by_expanded_query(filtered_data, expanded_query))
