from datetime import datetime, timedelta
import openai
import json
import os
import re
from dotenv import load_dotenv

from database import get_db_connection
from backend.Constants import FACILITIES, PARKING, VERY_GOOD, SEATS, TAG_GROUPS
# .env 파일 로딩하여 OpenAI API Key 가져오기
load_dotenv()

class RestaurantFilter:
    """
    식당 필터링을 위한 클래스
    1. 1차 필터링 (카테고리/메뉴)
    2. 운영 시간 필터링 추가
    3. Query 재생성 (사용자 검색어 확장)
    4. 2차 필터링 (세부사항 기반 필터링)
    """

    def __init__(self):
        self.conn = get_db_connection()
        self.api_key = os.getenv("OPENAI_API_KEY_QUERY")
        if not self.api_key:
            raise ValueError("OpenAI API Key가 설정되지 않았습니다!")
        
        self.client = openai.OpenAI(api_key=self.api_key)

    def filter_ctgy(self, category: str):
        """
        1차 필터링 - 사용자의 카테고리 선택에 따라 식당 id 리스트 반환.
        """
        if self.conn is None:
            return []

        cursor = self.conn.cursor()
        try:
            if category == "아무거나":
                # debugging
                cursor.execute("SELECT id, name, category, menu, business_hours, facilities, parking, very_good, seat_info FROM reviews") # 디버깅용(아래 줄로 바꾸기) 
                # cursor.execute("SELECT id, business_hours FROM reviews")
            else:
                # debugging
                cursor.execute("SELECT id, name, category, menu, business_hours, facilities, parking, very_good, seat_info FROM reviews WHERE category = %s", (category,)) # 디버깅용(아래 줄로 바꾸기) 
                # cursor.execute("SELECT id, business_hours FROM reviews WHERE category = %s", (category,))
            
            results = cursor.fetchall()

            ## debugging
            # 새로운 쿼리 추가: 전체 식당 개수 확인 
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE category = %s", (category,))
            total_count = cursor.fetchone()[0]

            # 필터링된 데이터 출력
            # filtered_results = []
            # for res in results:
            #     filtered_results.append({
            #         "id": res["id"],
            #         "name": res["name"],
            #         "category": res["category"],
            #         "menu": res["menu"],
            #         "business_hours": res["business_hours"],
            #         "facilities": res["facilities"],
            #         "parking": res["parking"],
            #         "very_good": res["very_good"],
            #         "seat_info": res["seat_info"]
            #     })
            
            # print(f"전체 {category} 식당 개수: {total_count}")
            # print(f"{category} 카테고리 필터링 결과:")
            # print("ctgy filtered data:", json.dumps(filtered_results, indent=2, ensure_ascii=False))
            ## debugging

            return [(res["id"], res["business_hours"]) for res in results]  # ID, business_hours만 반환

        except Exception as e:
            print("DB 조회 오류:", e)
            return []
        finally:
            cursor.close()

    def is_restaurant_open(self, business_hours):
        """
        현재 시간을 기준으로 식당이 영업 중인지 판별하는 함수.
        - business_hours 예시: "화: 11:00 - 24:00; 수: 11:00 - 24:00; ..."
        - 운영 시간이 현재 시간과 겹치는 경우 True 반환.
        """
        # if not business_hours:
        #     return False  # 운영 시간 정보가 없으면 영업 중이 아니라고 간주
        
        day_translation = {
            "Mon": "월",
            "Tue": "화",
            "Wed": "수",
            "Thu": "목",
            "Fri": "금",
            "Sat": "토",
            "Sun": "일",
        }

        current_day_en = datetime.today().strftime('%a')  # 현재 요일 (Mon, Tues, ...)
        current_day_kr = day_translation[current_day_en]  # 현재 요일 (월, 화, ...)
        # current_time = datetime.now().strftime('%H:%M')  # 현재 시간 (HH:MM)
        now_time = datetime.now().time() # 현재 시간 (HH:MM)
        print(f"현재 시간: {current_day_kr}, {now_time}")
        print(type(now_time))

        # business_hours가 NaN이거나 비어있는 경우 → 식당을 포함 (True 반환)
        if not business_hours or business_hours.strip() in ["NaN", ""]:
            print("운영시간 정보 없음 → 그냥 식당 포함")
            return True  # 운영 시간 정보가 없는 경우 식당 포함

        # business_hours를 ';' 기준으로 분리
        for entry in business_hours.split(";"):
            entry = entry.strip()  # 공백 제거

            try:
                day, hours = entry.split(":", 1)
                day = day.strip()
                hours = hours.strip()
                print(f"요일: {day}, 운영시간: {hours}")

                # 정기휴무인 경우 처리
                if "정기휴무" in hours:
                    print(f"{day}은 정기휴무일 → 영업 안함")
                    return False

                # 현재 요일과 일치하는 운영 시간이 있는 경우
                if current_day_kr in day:
                    print("오늘 해당 요일: ", current_day_kr)

                    open_time, close_time = hours.split("-")
                    open_time_str, close_time_str = open_time.strip(), close_time.strip()
                
                    # 24:00 → 23:59 또는 00:00으로 변환 (format 안 맞아서 ValueError 발생)
                    if close_time_str == "24:00":
                        close_time_str = "23:59"

                    open_time = datetime.strptime(open_time_str, "%H:%M").time()
                    close_time = datetime.strptime(close_time_str, "%H:%M").time()

                    print(f"오픈시간: {open_time}, 마감: {close_time}")

                    # 운영 시간 비교
                    if open_time < close_time: #(11:00-24:00)
                        if open_time <= now_time <= close_time:
                            print(f"{open_time} ~ {close_time} 사이 → 영업 중")
                            return True  # 영업 중
                    else: # (예: `18:00 - 04:00` → 다음날 새벽까지)
                        close_time_dt = (datetime.now() + timedelta(days=1)).replace(
                            hour=close_time.hour, minute=close_time.minute
                        )

                        if now_time >= open_time or datetime.now() <= close_time_dt:
                            print(f"{open_time} ~ {close_time} 사이 → 영업 중")
                            return True  # 영업 중
                    
            except ValueError as e:
                print("value error: ", e)
                continue  # 데이터 형식이 맞지 않으면 넘어감

        return False  # 현재 시간과 일치하는 운영 시간이 없으면 False 반환

    def filter_business_hours(self, filtered_data):
        """
        운영 시간이 현재 시간과 일치하는 식당만 필터링
        """
        if not filtered_data:
            print("data 없음")
            return []

        open_restaurants = []
        for res_id, business_hours in filtered_data:
            if self.is_restaurant_open(business_hours):
                open_restaurants.append(res_id)  # 운영 중인 식당의 id만 저장

        print(f"운영 중인 식당 ID 리스트: {open_restaurants}")
        return open_restaurants

    def regenerate_query(self, details_input: str):
        """
        2차 필터링을 위한 Query 재생성 - JSON 형식으로 변환
        """
        system_prompt = f"""
        사용자의 검색어를 분석하여 JSON 형식으로 반환하세요.
        - 반드시 아래 제공된 리스트 속 단어 중에서만 선택하여 반환하세요.
        - JSON 형식으로만 출력하세요.
        - **주차 관련 키워드(주차 가능, 무료 주차 등)가 있으면 `parking`을 무조건 포함하세요.**
        - **좌석(seats) 관련 단어(단체석, 룸, 바테이블 등)가 있으면 `seats`를 포함하세요.**
        - 다른 카테고리는 중요도를 고려하여 최대 2개만 선택하세요.

        ### 사용 가능한 값:
        - **facilities**: {", ".join(FACILITIES)}
        - **parking**: {", ".join(PARKING)}
        - **very_good**: {", ".join(VERY_GOOD)}
        - **seat_info**: {", ".join(SEATS)}

        ### 예시:
        - 입력: '김치찌개 조용하고 주차할 수 있는 데서 먹고 싶어'
          출력: {{"very_good": ["조용히 쉬기 좋아요"], "parking": ["주차 가능"]}}
        
        - 입력: '단체석 있고 와인 추천 잘해주는 곳'
          출력: {{"facilities": ["와인 페어링"], "seat_info": ["와인 페어링"]}}

        - 입력: '아늑한 분위기의 조용한 식당'
          출력: {{"very_good": ["아늑해요", "조용히 쉬기 좋아요"]}}

        - 입력: '대기공간 있고, 유아의자 있는 곳'
          출력: {{"facilities": ["대기공간", "유아의자"]}}

        - 입력: '5명이서 다 기분 좋게 기분전환할 수 있는 식당'
        - 출력: {{"seat_info": ["단체석"], "very_good": ["분위기가 편안해요"]}}
        """

        try:
            response = self.client.chat.completions.create(  # 최신 API 방식 사용
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": details_input}]
            )

            expanded_query = json.loads(response.choices[0].message.content)
            return expanded_query

        except Exception as e:
            print("OpenAI API 요청 실패:", e)
            return {}

    def filter_expanded_query(self, filtered_restaurant_ids, expanded_query):
        """
        2차 필터링 - Query 재생성 결과를 기반으로 태그 매칭 수행.
        """
        if not filtered_restaurant_ids:
            print("1차 필터링 후 남은 식당이 없음 → 추가 필터링 없이 반환")
            return []

        cursor = self.conn.cursor()
        try:
            # 운영시간 필터링된 식당 ID 기준으로 태그 데이터 가져오기
            cursor.execute("""
                SELECT id, facilities, parking, very_good, seat_info 
                FROM reviews 
                WHERE id IN %s
            """, (tuple(filtered_restaurant_ids),))
            results = cursor.fetchall()

            matched_restaurants = []
            for res in results:
                res_id, facilities, parking, very_good, seat_info = (
                    res["id"], (res["facilities"]) if res["facilities"] else [],
                    res["parking"], (res["very_good"]) if res["very_good"] else [],
                    (res["seat_info"]) if res["seat_info"] else []
                )

                # 태그 매칭 검사
                match_found = False
                for category, tags in expanded_query.items():
                    if category == "facilities" and any(tag in facilities for tag in tags):
                        match_found = True
                    if category == "parking" and parking in tags:
                        match_found = True
                    if category == "very_good" and any(tag in very_good for tag in tags):
                        match_found = True
                    if category == "seats" and any(tag in seat_info for tag in tags):
                        match_found = True
                print(match_found)
                if match_found:
                    matched_restaurants.append(res_id)

            return matched_restaurants

        except Exception as e:
            print("DB 조회 오류:", e)
            return []
        finally:
            cursor.close()



## debugging
if __name__ == "__main__":
    # 필터링 객체 생성
    restaurant_filter = RestaurantFilter()

    # 1-1차 필터링: 카테고리 선택 (예: '한식')
    test_category = "한식"  # 테스트할 카테고리
    filtered_data = restaurant_filter.filter_ctgy(test_category)
    
    print(f"\n'{test_category}' 카테고리의 1차 필터링 결과 (ID + 운영시간):")
    print(json.dumps(filtered_data, indent=2, ensure_ascii=False))

    # 1-2차 필터링: 운영시간 필터링
    open_restaurants = restaurant_filter.filter_business_hours(filtered_data)

    print(f"\n'{test_category}' 카테고리에서 운영 중인 식당 리스트:")
    print(json.dumps(open_restaurants, indent=2, ensure_ascii=False))

    # query 재생성
    print("\n[Query 재생성] LLM을 통한 태그 변환")
    test_queries = [
        # "아늑한 분위기에서 유아의자 있는 곳에서 먹고 싶어",
        "노키즈존이고 비건 메뉴 있는 식당 알려줘",
        # "나 지금 오늘 아침 5시에 일어나서 화가 너무 많은데 지금 머리도 뜨겁고 플젝도 어렵고 우리 팀플하고 있어서 5명이서 다 기분좋게 기분전환할 수 있는 식당좀",
        # "주차 가능한 곳에서 단체석 있는 식당 추천해줘",
        # "야외 테라스가 있고, 조용한 분위기의 레스토랑",
        # "배달 가능한 곳 중에서 포장 할인되는 곳 알려줘"
    ]

    for details_test in test_queries:
        expanded_query = restaurant_filter.regenerate_query(details_test)

        print(f"\n'{details_test}'에 대한 확장 쿼리:")
        print(json.dumps(expanded_query, indent=2, ensure_ascii=False))

        print("\n[3차 필터링] 태그 기반 필터링")
        final_filtered_restaurants = restaurant_filter.filter_expanded_query(open_restaurants, expanded_query)

        print(f"\n최종 필터링 결과 (태그 기반):")
        print(json.dumps(final_filtered_restaurants, indent=2, ensure_ascii=False))

