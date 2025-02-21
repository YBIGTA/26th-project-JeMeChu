## fastapi 실행
from fastapi import FastAPI
from pydantic import BaseModel
from menu_filter import filter_restaurants
from details_filter import regenerate_query, filter_by_expanded_query

app = FastAPI()

# 아예 filter를 하나로 통합..
class FilterRequest(BaseModel):
    user_input: str  # 메뉴명 or 카테고리 or "아무거나"
    details: str  # 세부사항

class MenuRequest(BaseModel):
    user_input: str  # 메뉴명 또는 카테고리명 또는 "아무거나"

class DetailsRequest(BaseModel):
    details: str

@app.post("/filter_restaurants_with_details/")
async def filter_restaurants_with_details(request: FilterRequest):
    """
    사용자가 입력한 메뉴 또는 카테고리 + 세부사항 기반으로 식당 필터링 API
    """
    # 1차 필터링 (메뉴 또는 카테고리)
    filtered_data = filter_restaurants(request.user_input)

    # 2차 필터링 (세부사항)
    expanded_query = regenerate_query(request.details)
    result = filter_by_expanded_query(filtered_data, expanded_query)

    return {"restaurants": result}

@app.post("/filter_restaurants/")
async def filter_restaurants_api(request: MenuRequest):
    """
    사용자가 입력한 메뉴 또는 카테고리 기반으로 식당 필터링 API
    """
    result = filter_restaurants(request.user_input)
    return {"restaurants": result}

@app.post("/filter_details/")
async def filter_details(request: DetailsRequest):
    """
    세부사항 기반 식당 필터링 API
    """
    expanded_query = regenerate_query(request.details)
    result = filter_by_expanded_query(expanded_query)
    return {"restaurants": result}

# FastAPI 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 실행 원하면 : python backend/app/main.py 실행해보삼..