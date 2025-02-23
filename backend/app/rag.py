import os
import json
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv
import openai
import time
import pandas as pd
import ast
import math
import geocoder
import requests
from distance_utils import get_current_location, calculate_distance

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone
from sqlalchemy import create_engine
from langchain.schema import SystemMessage, HumanMessage

# .env 파일 로드 및 OpenAI API Key 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class RAGEngine:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.INDEX_NAME = "vectorspace"
        self.POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR")
        self.KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

        # Pinecone 클라이언트 초기화 및 인덱스 연결
        pc = Pinecone(api_key=self.PINECONE_API_KEY)
        self.index = pc.Index(self.INDEX_NAME)
        
        # DB 연결 (SQLAlchemy)
        self.restaurant_engine = create_engine(self.POSTGRES_CONN_STR)
        
        print("RAGEngine 초기화: Pinecone과 DB에 정상적으로 연결되었습니다.")
    
    def get_embedding(self, text):
        """텍스트 하나에 대한 임베딩을 생성합니다."""
        try:
            if not isinstance(text, str) or not text.strip():
                return None
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ 텍스트 임베딩 생성 오류: {e}")
            time.sleep(5)
            return None
    
    def reorder_business_hours(self, business_hours_str):
        """사업시간 문자열을 요일 순서대로 재정렬합니다."""
        day_order = {"월": 1, "화": 2, "수": 3, "목": 4, "금": 5, "토": 6, "일": 7}
        entries = [entry.strip() for entry in business_hours_str.split(";") if entry.strip()]
        sorted_entries = sorted(entries, key=lambda entry: day_order.get(entry.split(":")[0].strip(), 100))
        return "; ".join(sorted_entries)
    
    def transform_row(self, row):
        """DB에서 가져온 행의 business_hours를 재정렬하고 필요한 필드를 반환합니다."""
        if isinstance(row["business_hours"], str):
            bh = self.reorder_business_hours(row["business_hours"])
        else:
            bh = row["business_hours"]
        return {
            "id": row["id"],
            "name": row["name"],
            "photo_url": row["photo_url"],
            "phone": row["phone"],
            "business_hours": bh,
            "facilities": row["facilities"],
            "parking": row["parking"],
            "very_good": row["very_good"],
            "seat_info": row["seat_info"],
            "menu": row["menu"],
            "connect_url": row["connect_url"]
        }
    
    def run(self, query, allowed_ids):
        """
        1. 사용자 쿼리에 대한 임베딩을 생성하고,
        2. Pinecone 인덱스에서 allowed_ids에 해당하는 문서들만 대상으로 벡터 검색(top_k=10)을 수행합니다.
        3. 검색 결과를 바탕으로 각 식당의 리뷰를 그룹화하고 유사도 평균을 계산하여 상위 3개 식당을 선정합니다.
        4. 선정된 식당의 id를 이용해 DB에서 상세 정보를 가져오고,
        5. LLM을 통해 각 식당에 대한 추천 사유(reason)와 핵심(core)을 생성하여 최종 JSON 결과를 반환합니다.
        """
        # 사용자 쿼리 임베딩 생성
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return {"error": "임베딩 생성 실패"}
        
        print(f"임베딩 생성 완료, 벡터 길이: {len(query_embedding)}")

        # allowed_ids에 해당하는 문서만 검색 (Pinecone 메타데이터의 'id' 필드 사용)
        filter_dict = {"id": {"$in": allowed_ids}} if allowed_ids else None
        results = self.index.query(
            vector=query_embedding,
            top_k=10,
            include_metadata=True,
            filter=filter_dict
        )
        
        print(f"Pinecone 검색 완료, 매치 개수: {len(results.matches)}")

        # 검색 결과 처리: 각 식당의 리뷰 그룹화, 유사도 점수 누적 및 카운트
        restaurant_reviews = defaultdict(list)
        restaurant_scores = defaultdict(float)
        restaurant_counts = defaultdict(int)
        
        for match in results.matches:
            meta = match.metadata
            restaurant_name = meta.get("name")
            review_text = meta.get("text", "")
            restaurant_reviews[restaurant_name].append(review_text)
            restaurant_scores[restaurant_name] += match.score
            restaurant_counts[restaurant_name] += 1

        # 평균 유사도 계산 후 상위 3개 식당 선정
        restaurant_avg_scores = []
        for name, total_score in restaurant_scores.items():
            count = restaurant_counts[name]
            avg_score = total_score / count
            restaurant_avg_scores.append((name, avg_score))
        restaurant_avg_scores.sort(key=lambda x: x[1], reverse=True)
        top_3 = restaurant_avg_scores[:3]
        print(f"상위 3개 식당 (평균 점수 기준): {top_3}")

        # 추천 컨텍스트 포맷팅 (상위 3개 식당과 해당 리뷰 목록)
        recommendation_context = ""
        for idx, (name, avg_score) in enumerate(top_3, start=1):
            reviews = restaurant_reviews.get(name, [])
            reviews_text = "\n    - ".join(reviews) if reviews else "리뷰 없음"
            recommendation_context += (
                f"{idx}. 레스토랑: {name} (평균 유사도: {avg_score:.2f})\n"
                f"   리뷰:\n    - {reviews_text}\n\n"
            )
        
        print("추천 컨텍스트 생성 완료:")
        print(recommendation_context)

        # Pinecone 검색 결과에서 식당 이름과 id 매핑 (메타데이터의 'id' 사용)
        restaurant_id_by_name = {}
        for match in results.matches:
            meta = match.metadata
            restaurant_name = meta.get("name")
            restaurant_id = meta.get("id")
            if restaurant_name and restaurant_id and restaurant_name not in restaurant_id_by_name:
                restaurant_id_by_name[restaurant_name] = restaurant_id
        print("식당 이름 -> id 매핑 결과:")
        print(restaurant_id_by_name)

        # top_3 식당의 id 리스트 생성
        top3_ids = []
        for restaurant_name, _ in top_3:
            if restaurant_name in restaurant_id_by_name:
                top3_ids.append(restaurant_id_by_name[restaurant_name])
            else:
                print(f"Warning: {restaurant_name}에 해당하는 id 값을 찾을 수 없습니다.")
        print(f"선택된 상위 3개 식당 id 리스트: {top3_ids}")

        # DB에서 top3 식당의 상세 정보를 조회 (final 테이블)
        if top3_ids:
            sql_query = f"""
            SELECT id, photo_url, name, phone, business_hours, facilities, parking, very_good, seat_info, menu, connect_url
            FROM realfinal
            WHERE id IN ({','.join(map(str, top3_ids))})
            """
            db_details = pd.read_sql(sql_query, self.restaurant_engine)
        else:
            return {"error": "상위 식당 ID가 없습니다."}
        
        basic_info_list = [self.transform_row(row) for _, row in db_details.iterrows()]
        
        # 사용자의 현재 위치를 구하고 각 식당과의 거리를 계산
        user_lat, user_lon = get_current_location()
        for info in basic_info_list:
            restaurant_id = info.get("id")
            if restaurant_id:
                distance = calculate_distance(restaurant_id, user_lat, user_lon, self.POSTGRES_CONN_STR, self.KAKAO_API_KEY)
                info["distance"] = f"{distance:.2f} km" if distance is not None else "알 수 없음"
      
        # LLM 프롬프트 구성: 추천 사유와 핵심 단어를 JSON 배열로 생성하도록 요청
        system_message = SystemMessage(
            content=(
                "너는 JSON 배열 형식으로만 응답하는 AI 어시스턴트이고, 사용자의 쿼리와 리뷰를 비교해서 어떤 점이 유사해서 이 식당을 추천하는지 설명해주는 AI야."
                "출력은 오직 JSON 배열이어야 하며, 각 객체는 오직 'reason', 'core' 필드만 포함해야해. "
                "'reason'에서 설명할 때, 리뷰 문장을 그대로 가져와서 보여주며 유사성을 설명해야해."
                "'core'에는 유사성이 두드러지는 단어를 저장해줘."
                "실제 만나서 대화하는 것 처럼, 꼭 구어체로 말해주되 존댓말로 말해줘."
            )
        )
        human_message = HumanMessage(
            content=(
                f"사용자 쿼리: {query}\n\n"
                "추천된 레스토랑과 해당 리뷰 목록:\n"
                f"{recommendation_context}\n\n"
            )
        )
        rag_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4-turbo"
        )
        prompt_value = rag_prompt.format_prompt(query=query, recommendation_context=recommendation_context)
        messages = prompt_value.to_messages()

        print("LLM 프롬프트 메시지:")
        print(messages)

        final_reason_output = llm.invoke(messages)
        
        # LLM 응답은 [{"reason": "...", "core": "..."}, ...] 형태로 반환된다고 가정합니다.
        reasons_list = json.loads(final_reason_output.content)
        print("파싱된 추천 사유 리스트:")
        print(reasons_list)

        for i, info in enumerate(basic_info_list):
            try:
                info["reason"] = reasons_list[i]["reason"]
                info["core"] = reasons_list[i]["core"]
            except (IndexError, KeyError):
                info["reason"] = ""
                info["core"] = ""
        
        final_json_output = json.dumps(basic_info_list, ensure_ascii=False, indent=2)
        print(final_json_output)
        return final_json_output
