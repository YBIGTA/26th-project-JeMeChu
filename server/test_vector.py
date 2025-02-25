import os
from pinecone import Pinecone
import json
import numpy as np
from dotenv import load_dotenv


load_dotenv()

# ✅ Load API Key from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "embedding"  # Replace with your actual index name

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ Connect to existing index
index = pc.Index(INDEX_NAME)

# ✅ Example query vector (Use your actual query embedding)
query_embedding = np.random.rand(1536).tolist()  # Random vector for testing

# ✅ Search for top 5 similar vectors
results = index.query(vector=query_embedding, top_k=5, include_metadata=True)

# ✅ Print results
for match in results.matches:
    print(f"ID: {match.id}, Score: {match.score}, Metadata: {match.metadata}")