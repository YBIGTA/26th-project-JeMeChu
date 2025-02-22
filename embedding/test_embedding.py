from dotenv import load_dotenv
import openai
import pandas as pd
import os
import time
import ast
import json  # ✅ Fixes extra row issue

# ✅ Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Load CSV file
df = pd.read_csv("test_updated.csv")

# ✅ Columns to embed
columns_to_embed = ["description", "latest_reviews"]

# ✅ Function to get embedding for a single text
def get_embedding(text, max_tokens=8000):
    try:
        if not isinstance(text, str):  # ✅ Ensure text is a string
            raise ValueError("Input text must be a string.")
        if len(text.split()) > max_tokens:  # ✅ Truncate if too long
            text = " ".join(text.split()[:max_tokens])
        
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error: {e}")
        return None

# ✅ Function to get embeddings for a list of reviews (batch processing)
def get_embeddings_for_list(review_list):
    try:
        if not isinstance(review_list, list):  # ✅ Ensure input is a list
            raise ValueError("review_list must be a list.")

        # ✅ Convert all elements to strings & remove empty or invalid values
        review_list = [str(review).strip() for review in review_list if isinstance(review, (str, int, float)) and str(review).strip()]

        if len(review_list) == 0:  # ✅ Handle empty lists
            return None

        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=review_list  # ✅ Batch request (send all reviews at once)
        )
        return [embedding.embedding for embedding in response.data]  # ✅ Extract embeddings

    except Exception as e:
        print(f"Error: {e}")
        return None

# ✅ Process each column separately
for column in columns_to_embed:
    df[f"{column}_embedding"] = None  # ✅ Force column to exist
    embeddings_list = []

    for idx, row in df.iterrows():
        text = row[column]

        if pd.isna(text) or text == "":  # ✅ Handle missing or empty values
            embeddings_list.append(None)
            continue

        if column == "description":
            embedding = get_embedding(text)  # ✅ Single text embedding
        elif column == "latest_reviews":
            try:
                review_list = ast.literal_eval(text) if isinstance(text, str) else text
                if not isinstance(review_list, list):
                    raise ValueError("Invalid latest_reviews format")

                # ✅ Ensure all elements are properly formatted
                review_list = [str(review).strip() for review in review_list if isinstance(review, (str, int, float)) and str(review).strip()]
                
            except Exception as e:
                print(f"Skipping row {idx} due to error: {e}")
                embeddings_list.append(None)
                continue

            embedding = get_embeddings_for_list(review_list)  # ✅ Batch embedding

        embeddings_list.append(embedding)  # ✅ Store result

        if idx % 10 == 0:  # ✅ Print progress every 10 rows
            print(f"Processed {idx+1}/{len(df)} rows for column: {column}...")

        time.sleep(1)  # ✅ Prevent hitting OpenAI API rate limit

    # ✅ Assign embeddings to column
    df[f"{column}_embedding"] = embeddings_list

# ✅ Convert lists to JSON format before saving (Fixes extra row issue)
for column in columns_to_embed:
    df[f"{column}_embedding"] = df[f"{column}_embedding"].apply(
        lambda x: json.dumps(x) if isinstance(x, list) else ""
    )

# ✅ Save the new CSV file
df.to_csv("embedded_data.csv", index=False, encoding="utf-8-sig")
print("✅ CSV file saved: embedded_data.csv")