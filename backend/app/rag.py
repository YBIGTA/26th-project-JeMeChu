# rag.py
import os
import json
from collections import defaultdict
from dotenv import load_dotenv
import openai
import time
import pandas as pd
from app.database import engine

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone
from langchain.schema import SystemMessage, HumanMessage

from app.distance_utils import get_current_location, calculate_distance
from app.database import SessionLocal, RealFinal  # <--- ensure this is correct
from fastapi.responses import JSONResponse

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.INDEX_NAME = "vectorspace"
        self.POSTGRES_CONN_STR = os.getenv("DB_URL")
        self.KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

        pc = Pinecone(api_key=self.PINECONE_API_KEY)
        self.index = pc.Index(self.INDEX_NAME)
        self.restaurant_engine = engine
        print("RAGEngine 초기화 완료")

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
            print(f"텍스트 임베딩 생성 오류: {e}")
            time.sleep(5)
            return None

    def reorder_business_hours(self, business_hours_str):
        """사업시간 문자열을 요일 순서대로 재정렬합니다."""
        day_order = {"월": 1, "화": 2, "수": 3, "목": 4, "금": 5, "토": 6, "일": 7}
        entries = [entry.strip() for entry in business_hours_str.split(";") if entry.strip()]
        sorted_entries = sorted(entries, key=lambda entry: day_order.get(entry.split(":")[0].strip(), 100))
        return "; ".join(sorted_entries)

    def transform_row(self, row):
        if isinstance(row.business_hours, str):
            bh = self.reorder_business_hours(row.business_hours)
        else:
            bh = row.business_hours

        name = str(row["name"]) if not isinstance(row["name"], str) else row["name"]

        return {
            "id": row.id,
            "name": name,
            "photo_url": row.photo_url,
            "phone": row.phone,
            "business_hours": bh,
            "facilities": row.facilities,
            "parking": row.parking,
            "very_good": row.very_good,
            "seat_info": row.seat_info,
            "menu": row.menu,
            "connect_url": row.connect_url
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
        restaurant_id_by_name = {}  # ✅ 이름을 키로 ID 저장
        
        # restaurant_info = defaultdict(lambda: {"id": None, "reviews": [], "score": 0.0, "count": 0})

        for match in results.matches:
            meta = match.metadata
            restaurant_name = meta.get("name")
            restaurant_id = meta.get("id")  # ✅ 식당 ID 가져오기
            review_text = meta.get("text", "")

            restaurant_reviews[restaurant_name].append(review_text)
            restaurant_scores[restaurant_name] += match.score
            restaurant_counts[restaurant_name] += 1

            # if restaurant_name:
            #     restaurant_info[restaurant_name]["id"] = restaurant_id  # ✅ ID 저장
            #     restaurant_info[restaurant_name]["reviews"].append(review_text)
            #     restaurant_info[restaurant_name]["score"] += match.score
            #     restaurant_info[restaurant_name]["count"] += 1  # ✅ 리뷰 개수 증가
            # ✅ ID는 처음 추가될 때만 저장 (중복 방지)
            if restaurant_name not in restaurant_id_by_name:
                restaurant_id_by_name[restaurant_name] = restaurant_id

        # ✅ 결과 확인
        print("📌 식당 ID 매핑 완료:", restaurant_id_by_name)
        print("📌 리뷰 데이터 확인:", restaurant_reviews)
        print("📌 점수 데이터 확인:", restaurant_scores)
        print("📌 카운트 데이터 확인:", restaurant_counts)
        print(restaurant_name)
        # 평균 유사도 계산 후 상위 3개 식당 선정
        restaurant_avg_scores = []
        
        for name, total_score in restaurant_scores.items():
            count = restaurant_counts[name]
            if count > 0:  # ✅ 리뷰 개수가 있는 경우만 고려
                avg_score = total_score / count
                restaurant_id = restaurant_id_by_name.get(name, "알 수 없음")  # ✅ ID 매핑
                restaurant_avg_scores.append((name, avg_score, restaurant_id))  # ✅ ID 포함

        # ✅ 유사도 기준으로 정렬 (내림차순)
        restaurant_avg_scores.sort(key=lambda x: x[1], reverse=True)

        # ✅ 상위 3개 식당 선택 (ID 포함)
        top_3 = restaurant_avg_scores[:3]

        print(f"✅ 상위 3개 식당 (평균 점수 기준, ID 포함): {top_3}")
        # for name, data in restaurant_info.items():
        #     if data["count"] > 0:  # ✅ 리뷰 개수가 있는 경우만 고려
        #         avg_score = data["score"] / data["count"]
        #         restaurant_avg_scores.append((name, avg_score, data["id"]))  # ✅ ID 추가

        # # ✅ 유사도 기준으로 정렬 (내림차순)
        # restaurant_avg_scores.sort(key=lambda x: x[1], reverse=True)

        # # ✅ 상위 3개 식당 선택 (ID 포함)
        # top_3 = restaurant_avg_scores[:3]

        # print(f"✅ 상위 3개 식당 (평균 점수 기준, ID 포함): {top_3}")
        
        # for name, total_score in restaurant_scores.items():
        #     count = restaurant_counts[name]
        #     avg_score = total_score / count
        #     restaurant_avg_scores.append((name, avg_score))
        # restaurant_avg_scores.sort(key=lambda x: x[1], reverse=True)
        # top_3 = restaurant_avg_scores[:3]
        # print(f"상위 3개 식당 (평균 점수 기준): {top_3}")

        # 추천 컨텍스트 포맷팅 (상위 3개 식당과 해당 리뷰 목록)
        # recommendation_context = ""
        # for idx, (name, avg_score) in enumerate(top_3, start=1):
        #     reviews = restaurant_reviews.get(name, [])
        #     reviews_text = "\n    - ".join(reviews) if reviews else "리뷰 없음"
        #     recommendation_context += (
        #         f"{idx}. 레스토랑: {name} (평균 유사도: {avg_score:.2f})\n"
        #         f"   리뷰:\n    - {reviews_text}\n\n"
        #     )
        
        # print("추천 컨텍스트 생성 완료:")
        # print(recommendation_context)

        
        # ✅ 추천 컨텍스트 포맷팅 (상위 3개 식당과 해당 리뷰 목록)
        recommendation_context = ""

        for idx, (name, avg_score, restaurant_id) in enumerate(top_3, start=1):
            reviews = restaurant_reviews.get(name, [])
            reviews_text = "\n    - ".join(reviews) if reviews else "리뷰 없음"

            recommendation_context += (
                f"{idx}. 레스토랑: {name} (ID: {restaurant_id}, 평균 유사도: {avg_score:.2f})\n"
                f"   리뷰:\n    - {reviews_text}\n\n"
            )

        print("✅ 추천 컨텍스트 생성 완료:")
        print(recommendation_context)

        # # ✅ 추천 컨텍스트 포맷팅 (상위 3개 식당과 해당 리뷰 목록)
        # recommendation_context = ""
        # restaurant_id_by_name = {name: rid for name, _, rid in top_3}  # ✅ 이름 -> ID 매핑

        # for idx, (name, avg_score, restaurant_id) in enumerate(top_3, start=1):
        #     reviews = restaurant_reviews.get(name, [])
        #     reviews_text = "\n    - ".join(reviews) if reviews else "리뷰 없음"

        #     recommendation_context += (
        #         f"{idx}. 레스토랑: {name} (ID: {restaurant_id}, 평균 유사도: {avg_score:.2f})\n"
        #         f"   리뷰:\n    - {reviews_text}\n\n"
        #     )

        # print("✅ 추천 컨텍스트 생성 완료:")
        # print(recommendation_context)



        # Pinecone 검색 결과에서 식당 이름과 id 매핑 (메타데이터의 'id' 사용)
        restaurant_id_by_name = {}
        for match in results.matches:
            meta = match.metadata
            restaurant_name = meta.get("name")
            restaurant_id = meta.get("id")
            if restaurant_name and restaurant_id and restaurant_name not in restaurant_id_by_name:
                restaurant_id_by_name[restaurant_name] = restaurant_id
        print("식당 이름 -> id 매핑 결과:")
        print(restaurant_id_by_name, "\n")

        # ✅ top_3을 올바르게 언패킹해서 ID까지 활용
        top3_ids = []
        for restaurant_name, _, restaurant_id in top_3:
            if restaurant_name in restaurant_id_by_name:
                top3_ids.append(restaurant_id)  # ✅ 올바르게 ID를 저장
            else:
                print(f"Warning: {restaurant_name}에 해당하는 ID 값을 찾을 수 없습니다.")


        # DB에서 top3 식당의 상세 정보를 조회 (final 테이블)
        if top3_ids:
            sql_query = f"""
            SELECT id, name, photo_url, phone, business_hours, facilities, parking, very_good, seat_info, menu, connect_url
            FROM realfinal
            WHERE id IN ({','.join(map(str, top3_ids))})
            """
            db_details = pd.read_sql(sql_query, self.restaurant_engine)
        else:
            return {"error": "상위 식당 ID가 없습니다."}
        
        # 

        basic_info_list = [self.transform_row(row) for _, row in db_details.iterrows()]
        # 사용자의 현재 위치를 구하고 각 식당과의 거리를 계산
        user_lat, user_lon = get_current_location()
        for info in basic_info_list:
            restaurant_id = info.get("id")
            if restaurant_id:
                distance = calculate_distance(restaurant_id, user_lat, user_lon, self.POSTGRES_CONN_STR, self.KAKAO_API_KEY)
                info["distance"] = f"{distance:.2f} km" if distance is not None else "알 수 없음"
      
        # LLM 프롬프트 구성: 추천 사유와 핵심 단어를 JSON 배열로 생성하도록 요청
        # "너는 JSON 배열 형식으로만 응답하는 AI 어시스턴트야. 사용자의 요청과 식당 리뷰를 비교해서, 왜 이 식당이 추천되는지 자연스럽게 설명해줘. "
        #         "출력은 오직 JSON 배열이며, 각 객체는 'reason'과 'core' 필드만 포함해야 해. "
        #         "'reason' 필드에서는 친근한 말투로, 마치 사람이 설명하듯이 자연스럽게 이유를 알려줘야 해. "
        #         "리뷰에 있는 문장을 그대로 복붙하지 말고, 요약하거나 문맥에 맞게 다듬어서 매끄럽게 설명해. "
        #         "또한, 'core' 필드에는 유사성이 두드러지는 키워드를 저장해줘. "
        #         "만약 부정적인 리뷰가 포함되어 있다면, 단점을 솔직하게 언급하되, 대안을 함께 제시해줘. "
        #         "반드시 **구어체**로 설명하고, 존댓말을 사용해줘."
        
                # "출력은 오직 JSON 배열이며, 객체에는 반드시 'id', 'reason', 'core' 필드만 포함해야 해. "
                # "**각 객체는 반드시 서로 다른 3개의 식당을 포함해야 하며, 리뷰 개수와 상관없이 항상 3개의 추천 이유를 생성해야 해!**\n\n"
                
                # "각 'reason'은 반드시 해당 식당의 실제 리뷰를 바탕으로 작성해야 해. "
                
                # "**출력 형식 예시:**\n"
                # "[\n"
                # "  {\"id\": 123, \"reason\": \"이곳은 주차 공간이 넉넉해서 차를 가져오기에 좋아요!\", \"core\": \"주차 가능, 넓은 공간\"},\n"
                # "  {\"id\": 456, \"reason\": \"깔끔한 인테리어와 조용한 분위기로 대화하기 좋은 곳이에요.\", \"core\": \"깔끔한 인테리어, 조용한 분위기\"},\n"
                # "  {\"id\": 789, \"reason\": \"다양한 안주가 맛있어서 모임에 추천드려요.\", \"core\": \"다양한 안주, 분위기 좋음\"}\n"
                # "]\n\n"

                # "**✅ 중요한 규칙:**\n"
                # "1. **반드시 3개의 JSON 객체를 생성해야 해.**\n"
                # "2. **각 객체에는 'id', 'reason', 'core'를 포함해야 해.**\n"
                # "3. **3개 미만으로 응답하면 잘못된 응답이므로 다시 생성해야 해.**\n"
                # "4. **리뷰 개수와 상관없이 항상 3개의 식당이 있어야 해.**\n"
                # "5. **'reason' 필드에서는 자연스럽고 친근한 말투로 설명해야 해.**\n"
                # "6. **'core' 필드에는 해당 식당을 대표하는 키워드(2~3개)를 넣어야 해.**\n"
                # "7. **만약 부정적인 리뷰가 있다면, 단점을 솔직하게 언급하되 대안을 함께 제시해야 해.**\n"
                # "8. **각 식당의 id가 정확히 매칭되었는지 점검해야 해. (예: 향남추어탕 밑에 향원정에 대한 설명을 쓰면 안 됨!)**\n"

        system_message = SystemMessage(
            content=(
            "너는 JSON 배열 형식으로만 응답하는 AI 어시스턴트야. 사용자의 요청과 식당 리뷰를 비교해서, 왜 이 식당이 추천되는지 자연스럽게 설명해줘. "
            "출력은 오직 JSON 배열이며, 각 객체는 'reason'과 'core' 필드만 포함해야 해. "
            "'reason' 필드에서는 친근한 말투로, 마치 사람이 설명하듯이 자연스럽게 이유를 알려줘야 해. "
            "해당 식당의 실제 리뷰를 바탕으로 하되 리뷰에 있는 문장을 그대로 직접 인용해줘."
            "또한, 'core' 필드에는 유사성이 두드러지는 키워드를 저장해줘. "
            "만약 부정적인 리뷰가 포함되어 있다면, 단점을 솔직하게 언급하되, 대안을 함께 제시해줘. "
            "반드시 **구어체**로 설명하고, 존댓말을 사용해줘."
            )
        )

        human_message = HumanMessage(
            content=(
                f"사용자 쿼리: {query}\n\n"
                "추천된 레스토랑과 해당 리뷰 목록:\n"
                f"{recommendation_context}\n\n"
                "**각 레스토랑이 왜 추천되었는지 3개의 JSON 객체로 설명해줘.** "
                "하지만 너무 딱딱한 설명이 아니라, 사람들이 자연스럽게 말하는 방식으로 전달해줘!"
                "각 객체에는 'id', 'reason', 'core'를 포함해야 하며, 반드시 3개의 식당을 포함해야 해."
                "반드시 3개를 생성하지 않으면 오류이므로 다시 생성해야 해!"
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
        print(messages, "\n")

        final_reason_output = llm.invoke(messages)
        
        # LLM 응답은 [{"reason": "...", "core": "..."}, ...] 형태로 반환된다고 가정합니다.
        reasons_list = json.loads(final_reason_output.content)
        print("파싱된 추천 사유 리스트:")
        print(reasons_list, "\n")

        # for i, info in enumerate(basic_info_list):
        #     print("i:",i)
        #     try:
        #         info["reason"] = reasons_list[i]["reason"]
        #         info["core"] = reasons_list[i]["core"]
        #     except (IndexError, KeyError):
        #         info["reason"] = ""
        #         info["core"] = ""
        # # print(f"basic_info_list(거리계산 후): {basic_info_list}\n")
        # return JSONResponse(content=basic_info_list)

        # ✅ 1. reasons_list를 ID 기반 딕셔너리로 변환
        reasons_dict = {int(item["id"]): {"reason": item["reason"], "core": item["core"]} for item in reasons_list}

        # ✅ 2. 기본 정보 리스트에서 ID 기준으로 reason/core 추가
        for info in basic_info_list:
            restaurant_id = int(info["id"])  # ID를 정수형으로 변환
            if restaurant_id in reasons_dict:
                info["reason"] = reasons_dict[restaurant_id]["reason"]
                info["core"] = reasons_dict[restaurant_id]["core"]
            else:
                info["reason"] = "추천 이유 없음"
                info["core"] = "정보 없음"

        # ✅ 최종 JSON 응답 반환
        print(json.dumps(basic_info_list, indent=4, ensure_ascii=False))
        return JSONResponse(content=basic_info_list)


