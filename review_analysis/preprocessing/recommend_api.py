from fastapi import FastAPI
import pandas as pd
import os
from Constants import DATABASE_PATH

app = FastAPI()

### CSV 파일 로드
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
# DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "database"))

file_path = os.path.abspath(os.path.join(DATABASE_PATH, "final_recommendations.csv")) # str임
# 파일 로드
df = pd.read_csv(file_path)


@app.get("/recommend")
def recommend_restaurants(n: int = 10, space_feature: str = None):
    if space_feature:
        filtered_df = df[df["공간적 특징"].apply(lambda x: space_feature in x)]
    else:
        filtered_df = df

    top_restaurants = filtered_df.sort_values("final_score", ascending=False).head(n)
    return top_restaurants[["사업장명", "final_score", "공간적 특징", "유사 공간 특징 맛집"]].to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
