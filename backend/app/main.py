## fastapi 실행
from fastapi import FastAPI
from pydantic import BaseModel
from restaurant_filter import RestaurantFilter

app = FastAPI()
restaurant_filter = RestaurantFilter()

class FilterRequest(BaseModel):
    ctgy: str  # 카테고리
    details: str  # 세부사항

@app.post("/filter_restaurants/")
async def filter_restaurants(request: FilterRequest):
    """
    1차 필터링 (카테고리 기반) → 운영 시간 필터링 → 2차 필터링 (세부사항 기반)
    """
    # 1차 필터링 (카테고리 기준)
    id_list = restaurant_filter.filter_ctgy(request.ctgy)
    
    # 운영 시간 기준 필터링
    open_restaurants = restaurant_filter.filter_business_hours(id_list)

    # Query 재생성 (사용자가 입력한 세부 필터를 태그 기반으로 변환)
    expanded_query = restaurant_filter.regenerate_query(request.details)

    # 2차 필터링 (태그 매칭 수행)
    result = restaurant_filter.filter_expanded_query(open_restaurants, expanded_query)

    return {"restaurants": result}

# FastAPI 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 실행 원하면 : python backend/app/main.py 실행해보삼..