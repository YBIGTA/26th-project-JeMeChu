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

# ✅ Set batch size
BATCH_SIZE = 30  # ✅ Adjusted batch size

# ✅ Checkpoint file
CHECKPOINT_FILE = "embedding_dropped_checkpoint.json"

# ✅ Load checkpoint if it exists
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        completed_rows = set(json.load(f))  # ✅ Set of completed row indices
else:
    completed_rows = set()

# ✅ Ensure "embedding" column exists
if "embedding" not in df.columns:
    df["embedding"] = None  # ✅ Create the column before processing


df["embedding"] = df["embedding"].astype(object)

# ✅ Function to get OpenAI embeddings in batches
def get_batch_embeddings(batch_texts):
    """Fetch embeddings for a batch of texts."""
    try:
        valid_texts = [text if isinstance(text, str) and text.strip() else "" for text in batch_texts]
        if not valid_texts:
            return [None] * len(batch_texts)

        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=valid_texts
        )
        embeddings = [item.embedding for item in response.data]

        # ✅ Ensure output matches input size
        return embeddings + [None] * (len(batch_texts) - len(embeddings))

    except Exception as e:
        print(f"❌ Error processing batch: {e}")
        time.sleep(5)  # ✅ Wait & retry on failure
        return [None] * len(batch_texts)

# ✅ Process embeddings in batches (Sequential)
for start_idx in tqdm(range(0, len(df), BATCH_SIZE), desc="Processing Batches"):
    if start_idx in completed_rows:  # ✅ Skip already processed batches
        continue

    batch_texts = df.loc[start_idx:start_idx + BATCH_SIZE - 1, "embedded"].tolist()
    embeddings = get_batch_embeddings(batch_texts)

    for i, emb in enumerate(embeddings):
        row_idx = start_idx + i
        if row_idx < len(df):  # ✅ Ensure within bounds
            df.at[row_idx, "embedding"] = emb
            completed_rows.add(row_idx)

    # ✅ Save progress every batch
    df.to_csv("embedded_data_dropped_temp.csv", index=False, encoding="utf-8-sig")
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(list(completed_rows), f)

    # ✅ Print progress
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    remaining = len(df) - len(completed_rows)
    print(f"[{timestamp}] ✅ Processed {len(completed_rows)}/{len(df)} rows... ({remaining} left)")

    time.sleep(2)  # ✅ Prevent hitting OpenAI rate limits

# ✅ Save final output
df.to_csv("embedded_dropped_data.csv", index=False, encoding="utf-8-sig")

# ✅ Remove checkpoint file after successful completion
if os.path.exists(CHECKPOINT_FILE):
    os.remove(CHECKPOINT_FILE)

print("\n✅ Embedding completed! Final CSV saved as: embedded_data.csv")