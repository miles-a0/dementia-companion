import httpx
from config import QDRANT_URL, N8N_URL, IMMICH_URL, VIKUNJA_URL
from qdrant_client import QdrantClient

qdrant_client = QdrantClient(url=QDRANT_URL)

async def search_memories(query: str, user_id: int, limit: int = 5):
    try:
        search_result = qdrant_client.search(
            collection_name=f"user_{user_id}_memories",
            query_vector=query,
            limit=limit
        )
        return [hit.payload for hit in search_result]
    except Exception as e:
        print(f"Qdrant search error: {e}")
        return []

async def trigger_n8n_workflow(workflow_id: str, data: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{N8N_URL}/webhook/{workflow_id}", json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"n8n trigger error: {e}")
            return False

async def get_immich_photos(album_id: str = None):
    headers = {"x-api-key": "dev-api-key"}
    async with httpx.AsyncClient() as client:
        try:
            if album_id:
                response = await client.get(f"{IMMICH_URL}/api/albums/{album_id}/assets", headers=headers)
            else:
                response = await client.get(f"{IMMICH_URL}/api/assets", headers=headers)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Immich API error: {e}")
            return []

async def get_vikunja_tasks():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{VIKUNJA_URL}/api/v1/tasks")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Vikunja API error: {e}")
            return []