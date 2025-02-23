from database import get_db_connection
import json
from datetime import datetime

## db 열 구조 수정 후 함수 수정 예정
def filter_ctgy(ctgy: str):
    """
    - 사용자의 입력(ctgy)에 따라 식당을 필터링.
    - 입력이 특정 "메뉴"라면 해당 메뉴가 포함된 식당만 반환.
    - 입력이 특정 "카테고리(한식, 중식, 일식 등)"라면 해당 카테고리의 식당을 반환.
    - 입력이 "아무거나"라면 모든 식당 반환.
    """
    categories = {"한식", "중식", "일식", "양식", "주점"}

    if ctgy in categories:
        return filter_by_category_from_db(ctgy)
    elif ctgy == "아무거나":
        return filter_by_category_from_db("아무거나")  # 모든 식당 반환
    else:
        return None
        # return filter_by_menu_from_db(ctgy)  # 메뉴 필터링

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
            cursor.execute("SELECT id, name, category, menu, business_hours, facilities, parking, very_good, seat_info FROM reviews LIMIT 3") # 디버깅용(아래 줄로 바꾸기) 
            # cursor.execute("SELECT id FROM reviews LIMIT 3") # SELECT id, name, category, menu, business_hours, , facilities, parking, very_good FROM reviews 
        else:
            cursor.execute("SELECT id, name, category, menu, business_hours, facilities, parking, very_good, seat_info FROM reviews WHERE category = %s LIMIT 3", (category,)) # 디버깅용(아래 줄로 바꾸기) 
            # cursor.execute("SELECT id FROM reviews WHERE category = %s LIMIT 3", (category,)) # SELECT id, name, category, menu, business_hours, , facilities, parking, very_good FROM reviews 
 
        results = cursor.fetchall()

        ## 새로운 쿼리 추가: 전체 식당 개수 확인 (debugging)
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE category = %s", (category,))
        total_count = cursor.fetchone()[0]

        conn.close()

        ## debugging용
        filtered_results = []
        for res in results:
            filtered_results.append({
                "id": res["id"],
                "name": res["name"],
                "category": res["category"],
                "menu": res["menu"],
                # "menu": parse_menu(res["menu"]),
                "business_hours": res["business_hours"],
                # "facilities": json.loads(res["facilities"]) if isinstance(res["facilities"], str) else res["facilities"],
                "facilities": res["facilities"],
                "parking": res["parking"],
                "very_good": res["very_good"],
                "seat_info": res["seat_info"]
            })
        
        # 디버깅 출력 (필터링된 데이터와 전체 개수 확인)
        print(f"전체 {category} 식당 개수: {total_count}")
        print(f"{category} 카테고리 필터링 결과:")
        print("ctgy filtered data:", json.dumps(filtered_results, indent=2, ensure_ascii=False))

        ## debugging용

        # id만 리스트로 반환
        return [res["id"] for res in results]

    except Exception as e:
        print("DB 조회 오류:", e)
        return []
    finally:
        cursor.close()
        conn.close()

# 이건 나중에 menu 다룰 때 하기 (ctgy filter랑 다름..)
def filter_by_menu_from_db(menu_item: str):
    """
    PostgreSQL에서 특정 메뉴가 포함된 식당을 필터링.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, category, menu, business_hours, facilities, parking, very_good, seat_info FROM reviews") # 나중에 id 추가!!!!!
        results = cursor.fetchall()
        conn.close()
        
        filtered_data = []
        for res in results:
            menu_list = []
            if isinstance(res["menu"], str):  # 메뉴가 문자열이면 JSON 변환
                try:
                    menu_list = json.loads(res["menu"])
                except json.JSONDecodeError:
                    menu_list = []

            elif isinstance(res["menu"], list):  # 이미 리스트라면 그대로 사용
                menu_list = res["menu"]
            
            

            if menu_item in menu_list:  # 특정 메뉴가 포함된 경우만 추가
                filtered_data.append({
                    "id": res["id"],
                    "name": res["name"],
                    "category": res["category"],
                    "menu": parse_menu(res["menu"]),
                    "business_hours": res["business_hours"],
                    "facilities": parse_keywords(res["keyword"])[0],  # 시설 정보
                    "parking": parse_keywords(res["keyword"])[1],  # 주차 정보
                    "very_good": parse_keywords(res["keyword"])[2],  # "이런 점이 좋았어요"
                    # "facilities": json.loads(res["facilities"]) if isinstance(res["facilities"], str) else res["facilities"],
                    "facilities": safe_json_loads(res["facilities"]),
                    "parking": res["parking"],
                    "very_good": res["very_good"],
                    "seat_info": res["seat_info"]
                })

        return filtered_data[:3] #  나중에 바꾸기

    except Exception as e:
        print("메뉴 필터링 오류:", e)
        return []
    finally:
        cursor.close()
        conn.close()





# 직접 실행할 경우 테스트 코드 추가
if __name__ == "__main__":
    test_inputs = ["양식"]

    for user_input in test_inputs:
        print(f"\n'{user_input}'에 해당하는 식당 필터링 결과:")
        result = filter_ctgy(user_input)
        print("id: " + json.dumps(result, indent=2, ensure_ascii=False))  # JSON 형식으로 깔끔하게 출력
