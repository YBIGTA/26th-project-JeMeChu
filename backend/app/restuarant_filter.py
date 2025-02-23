from database import get_db_connection
import openai
import json
import os
from dotenv import load_dotenv

# .env 파일 로딩하여 OpenAI API Key 가져오기
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY_QUERY")

class RestaurantFilter:
    """
    식당 필터링을 위한 클래스
    1. 1차 필터링 (카테고리/메뉴)
    2. 2차 필터링 (세부사항 기반 필터링)
    3. Query 재생성 (사용자 검색어 확장)
    """

    def __init__(self):
        self.conn = get_db_connection()

    def filter_ctgy(self, category: str):
        """
        1차 필터링 - 사용자의 카테고리 선택에 따라 식당 id 리스트 반환.
        """
        if self.conn is None:
            return []

        cursor = self.conn.cursor()
        try:
            if category == "아무거나":
                cursor.execute("SELECT id FROM restaurant_updated LIMIT 3")
            else:
                cursor.execute("SELECT id FROM restaurant_updated WHERE category = %s LIMIT 3", (category,))
            
            results = cursor.fetchall()
            return [res["id"] for res in results]

        except Exception as e:
            print("DB 조회 오류:", e)
            return []
        finally:
            cursor.close()

    def regenerate_query(self, details_input: str):
        """
        2차 필터링을 위한 Query 재생성 - JSON 형식으로 변환
        """
        system_prompt = """
        사용자의 검색어를 분석하여 JSON 형식으로 반환하세요.
        
        예시:
        - 입력: '김치찌개 조용하고 주차할 수 있는 데서 먹고 싶어'
          출력: {"menu": ["김치찌개"], "분위기": ["조용함"], "주차": ["주차 가능"]}
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
            return {}

    def filter_by_expanded_query(self, id_list, expanded_query):
        """
        2차 필터링 - Query 재생성 결과를 기반으로 식당 필터링 수행
        """
        if not id_list:
            print("1차 필터링 결과가 비어 있음 → 추가 필터링 없이 반환")
            return []

        cursor = self.conn.cursor()

        try:
            cursor.execute(
                "SELECT id, name, facilities, parking, very_good FROM restaurant_updated WHERE id IN %s",
                (tuple(id_list),)
            )
            results = cursor.fetchall()

            matched_restaurants = []

            for res in results:
                res_id, name = res["id"], res["name"]
                facilities = json.loads(res["facilities"]) if isinstance(res["facilities"], str) else res["facilities"]
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

        except Exception as e:
            print("DB 조회 오류:", e)
            return []
        finally:
            cursor.close()
            self.conn.close()
