import os
import uuid
import logging

logger = logging.getLogger(__name__)

# Singleton client instance
_client = None

# Placeholder import - will be implemented in next task
# from services.openrouter import get_embedding


async def get_embedding(text: str) -> list:
    """Placeholder - returns a zero vector. Will be replaced with real OpenRouter call."""
    logger.info(f"Would generate embedding for: {text[:50]}...")
    return [0.0] * 1536


def get_qdrant_client():
    """Returns a QdrantClient instance using QDRANT_URL from environment."""
    global _client
    
    if _client is not None:
        return _client
    
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        logger.error("qdrant-client library not installed. Run: pip install qdrant-client")
        raise
    
    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if qdrant_api_key:
        _client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    else:
        _client = QdrantClient(url=qdrant_url)
    
    return _client


async def search_memories(query: str, collections: list, limit: int = 3) -> list:
    """Search memories across multiple Qdrant collections."""
    try:
        # Generate embedding for query
        embedding = await get_embedding(query)
        
        client = get_qdrant_client()
        
        all_results = []
        
        for collection in collections:
            try:
                search_result = client.search(
                    collection_name=collection,
                    query_vector=embedding,
                    limit=limit
                )
                
                for result in search_result:
                    payload = result.payload
                    if payload and payload.get('text'):
                        all_results.append(payload.get('text'))
                        
            except Exception as e:
                logger.warning(f"Error searching collection {collection}: {e}")
        
        return all_results
        
    except Exception as e:
        logger.error(f"Error in search_memories: {e}")
        return []


async def upsert_memory(text: str, collection: str, metadata: dict = None) -> bool:
    """Upsert a memory to a Qdrant collection."""
    try:
        from qdrant_client.models import PointStruct
        
        # Generate embedding
        embedding = await get_embedding(text)
        
        # Create unique ID
        point_id = str(uuid.uuid4())
        
        # Build payload
        payload = {"text": text, "source": "companion"}
        if metadata:
            payload.update(metadata)
        
        # Create point
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload=payload
        )
        
        client = get_qdrant_client()
        
        client.upsert(
            collection_name=collection,
            points=[point]
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error in upsert_memory: {e}")
        return False