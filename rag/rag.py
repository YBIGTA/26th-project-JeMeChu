# Cell 1: 라이브러리 임포트 및 환경 변수 로드
import os
import json
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv
import openai
import time

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone

# .env 파일 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 환경 변수 출력 (디버깅용)
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))
print("INDEX_NAME:", "vectorspace")

# Cell 2: OpenAI 임베딩 모델 생성 및 Pinecone 클라이언트 초기화
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "vectorspace"

# Pinecone 클라이언트 초기화 및 인덱스 연결
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

print("Embeddings와 Pinecone 클라이언트가 정상적으로 초기화되었습니다.")

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
    
query = "오뎅바에서 시원한 오뎅국물 마시고 오뎅 질겅질겅 씹으면서 사케로 입 씻고 싶다."
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
print("레스토랑 ID 목록:", list(restaurant_reviews.keys()))


# Cell 6: 평균 유사도 계산 및 상위 3개 레스토랑 선정
restaurant_avg_scores = []
for rid, total_score in restaurant_scores.items():
    count = restaurant_counts[rid]
    avg_score = total_score / count
    restaurant_avg_scores.append((rid, avg_score))

restaurant_avg_scores.sort(key=lambda x: x[1], reverse=True)
top_3 = restaurant_avg_scores[:3]

print("상위 3개 레스토랑 (ID, 평균 유사도):", top_3)

# Cell 7: 추천된 레스토랑 및 리뷰 문자열 포맷팅
recommendation_context = ""
for idx, (rid, avg_score) in enumerate(top_3, start=1):
    reviews = restaurant_reviews.get(rid, [])
    reviews_text = "\n    - ".join(reviews) if reviews else "리뷰 없음"
    recommendation_context += (
        f"{idx}. 레스토랑: {rid} (평균 유사도: {avg_score:.2f})\n"
        f"   리뷰:\n    - {reviews_text}\n\n"
    )

print("포맷팅된 추천 및 리뷰 정보:\n")
print(recommendation_context)

# Cell 8: Output
from langchain.schema import SystemMessage, HumanMessage

# 1) 메시지 객체 생성
system_message = SystemMessage(
    content="당신은 설명 가능한 AI 어시스턴트입니다. "
            "주어진 리뷰와 추천 정보를 기반으로, 사용자 쿼리에 맞는 "
            "레스토랑 추천과 그 이유를 상세하게 설명해 주세요."
)

human_message = HumanMessage(
    content=(
        f"사용자 쿼리: {query}\n\n"
        "추천된 레스토랑과 해당 리뷰 목록:\n"
        f"{recommendation_context}\n\n"
        "이 정보를 종합하여, 왜 이 레스토랑들이 추천되는지 구체적인 이유와 함께 답변해 주세요."
    )
)

# 2) ChatPromptTemplate 생성 (from_messages에 Message 객체 리스트)
rag_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

# 3) LLM 설정
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4-turbo"
)

# 4) PromptValue 포맷팅

prompt_value = rag_prompt.format_prompt(
    query=query,
    recommendation_context=recommendation_context
)

# 5) 최신 호출 방식: llm.invoke(...)
#    메시지 객체로 변환한 뒤 LLM 호출
messages = prompt_value.to_messages()
final_answer = llm.invoke(messages)

print("\n[최종 추천 및 설명 답변]")
print(final_answer.content)

