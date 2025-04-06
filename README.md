# 26th-project-JeMeChu
26기 신입기수 프로젝트 - 맞춤형 맛집 추천 서비스

---

## 요약

![1](images/1.png)
![2](images/2.png)
![3](images/3.png)
![4](images/4.png)
![5](images/5.png)

---

## 소개

사용자의 자연어 입력을 기반으로, 합정/서교동 지역 맛집 중 조건에 맞는 식당을 추천해주는 서비스입니다. \\
LangChain과 Pinecone을 활용한 RAG 파이프라인으로 동작하며, 식당 리뷰 데이터를 통해 추천 사유까지 자연어로 설명합니다.

---

## 전체 파이프라인

1. **합정/서교동 공공 식당 데이터 인덱싱**
2. **네이버 지도 크롤링 → 리뷰 수집**
3. **전처리 및 필터링 (카테고리, 영업시간 등)** → PostgreSQL 저장
4. **GPT-4o mini를 활용한 사용자 세부 조건 파싱 (JSON 반환)**
5. **PostgreSQL에서 조건 기반 필터링**
6. **Pinecone에서 리뷰 임베딩 유사도 기반 검색 (top 3)**
7. **LangChain으로 추천 사유 생성**
8. **Next.js 프론트에서 결과 출력**

---

## 기술 스택
```
| 파트        | 기술                    |
|-------------|-------------------------|
| 프론트엔드   | Next.js, Tailwind, TypeScript |
| 백엔드       | FastAPI, LangChain, Pinecone |
| 임베딩       | OpenAI embedding          |
| DB           | PostgreSQL              |
| LLM 활용      | OpenAI GPT-4o mini       |
```
---

## Repository 구조
```
├── .gitignore                     # Git에서 제외할 파일 목록
├── README.md                     # 프로젝트 소개 문서

├── backend/                      # 백엔드 코드 및 관련 설정
│   ├── .dockerignore            # 도커 빌드시 제외할 항목
│   ├── Constants.py             # 프로젝트 공통 상수
│   ├── Dockerfile               # Docker 이미지 설정 파일
│   ├── requirements.txt         # 백엔드 파이썬 패키지 의존성
│   └── app/                     # 백엔드 실제 애플리케이션 코드
│       ├── database.py
│       ├── distance_utils.py
│       ├── main.py
│       ├── rag.py
│       ├── restaurant_filter.py
│       ├── test_db.ipynb
│       └── __init__.py

├── database/                    # 전처리된 데이터 및 CSV 파일 모음
│   ├── dropped.csv
│   ├── embedded_dropped_data.csv
│   ├── final_link_sql.csv
│   ├── final_sql.csv
│   ├── final_updated.csv
│   ├── frequency_test_adj_df.csv
│   ├── idwithreview.csv
│   ├── link_url.csv
│   ├── menu_updated.csv
│   ├── naver_data.csv
│   ├── photo.csv
│   ├── photo_url.csv
│   ├── preprocessed_naver.csv
│   ├── pre_embedding.csv
│   ├── pre_embedding_ready.csv
│   ├── price.csv
│   ├── restaurant_df.csv
│   ├── restaurant_final.csv
│   ├── restaurant_temp.csv
│   ├── reviews_naver.csv
│   ├── scraper_price_exception.csv
│   ├── SQL_DB.csv
│   ├── SQL_DB_check.csv
│   ├── SQL_DB_updated.csv
│   ├── test.csv
│   ├── test_updated.csv
│   └── updated_naver_map_data.csv

├── embedding/                   # 임베딩 처리 코드
│   ├── embedding.py
│   ├── embedding_onebyone.py
│   └── test/                    # 테스트용 임베딩 노트북/스크립트
│       ├── embedding_test.ipynb
│       ├── testfile_maker.ipynb
│       └── test_embedding.py

├── frontend/                    # 프론트엔드 React 기반 앱 (Next.js)
│   ├── .gitignore
│   ├── basic_image.png
│   ├── eslint.config.mjs
│   ├── logo.png
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── app/                     # 페이지 및 스타일 구성
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── recommendations/
│   │   │   └── page.tsx
│   │   └── utils/
│   │       ├── highlightCore.tsx
│   │       ├── parseRestaurantData.ts
│   │       └── types.ts
│   ├── components/              # UI 컴포넌트
│   │   └── Sidebar.tsx
│   └── public/                  # 정적 자산
│       ├── file.svg
│       ├── globe.svg
│       ├── next.svg
│       ├── vercel.svg
│       ├── window.svg
│       ├── assets/
│       │   └── cursor.svg
│       └── fonts/
│           ├── GmarketSansTTFBold.ttf
│           ├── GmarketSansTTFLight.ttf
│           └── GmarketSansTTFMedium.ttf

├── images/                      # 이미지 파일들
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   └── 5.png

├── review_analysis/            # 리뷰 분석 관련 코드
│   ├── __init__.py
│   ├── crawling/               # 네이버 리뷰 크롤링 스크립트
│   │   ├── eda_restaurant.py
│   │   ├── scraper_naver.py
│   │   ├── scraper_photo_naver.py
│   │   ├── scraper_price.py
│   │   ├── scraper_price_exception.py
│   │   └── scraper_url_naver.py
│   ├── preprocessing/          # 리뷰 전처리 코드
│   │   ├── base_processor.py
│   │   ├── extra_preprocessing.ipynb
│   │   ├── main.py
│   │   ├── NaverProcessor.py
│   │   └── __init__.py
│   └── test/                   # 실험 및 분석 노트북
│       ├── analysis_restaurant.ipynb
│       ├── before_scraping.ipynb
│       ├── CheckforDetail.ipynb
│       ├── eda_restaurant.ipynb
│       ├── final_file_merging.ipynb
│       ├── frequency_test.ipynb
│       ├── frequency_test.png
│       ├── frequency_test_adj.png
│       ├── frequency_test_adj_nonoutlier.png
│       ├── frequency_test_df.csv
│       ├── MergeDetail.ipynb
│       ├── MergeDetail.R
│       ├── merge_url.ipynb
│       ├── quick_adjustment.ipynb
│       ├── scraper_price_exception.ipynb
│       ├── test.ipynb
│       ├── text_counter.ipynb
│       ├── unique_features.txt
│       └── visualize_frequency.R

├── server/                      # 파인콘 벡터 DB 연동 및 관련 스크립트
│   ├── DB_UPDATE.ipynb
│   ├── from pinecone import Pinecone.py
│   ├── id_mapping.ipynb
│   ├── pinecone_setup.py
│   ├── test_db_connect.py
│   ├── test_filtering.ipynb
│   ├── test_vector.py
│   ├── upload_sql.py
│   └── upload_vector.py

└── translate/                   # 번역 및 문장 분할 관련 노트북
    ├── converted_test.txt
    ├── divide_sentence.ipynb
    ├── preprocessed_naver.csv
    ├── test.txt
    └── translate_test.ipynb
```
## TEAM 

<img src="https://github.com/Mookjsi.png" width="30"/> [강정묵](https://github.com/Mookjsi)
<img src="https://github.com/yunbeeee.png" width="30"/> [엄윤희](https://github.com/yunbeeee)
이경민
<img src="https://github.com/sleepylee02.png" width="30"/> [이재영](https://github.com/sleepylee02)
<img src="https://github.com/mjxjung.png" width="30"/> [정민지](https://github.com/mjxjung)
