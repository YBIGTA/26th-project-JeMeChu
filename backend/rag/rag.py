# Cell 1: 라이브러리 임포트 및 환경 변수 로드
import os
import json
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv
import openai
import time
import pandas as pd
import ast

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone
from sqlalchemy import create_engine

# .env 파일 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 환경 변수 출력 (디버깅용)
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))
print("INDEX_NAME:", "vectorspace")

# Cell 2: OpenAI 임베딩 모델 생성 및 Pinecone 클라이언트 초기화, DB 연결결
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "vectorspace"
POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR")

# Pinecone 클라이언트 초기화 및 인덱스 연결
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# DB 연결
restaurant_engine = create_engine(POSTGRES_CONN_STR)

print("Embeddings와 Pinecone 클라이언트가 정상적으로 초기화되었으며 DB에 연결됐습니다.")

# Cell 3: 사용자 쿼리 및 해당 임베딩 생성
def get_embedding(text):
    """Fetch embedding for a single text."""
    try:
        if not isinstance(text, str) or not text.strip():
            return None  # ✅ Skip empty or non-string texts

        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding  # ✅ Extract the embedding

    except Exception as e:
        print(f"❌ Error processing text: {e}")
        time.sleep(5)  # ✅ Wait & retry on failure
        return None
    
query = "우리 프로젝트 마감 3일전이라 조뺑이 존나 치느라 개힘든데 저녁이라도 근사하게 먹고 싶거든? 기분이 좋아지고 든든한 한 끼 추천해줘."
query_embedding = get_embedding(query) # 텍스트를 벡터로 변환

print("사용자 쿼리:", query)
print("임베딩 벡터 길이:", len(query_embedding))

# Pinecone에서 벡터 검색
results = index.query(vector=query_embedding, top_k=10, include_metadata=True)
print("Pinecone 검색 완료, 반환된 매치 수:", len(results.matches))

# 실제 반환된 match의 정보를 확인
for i, match in enumerate(results.matches, start=1):
    print(f"\n=== Match {i} ===")
    print(f"Match ID: {match.id}")
    print(f"Score: {match.score}")

    # 메타데이터 확인
    print(f"Metadata: {match.metadata}")

# Cell 5: 검색 결과 처리
restaurant_reviews = defaultdict(list)
restaurant_scores = defaultdict(float)
restaurant_counts = defaultdict(int)

for match in results.matches:
    meta = match.metadata
    restaurant_name = meta.get("name")
    review_text = meta.get("text", "")
    
    # 해당 레스토랑의 리뷰 그룹화
    restaurant_reviews[restaurant_name].append(review_text)
    
    # 유사도 점수 누적
    restaurant_scores[restaurant_name] += match.score
    restaurant_counts[restaurant_name] += 1

print("검색 결과 처리 완료.")
print("레스토랑 이름 목록:", list(restaurant_reviews.keys()))


# Cell 6: 평균 유사도 계산 및 상위 3개 레스토랑 선정
restaurant_avg_scores = []
for name, total_score in restaurant_scores.items():
    count = restaurant_counts[name]
    avg_score = total_score / count
    restaurant_avg_scores.append((name, avg_score))

restaurant_avg_scores.sort(key=lambda x: x[1], reverse=True)
top_3 = restaurant_avg_scores[:3]

print("상위 3개 레스토랑 (이름, 평균 유사도):", top_3)

# Cell 7: 추천된 레스토랑 및 리뷰 문자열 포맷팅
recommendation_context = ""
for idx, (name, avg_score) in enumerate(top_3, start=1):
    reviews = restaurant_reviews.get(name, [])
    reviews_text = "\n    - ".join(reviews) if reviews else "리뷰 없음"
    recommendation_context += (
        f"{idx}. 레스토랑: {name} (평균 유사도: {avg_score:.2f})\n"
        f"   리뷰:\n    - {reviews_text}\n\n"
    )

print("포맷팅된 추천 및 리뷰 정보:\n")
print(recommendation_context)

# top3 id를 이용하여 DB에서 세부 사항 가져오기
restaurant_id_by_name = {}
for match in results.matches:
    meta = match.metadata
    restaurant_name = meta.get("name")
    restaurant_id = meta.get("id")  # Pinecone 메타데이터에 id 필드가 있다고 가정합니다.
    if restaurant_name and restaurant_id and restaurant_name not in restaurant_id_by_name:
        restaurant_id_by_name[restaurant_name] = restaurant_id

# top_3 리스트는 식당명으로 구성되어 있으므로, 이에 해당하는 id 값을 별도의 리스트로 생성합니다.
top3_ids = []
for restaurant_name, _ in top_3:
    if restaurant_name in restaurant_id_by_name:
        top3_ids.append(restaurant_id_by_name[restaurant_name])
    else:
        print(f"Warning: {restaurant_name}에 해당하는 id 값을 찾을 수 없습니다.")

# DB에서 reviews 테이블의 상세 정보를 가져옵니다.
if top3_ids:
    # SQL 쿼리 생성 (리뷰 테이블의 id 열과 Pinecone 메타데이터의 id가 일치하는 행만 조회)
    sql_query = f"""
    SELECT id, phone, business_hours, facilities, parking, very_good, seat_info, menu
    FROM final
    WHERE id IN ({','.join(map(str, top3_ids))})
    """
    db_details = pd.read_sql(sql_query, restaurant_engine)
else:
    print("top3_ids에 해당하는 값이 없습니다.")

# Cell 8: Output
from langchain.schema import SystemMessage, HumanMessage

def reorder_business_hours(business_hours_str):
    # 사업시간 문자열 예시: "화: 18:00 - 03:00; 수: 18:00 - 03:00; 목: 18:00 - 03:00; 금: 18:00 - 03:00; 토: 18:00 - 03:00; 일: 18:00 - 03:00; 월: 18:00 - 01:00"
    day_order = {"월": 1, "화": 2, "수": 3, "목": 4, "금": 5, "토": 6, "일": 7}
    entries = [entry.strip() for entry in business_hours_str.split(";") if entry.strip()]
    # 정렬: 각 항목의 앞부분에 있는 요일(한글 한 글자)을 기준으로 정렬
    sorted_entries = sorted(entries, key=lambda entry: day_order.get(entry.split(":")[0].strip(), 100))
    return "; ".join(sorted_entries)

def transform_row(row):
    # business_hours 재정렬
    if isinstance(row["business_hours"], str):
        bh = reorder_business_hours(row["business_hours"])
    else:
        bh = row["business_hours"]
    
    return {
        "phone": row["phone"],
        "business_hours": bh,
        "facilities": row["facilities"],
        "parking": row["parking"],
        "very_good": row["very_good"],
        "seat_info": row["seat_info"],
        "menu": row["menu"]
    }

# basic_info_list: reason 제외한 나머지 정보 리스트
basic_info_list = [transform_row(row) for _, row in db_details.iterrows()]

# 시스템 메시지: 출력은 JSON 배열이며, 각 객체는 오직 'reason' 필드만 포함해야 함
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
final_reason_output = llm.invoke(messages)

# LLM 응답은 [ {"reason": "..."}, {"reason": "..."}, {"reason": "..." } ] 형태라고 가정합니다.
reasons_list = json.loads(final_reason_output.content)

for i, info in enumerate(basic_info_list):
    try:
        info["reason"] = reasons_list[i]["reason"]
        info["core"] = reasons_list[i]["core"]
    except (IndexError, KeyError):
        info["reason"] = ""
        info["core"] = ""

# 최종 JSON 결과를 프론트엔드에 전달할 형태로 출력합니다.
final_json_output = json.dumps(basic_info_list, ensure_ascii=False, indent=2)
print(final_json_output)