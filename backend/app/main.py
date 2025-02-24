# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from app.restaurant_filter import RestaurantFilter
from app.rag import RAGEngine
import json
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

restaurant_filter = RestaurantFilter()
rag_engine = RAGEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class FilterRequest(BaseModel):
    ctgy: str
    details: str

@app.post("/filter_restaurants/")
async def filter_restaurants(request: FilterRequest):
    # 1차 - category
    id_list = restaurant_filter.filter_ctgy(request.ctgy)
    # 2차 - open now?
    open_restaurants = restaurant_filter.filter_business_hours(id_list)
    # 3차 - expand query => filter by tags
    expanded_query = restaurant_filter.regenerate_query(request.details)
    final_filtered_restaurant = restaurant_filter.filter_expanded_query(open_restaurants, expanded_query)
    # 4 - RAG
    rag_result = rag_engine.run(request.details, final_filtered_restaurant)
    return rag_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)