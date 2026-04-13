import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Body

# Placeholder imports - will be implemented in next tasks
# from services.qdrant_client import search_memories
# from services.openrouter import get_ai_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["messages"])

DATABASE_URL = os.getenv("DATABASE_URL")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")


async def search_memories(query: str, collections: list, limit: int = 3):
    """Placeholder - will be implemented in next task"""
    # TODO: Implement actual Qdrant search
    logger.info(f"Would search Qdrant for: {query} in collections: {collections}")
    return []


async def get_ai_response(system_prompt: str, user_message: str):
    """Placeholder - will be implemented in next task"""
    # TODO: Implement actual OpenRouter API call
    logger.info(f"Would call OpenRouter with prompt: {user_message}")
    return "I'm here to help you, John."


async def get_db_connection():
    """Get async database connection"""
    try:
        import asyncpg
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.warning(f"Database not configured: {e}")
        return None


@router.post("/messages/respond")
async def respond_to_message(
    text: str = Body(...),
    user_id: int = Body(default=1),
    conversation_id: Optional[int] = Body(default=None)
):
    try:
        # a. Search Qdrant for relevant memories
        collections = ["life_stories", "merchant_navy", "family", "jokes", "preferences"]
        memories = []
        
        for collection in collections:
            results = await search_memories(text, [collection], limit=3)
            memories.extend(results)
        
        # b. Build system prompt
        memory_text = ""
        if memories:
            memory_lines = [f"- {m.get('text', '')}" for m in memories if m.get('text')]
            memory_text = "\n".join(memory_lines)
        
        system_prompt = f"""You are a warm, patient, and gentle companion for a man named John who has dementia.
John is at home in Barrowford, Lancashire. Speak to him kindly and simply.
Keep responses short — no more than 3 sentences. Never tell John he has dementia.
If he seems confused, gently orient him with the date and where he is.
Here are some things you know about John:
{memory_text}"""
        
        # c. Get AI response
        ai_response = await get_ai_response(system_prompt, text)
        
        # d. Log to Postgres conversations table
        conn = await get_db_connection()
        if conn:
            try:
                await conn.execute("""
                    INSERT INTO conversations (user_id, started_at, transcript, trigger_type)
                    VALUES ($1, $2, $3, $4)
                """, user_id, datetime.utcnow(), f'{{"user": "{text}", "assistant": "{ai_response}"}}', 'manual')
                # TODO: Get the conversation_id after insert
                conversation_id = None
            except Exception as e:
                logger.warning(f"Could not log conversation: {e}")
            finally:
                await conn.close()
        
        # e. Return response
        return {"response": ai_response, "conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Error in respond_to_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/pending")
async def get_pending_message(user_id: int = Query(default=1)):
    try:
        conn = await get_db_connection()
        if not conn:
            logger.warning("Database not configured, returning null message")
            return {"message": None}
        
        try:
            result = await conn.fetchrow("""
                SELECT id, content, message_type
                FROM messages
                WHERE user_id = $1 AND read_at IS NULL
                ORDER BY created_at ASC
                LIMIT 1
            """, user_id)
            
            if result:
                await conn.execute("UPDATE messages SET read_at = NOW() WHERE id = $1", result['id'])
                return {
                    "message": {
                        "id": result['id'],
                        "content": result['content'],
                        "message_type": result['message_type']
                    }
                }
            return {"message": None}
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Error in get_pending_message: {e}")
        return {"message": None}


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int):
    try:
        conn = await get_db_connection()
        if not conn:
            return {"deleted": True}
        
        try:
            await conn.execute("UPDATE messages SET spoken_at = NOW() WHERE id = $1", message_id)
        finally:
            await conn.close()
        
        return {"deleted": True}
        
    except Exception as e:
        logger.error(f"Error in delete_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/queue")
async def queue_message(
    user_id: int = Body(...),
    content: str = Body(...),
    message_type: str = Body(...)
):
    try:
        conn = await get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        try:
            message_id = await conn.fetchval("""
                INSERT INTO messages (user_id, content, message_type, created_at)
                VALUES ($1, $2, $3, NOW())
                RETURNING id
            """, user_id, content, message_type)
        finally:
            await conn.close()
        
        return {"queued": True, "message_id": message_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in queue_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interventions/trigger")
async def trigger_intervention(
    user_id: int = Body(...),
    trigger_type: str = Body(...)
):
    try:
        current_hour = datetime.utcnow().hour
        
        # Determine intervention type based on hour
        intervention_map = {
            (7, 10): ("morning_story", "merchant_navy"),
            (10, 12): ("family_memory", "family"),
            (12, 15): ("joke", "jokes"),
            (15, 18): ("life_story", "life_stories"),
            (18, 21): ("preferences", "preferences"),
        }
        
        intervention_type = "check_in"
        collection = None
        
        for hour_range, (i_type, coll) in intervention_map.items():
            if hour_range[0] <= current_hour < hour_range[1]:
                intervention_type = i_type
                collection = coll
                break
        
        # Build prompt and get AI response
        if collection:
            memories = await search_memories("", [collection], limit=1)
            memory_text = memories[0].get('text', '') if memories else ""
            system_prompt = f"""You are a warm companion for John. Share a nice memory with him.
{memory_text}
Keep it short and friendly."""
        else:
            system_prompt = """You are a warm companion for John. Gently check in with him.
Ask how he's feeling and remind him of the date."""
        
        ai_response = await get_ai_response(system_prompt, "Hello")
        
        # Queue the message
        conn = await get_db_connection()
        if conn:
            try:
                await conn.execute("""
                    INSERT INTO messages (user_id, content, message_type, created_at)
                    VALUES ($1, $2, $3, NOW())
                """, user_id, ai_response, intervention_type)
            finally:
                await conn.close()
        
        return {"triggered": True, "intervention_type": intervention_type}
        
    except Exception as e:
        logger.error(f"Error in trigger_intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))