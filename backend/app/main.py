from fastapi import FastAPI
from pydantic import BaseModel
from restaurant_filter import RestaurantFilter
from rag import RAGEngine

app = FastAPI()

# 모듈 객체 초기화
restaurant_filter = RestaurantFilter()
rag_engine = RAGEngine()

class FilterRequest(BaseModel):
    ctgy: str      # 카테고리
    details: str   # 세부사항 (태그 확장을 위한 입력)
    # query: str     # RAG 검색용 사용자 쿼리

@app.post("/filter_restaurants/")
async def filter_restaurants(request: FilterRequest):
    """
    1. restaurant_filter 모듈을 이용해
       - 카테고리 필터링 → 운영시간 필터링 → 태그 기반 2차 필터링을 수행하여 최종 식당 id 리스트를 도출합니다.
    2. 도출된 최종 id 리스트를 allowed_ids로 하여, rag 모듈에서 해당 문서들만 대상으로 RAG 검색을 수행합니다.
    3. 최종적으로 JSON 형식의 3개 식당 상세 정보(추천 사유 포함)를 반환합니다.
    """
    # 1차 필터링: 카테고리 기준 식당 id와 운영시간 정보를 조회
    id_list = restaurant_filter.filter_ctgy(request.ctgy)
    open_restaurants = restaurant_filter.filter_business_hours(id_list)
    
    # 2차 필터링: 사용자가 입력한 세부사항(태그)를 기반으로 추가 필터링 수행
    expanded_query = restaurant_filter.regenerate_query(request.details)
    final_filtered_restaurant = restaurant_filter.filter_expanded_query(open_restaurants, expanded_query)
    
    # RAG 모듈 실행: allowed_ids (최종 필터링된 식당 id 리스트)를 대상으로 벡터 검색 및 추천 생성
    rag_result = rag_engine.run(request.details, final_filtered_restaurant)
    
    return {"result": rag_result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
