import os
import pandas as pd
import pinecone
from tqdm import tqdm
import json
import hashlib
from dotenv import load_dotenv


load_dotenv()

# ✅ Load API Key and Environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  
INDEX_NAME = "vectorspace"  # Change this if your index name is different

# ✅ Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ✅ Load Large CSV in Chunks
CHUNK_SIZE = 100  # Adjust batch size based on your needs
csv_file = "embedded_withname.csv"  # Change to your actual file name

# ✅ Read CSV in chunks
for chunk in tqdm(pd.read_csv(csv_file, chunksize=CHUNK_SIZE), desc="Uploading Data"):
    vectors = []

    for idx, row in chunk.iterrows():
        if isinstance(row["embedding"], str):  # ✅ Ensure valid embedding
            embedding = json.loads(row["embedding"])  # Convert string to list

            # ✅ Generate a Unique ID (Hash-based)
            unique_id = hashlib.md5(f"{row['id']}_{idx}".encode()).hexdigest()

            # ✅ Store the original `id` as metadata
            metadata = {
                "id": row["id"],
                "text": row["embedded"] if pd.notna(row["embedded"]) else "",
                "name": row["name"] if pd.notna(row["name"]) else ""
                }

            vectors.append((unique_id, embedding, metadata))

    # ✅ Upsert into Pinecone
    index.upsert(vectors)

print("✅ Data successfully uploaded to Pinecone!")