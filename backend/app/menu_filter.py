from database import get_db_connection
import json
from datetime import datetime

## db 열 구조 수정 후 함수 수정 예정
def filter_restaurants(user_input: str):
    """
    - 사용자의 입력(user_input)에 따라 식당을 필터링.
    - 입력이 특정 "메뉴"라면 해당 메뉴가 포함된 식당만 반환.
    - 입력이 특정 "카테고리(한식, 중식, 일식 등)"라면 해당 카테고리의 식당을 반환.
    - 입력이 "아무거나"라면 모든 식당 반환.
    """
    categories = {"한식", "중식", "일식", "양식", "주점"}

    if user_input in categories:
        return filter_by_category_from_db(user_input)
    elif user_input == "아무거나":
        return filter_by_category_from_db("아무거나")  # 모든 식당 반환
    else:
        return filter_by_menu_from_db(user_input)  # 메뉴 필터링

def safe_json_loads(value, default=[]):
    """JSON 문자열을 변환하고, 오류 시 기본값 반환"""
    if not value or value.lower() in ["null", "none"]:
        return default
    try:
        return json.loads(value) if isinstance(value, str) else value
    except json.JSONDecodeError:
        return default

def parse_menu(menu_data):
    """메뉴 데이터가 이중 리스트 형태일 경우 변환"""
    menu_list = safe_json_loads(menu_data, default=[])
    return [item[0] for item in menu_list] if menu_list else ["메뉴 정보 없음"]


def parse_keywords(keyword_data):
    """keyword 열에서 facilities, parking, very_good을 분리"""
    keyword_list = safe_json_loads(keyword_data, default=[])
    
    facilities = keyword_list[:-4] if len(keyword_list) > 4 else keyword_list  # 앞부분 = 시설 정보
    very_good = keyword_list[-4:] if len(keyword_list) > 4 else []  # 마지막 4개 = "이런 점이 좋았어요"
    parking = "주차 가능" if any("주차 가능" in kw for kw in keyword_list) else "주차 불가"

    return facilities, parking, very_good


def filter_by_category_from_db(category: str):
    """
    PostgreSQL에서 카테고리에 해당하는 식당을 필터링.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        if category == "아무거나":
            cursor.execute("SELECT name, category, menu, business_hours, keyword FROM restaurant_updated LIMIT 3") # SELECT id, name, category, menu, business_hours, , facilities, parking, very_good FROM restaurant_updated 
        else:
            cursor.execute("SELECT name, category, menu, business_hours, keyword FROM restaurant_updated WHERE category = %s LIMIT 3", (category,))
        
        results = cursor.fetchall()
        conn.close()

        return [
            {
                "name": res["name"],
                "category": res["category"],
                "menu": parse_menu(res["menu"]),
                "business_hours": res["business_hours"] if res["business_hours"] else "영업시간 정보 없음",
                **dict(zip(["facilities", "parking", "very_good"], parse_keywords(res["keyword"])))
            }
            for res in results
        ]

        # filtered_results = []
        # for res in results:
        #     menu_list = []
        #     if isinstance(res["menu"], str):  # JSON 변환 처리
        #         try:
        #             menu_list = json.loads(res["menu"]) if res["menu"] else []
        #         except json.JSONDecodeError:
        #             menu_list = []
        #     elif isinstance(res["menu"], list):
        #         menu_list = res["menu"]

        #     filtered_results.append({
        #         # "id": res["id"],
        #         "name": res["name"],
        #         "category": res["category"],
        #         "menu": parse_menu(res["menu"]),
        #         "business_hours": res["business_hours"],
        #         "facilities": parse_keywords(res["keyword"])[0],  # 시설 정보
        #         "parking": parse_keywords(res["keyword"])[1],  # 주차 정보
        #         "very_good": parse_keywords(res["keyword"])[2]  # "이런 점이 좋았어요"
        #         # "facilities": json.loads(res["facilities"]) if isinstance(res["facilities"], str) else res["facilities"],
        #         # "facilities": safe_json_loads(res["facilities"]),
        #         # "parking": res["parking"],
        #         # "very_good": res["very_good"]
        #     })

        # return filtered_results

    except Exception as e:
        print("DB 조회 오류:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def filter_by_menu_from_db(menu_item: str):
    """
    PostgreSQL에서 특정 메뉴가 포함된 식당을 필터링.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, category, menu, business_hours, keyword FROM restaurant_updated") # 나중에 id 추가!!!!!
        results = cursor.fetchall()
        conn.close()

        filtered_data = []
        for res in results:
            menu_list = parse_menu(res["menu"])
            
            if menu_item in menu_list:  # 특정 메뉴가 포함된 경우만 추가
                filtered_data.append({
                    "name": res["name"],
                    "category": res["category"],
                    "menu": menu_list,
                    "business_hours": res["business_hours"] if res["business_hours"] else "영업시간 정보 없음",
                    **dict(zip(["facilities", "parking", "very_good"], parse_keywords(res["keyword"])))
                })

        return filtered_data[:3]  # 최대 3개 반환


        # def parse_menu(menu_data):
        #     """메뉴 데이터가 이중 리스트 형태일 경우 변환"""
        #     try:
        #         menu_list = json.loads(menu_data) if isinstance(menu_data, str) else menu_data
        #         return [item[0] for item in menu_list]  # 메뉴 이름만 추출
        #     except json.JSONDecodeError:
        #         return []

        # def parse_keywords(keyword_data):
        #     """keyword 열에서 facilities, parking, very_good을 분리"""
        #     try:
        #         keyword_list = json.loads(keyword_data) if isinstance(keyword_data, str) else keyword_data
        #         facilities = keyword_list[:-4] if len(keyword_list) > 4 else keyword_list  # 앞부분 = 시설 정보
        #         very_good = keyword_list[-4:] if len(keyword_list) > 4 else []  # 마지막 4개 = "이런 점이 좋았어요"
        #         parking = "주차 가능" if "주차 가능" in keyword_list else "주차 불가"
        #         return facilities, parking, very_good
        #     except json.JSONDecodeError:
        #         return [], "주차 정보 없음", []

        
        # filtered_data = []
        # for res in results:
        #     menu_list = []
        #     if isinstance(res["menu"], str):  # 메뉴가 문자열이면 JSON 변환
        #         try:
        #             menu_list = json.loads(res["menu"])
        #         except json.JSONDecodeError:
        #             menu_list = []

        #     elif isinstance(res["menu"], list):  # 이미 리스트라면 그대로 사용
        #         menu_list = res["menu"]
            
            

        #     if menu_item in menu_list:  # 특정 메뉴가 포함된 경우만 추가
        #         filtered_data.append({
        #             # "id": res["id"],
        #             "name": res["name"],
        #             "category": res["category"],
        #             "menu": parse_menu(res["menu"]),
        #             "business_hours": res["business_hours"],
        #             "facilities": parse_keywords(res["keyword"])[0],  # 시설 정보
        #             "parking": parse_keywords(res["keyword"])[1],  # 주차 정보
        #             "very_good": parse_keywords(res["keyword"])[2]  # "이런 점이 좋았어요"
        #             # "facilities": safe_json_loads(res["facilities"]),
        #             # # "facilities": json.loads(res["facilities"]) if isinstance(res["facilities"], str) else res["facilities"],
        #             # "parking": res["parking"],
        #             # "very_good": res["very_good"]
        #         })

        # return filtered_data[:3] #  나중에 바꾸기

    except Exception as e:
        print("메뉴 필터링 오류:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def safe_json_loads(value, default=[]):
            """JSON 문자열을 변환하고, 오류 시 기본값 반환"""
            if not value or value in ["null", "NULL"]:
                return default
            try:
                return json.loads(value) if isinstance(value, str) else value
            except json.JSONDecodeError:
                return default



# 직접 실행할 경우 테스트 코드 추가
if __name__ == "__main__":
    test_inputs = ["한식", "김치찌개", "아무거나"]

    for user_input in test_inputs:
        print(f"\n'{user_input}'에 해당하는 식당 필터링 결과:")
        result = filter_restaurants(user_input)
        print(json.dumps(result, indent=2, ensure_ascii=False))  # JSON 형식으로 깔끔하게 출력
