import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTIONS = [
    "life_stories",
    "family",
    "merchant_navy",
    "jokes",
    "routines",
    "medication",
    "places",
    "preferences",
]

def main():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    existing = [c.name for c in client.get_collections().collections]
    
    for name in COLLECTIONS:
        if name in existing:
            print(f"Collection '{name}' already exists, skipping.")
            continue
        
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
            ),
            on_disk_payload=True,
        )
        print(f"Created collection '{name}'.")
    
    print("Done.")

if __name__ == "__main__":
    main()