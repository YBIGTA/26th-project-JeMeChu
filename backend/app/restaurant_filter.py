# restaurant_filter.py
from datetime import datetime, timedelta
import openai
import json
import os
import re
from dotenv import load_dotenv

# Import the session and the updated RealFinal model
from app.database import SessionLocal, RealFinal
from Constants import FACILITIES, PARKING, VERY_GOOD, SEATS, TAG_GROUPS

load_dotenv()

class RestaurantFilter:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY_QUERY")
        if not self.api_key:
            raise ValueError("OpenAI API Key가 설정되지 않았습니다!")
        self.client = openai.OpenAI(api_key=self.api_key)

    def filter_ctgy(self, category: str):
        """
        1차 필터링 - 사용자의 카테고리 선택 (이제 uses realfinal)
        Returns a list of (id, business_hours).
        """
        session = SessionLocal()
        try:
            if category == "아무거나":
                restaurants = session.query(RealFinal).all()
            else:
                # Filter by category field (which must exist in realfinal!)
                restaurants = session.query(RealFinal).filter(RealFinal.category == category).all()

            # Return (id, business_hours) for convenience
            return [(r.id, r.business_hours) for r in restaurants]

        except Exception as e:
            print("DB 조회 오류:", e)
            return []
        finally:
            session.close()

    def is_restaurant_open(self, business_hours):
        """
        현재 시간을 기준으로 식당이 영업 중인지 판별.
        (unchanged logic)
        """
        day_translation = {
            "Mon": "월",
            "Tue": "화",
            "Wed": "수",
            "Thu": "목",
            "Fri": "금",
            "Sat": "토",
            "Sun": "일",
        }
        current_day_en = datetime.today().strftime('%a')
        current_day_kr = day_translation[current_day_en]
        now_time = datetime.now().time()

        if not business_hours or business_hours.strip() in ["NaN", ""]:
            return True

        for entry in business_hours.split(";"):
            entry = entry.strip()
            try:
                day, hours = entry.split(":", 1)
                day = day.strip()
                hours = hours.strip()

                if "정기휴무" in hours:
                    if current_day_kr in day:
                        return False
                    continue

                if current_day_kr in day:
                    open_str, close_str = hours.split("-")
                    open_str = open_str.strip()
                    close_str = close_str.strip()

                    if close_str == "24:00":
                        close_str = "23:59"
                    open_time = datetime.strptime(open_str, "%H:%M").time()
                    close_time = datetime.strptime(close_str, "%H:%M").time()

                    if open_time < close_time:
                        if open_time <= now_time <= close_time:
                            return True
                    else:
                        # e.g., 18:00~04:00
                        if now_time >= open_time or now_time <= close_time:
                            return True
            except ValueError:
                continue
        return False

    def filter_business_hours(self, filtered_data):
        """
        2차: 운영 시간 필터링
        filtered_data: list of (id, business_hours)
        """
        if not filtered_data:
            return []
        open_restaurants = []
        for (res_id, bhours) in filtered_data:
            if self.is_restaurant_open(bhours):
                open_restaurants.append(res_id)
        return open_restaurants

    def regenerate_query(self, details_input: str):
        """
        Query 재생성 (OpenAI)
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
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": details_input},
                ]
            )
            
            content = response.choices[0].message.content.strip()
            print("1차 필터링 expanded_query 원본:", content)  # 디버깅

            # `json` 코드 블록이 포함된 경우 제거
            json_match = re.search(r"```json\s*(\{.*\})\s*```", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                json_str = content  # 만약 코드 블록이 없으면 원본 사용

            # JSON 디코딩 (예외 처리 포함)
            expanded_query = json.loads(json_str)
            
            return expanded_query
        
        except Exception as e:
            print("OpenAI API 요청 실패:", e)
            return {}

    def filter_expanded_query(self, filtered_restaurant_ids, expanded_query):
        """
        3차: 태그 매칭
        """
        if not filtered_restaurant_ids:
            return []

        session = SessionLocal()
        try:
            # Query from realfinal with a WHERE id IN (...)
            restaurants = (
                session.query(RealFinal)
                .filter(RealFinal.id.in_(filtered_restaurant_ids))
                .all()
            )

            matched_restaurants = []
            for r in restaurants:
                # Convert None => ""
                r_facilities = r.facilities or ""
                r_parking = r.parking or ""
                r_very_good = r.very_good or ""
                r_seat_info = r.seat_info or ""

                match_found = False
                for category, tags in expanded_query.items():
                    if category == "facilities":
                        if any(tag in r_facilities for tag in tags):
                            match_found = True
                    elif category == "parking":
                        # If the entire r.parking string is in tags
                        if r_parking.strip() in tags:
                            match_found = True
                    elif category == "very_good":
                        if any(tag in r_very_good for tag in tags):
                            match_found = True
                    elif category == "seats":
                        if any(tag in r_seat_info for tag in tags):
                            match_found = True

                if match_found:
                    matched_restaurants.append(r.id)

            if not matched_restaurants:
                # If no matches, just return everything from the prior stage
                return filtered_restaurant_ids
            
            print("1차 restaurants_filter 완료~\nID:", matched_restaurants, "\n")

            return matched_restaurants

        except Exception as e:
            print("DB 조회 오류:", e)
            return []
        
        finally:
            session.close()