import os
import re
import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from routers.auth import get_current_carer
from services.qdrant_client import upsert_memory

logger = logging.getLogger(__name__)
router = APIRouter(tags=["memories"])

VALID_COLLECTIONS = [
    "life_stories", 
    "family", 
    "merchant_navy", 
    "jokes", 
    "routines", 
    "medication", 
    "places", 
    "preferences"
]

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")


def get_db_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        return None
    try:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        return None


def split_into_chunks(text: str) -> list:
    """Split text into chunks by sentence boundary"""
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if not sentence.strip():
            continue
        
        if current_chunk:
            test_chunk = current_chunk + " " + sentence
        else:
            test_chunk = sentence
        
        if len(test_chunk) <= 500:
            current_chunk = test_chunk
        else:
            if current_chunk and len(current_chunk) >= 20:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk and len(current_chunk) >= 20:
        chunks.append(current_chunk.strip())
    
    final_chunks = []
    temp_chunk = ""
    for chunk in chunks:
        if temp_chunk:
            test = temp_chunk + ". " + chunk
            if len(test) <= 500:
                temp_chunk = test
            else:
                if len(temp_chunk) >= 20:
                    final_chunks.append(temp_chunk)
                temp_chunk = chunk
        else:
            temp_chunk = chunk
    
    if temp_chunk and len(temp_chunk) >= 20:
        final_chunks.append(temp_chunk)
    
    return final_chunks if final_chunks else chunks


@router.post("/carer/memories/upload")
async def upload_memory(
    text: str = Body(...),
    collection: str = Body(...),
    metadata: dict = Body(default={}),
    source: str = Body(default="carer_upload"),
    carrier: dict = Depends(get_current_carer)
):
    """Upload memory text to Qdrant vector store"""
    
    if collection not in VALID_COLLECTIONS:
        return HTTPException(
            status_code=400, 
            detail="Invalid collection. Must be one of: " + ", ".join(VALID_COLLECTIONS)
        )
    
    if not text or len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Text must be at least 20 characters")
    
    chunks = split_into_chunks(text)
    
    metadata_with_source = {**metadata, "source": source}
    
    for chunk in chunks:
        try:
            await upsert_memory(chunk, collection, metadata_with_source)
        except Exception as e:
            logger.error(f"Error upserting chunk: {e}")
            raise HTTPException(status_code=500, detail="Failed to store memory")
    
    return {
        "stored": True, 
        "chunks": len(chunks), 
        "collection": collection
    }


@router.get("/carer/log")
async def get_carer_log(
    user_id: int = Query(default=1),
    limit: int = Query(default=50),
    carrier: dict = Depends(get_current_carer)
):
    """Get intervention log from Postgres"""
    
    conn = get_db_connection()
    if not conn:
        return {"log": [], "error": "Database not configured"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT triggered_at, trigger_type, message_sent, duration_seconds
            FROM intervention_log
            WHERE user_id = %s
            ORDER BY triggered_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        
        log_entries = []
        for row in rows:
            log_entries.append({
                "triggered_at": row[0].isoformat() if row[0] else None,
                "trigger_type": row[1],
                "message_sent": row[2],
                "duration_seconds": row[3]
            })
        
        cursor.close()
        conn.close()
        return {"log": log_entries}
    
    except Exception as e:
        logger.error(f"Error fetching log: {e}")
        if conn:
            conn.close()
        return {"log": [], "error": str(e)}


@router.get("/carer/collections")
async def get_collections(carrier: dict = Depends(get_current_carer)):
    """Get list of Qdrant collections with item counts"""
    
    collections_list = []
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for collection_name in VALID_COLLECTIONS:
                try:
                    response = await client.get(
                        "{}/collections/{}".format(QDRANT_URL, collection_name)
                    )
                    if response.status_code == 200:
                        data = response.json()
                        points_count = data.get("result", {}).get("points_count", 0)
                        collections_list.append({
                            "name": collection_name,
                            "count": points_count
                        })
                    else:
                        collections_list.append({
                            "name": collection_name,
                            "count": 0
                        })
                except Exception:
                    collections_list.append({
                        "name": collection_name,
                        "count": 0
                    })
    
    except Exception as e:
        logger.error(f"Error fetching collections: {e}")
    
    return {"collections": collections_list}