from dotenv import load_dotenv
import openai
import pandas as pd
import os
import time
import json
from datetime import datetime
from tqdm import tqdm  # ✅ Progress Bar

# ✅ Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Load CSV file
df = pd.read_csv("dropped.csv")

# ✅ Checkpoint file
CHECKPOINT_FILE = "embedding_dropped_checkpoint.json"

# ✅ Load checkpoint if it exists
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        completed_rows = set(json.load(f))  # ✅ Set of completed row indices
else:
    completed_rows = set()

# ✅ Ensure "embedding" column exists and is of dtype=object
if "embedding" not in df.columns:
    df["embedding"] = None  # ✅ Create the column before processing

df["embedding"] = df["embedding"].astype(object)  # ✅ Ensures Pandas can store lists

# ✅ Function to get OpenAI embedding for a single text
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

# ✅ Process embeddings one by one (Sequential)
for row_idx in tqdm(range(len(df)), desc="Processing Rows"):
    if row_idx in completed_rows:  # ✅ Skip already processed rows
        continue

    text = df.at[row_idx, "embedded"]
    emb = get_embedding(text)

    df.at[row_idx, "embedding"] = emb  # ✅ Assign embedding safely
    completed_rows.add(row_idx)

    # ✅ Save progress every row
    if row_idx % 10 == 0:  # ✅ Save every 10 rows to prevent data loss
        df.to_csv("embedded_data_dropped_temp.csv", index=False, encoding="utf-8-sig")
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(list(completed_rows), f)

    # ✅ Print progress every 50 rows
    if row_idx % 50 == 0:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        remaining = len(df) - len(completed_rows)
        print(f"[{timestamp}] ✅ Processed {len(completed_rows)}/{len(df)} rows... ({remaining} left)")

    time.sleep(1)  # ✅ Prevent hitting OpenAI rate limits

# ✅ Save final output
df.to_csv("embedded_dropped_data.csv", index=False, encoding="utf-8-sig")

# ✅ Remove checkpoint file after successful completion
if os.path.exists(CHECKPOINT_FILE):
    os.remove(CHECKPOINT_FILE)

print("\n✅ Embedding completed! Final CSV saved as: embedded_dropped_data.csv")