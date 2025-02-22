import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# ✅ Load Pinecone API Key from environment variable
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  

if not PINECONE_API_KEY:
    raise ValueError("Pinecone API Key not found. Make sure it's set in the environment.")

# ✅ Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ Define index parameters
INDEX_NAME = "embedding"

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME, 
        dimension=1536,  # Make sure this matches your embedding dimension
        metric="cosine",  # Choose "euclidean" or "dotproduct" if needed
        spec=ServerlessSpec(
            cloud="aws",  # Choose the correct cloud provider
            region=PINECONE_ENV  # Your region, e.g., "us-west4-gcp"
        )
    )

print(f"✅ Pinecone index '{INDEX_NAME}' is ready!")