import os
import logging
import json
import httpx
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Body
import psycopg2

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["messages"])

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
N8N_LEARNING_WEBHOOK_URL = os.environ.get("N8N_LEARNING_WEBHOOK_URL")


def get_db_connection():
    """Get synchronous database connection using psycopg2"""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not configured")
        return None
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        return None


def get_or_create_conversation(db_conn, user_id: int, trigger_type: str = 'manual') -> int:
    """Get existing open conversation or create new one"""
    cursor = db_conn.cursor()
    
    cursor.execute("""
        SELECT id FROM conversations
        WHERE user_id = %s AND ended_at IS NULL
        AND started_at > NOW() - INTERVAL '10 minutes'
        ORDER BY started_at DESC LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    if row:
        cursor.close()
        return row[0]
    
    cursor.execute("""
        INSERT INTO conversations (user_id, started_at, transcript, trigger_type)
        VALUES (%s, NOW(), '[]'::jsonb, %s)
        RETURNING id
    """, (user_id, trigger_type))
    
    new_id = cursor.fetchone()[0]
    db_conn.commit()
    cursor.close()
    return new_id


def append_to_transcript(db_conn, conversation_id: int, role: str, text: str):
    """Append a message to the conversation transcript"""
    cursor = db_conn.cursor()
    
    entry = json.dumps([{"role": role, "text": text, "time": datetime.utcnow().isoformat()}])
    
    cursor.execute("""
        UPDATE conversations 
        SET transcript = transcript || %s::jsonb
        WHERE id = %s
    """, (entry, conversation_id))
    
    db_conn.commit()
    cursor.close()


def check_and_close_stale_conversations(db_conn, user_id: int):
    """Close conversations older than 10 minutes and trigger learning webhook"""
    cursor = db_conn.cursor()
    
    cursor.execute("""
        SELECT id FROM conversations
        WHERE user_id = %s AND ended_at IS NULL
        AND started_at < NOW() - INTERVAL '10 minutes'
    """, (user_id,))
    
    stale_ids = [row[0] for row in cursor.fetchall()]
    
    if stale_ids:
        cursor.execute("""
            UPDATE conversations SET ended_at = NOW()
            WHERE user_id = %s AND ended_at IS NULL
            AND started_at < NOW() - INTERVAL '10 minutes'
        """, (user_id,))
        db_conn.commit()
        
        if N8N_LEARNING_WEBHOOK_URL:
            for conv_id in stale_ids:
                try:
                    import threading
                    def trigger_webhook():
                        try:
                            httpx.post(N8N_LEARNING_WEBHOOK_URL, json={
                                "conversation_id": conv_id,
                                "user_id": user_id
                            }, timeout=5.0)
                        except Exception:
                            pass
                    threading.Thread(target=trigger_webhook).start()
                except Exception as e:
                    logger.warning(f"Could not trigger learning webhook: {e}")
    
    cursor.close()


async def queue_message(user_id, content, message_type):
    """Helper function to queue a message - can be imported by other routers"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (user_id, content, message_type, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id
        """, (user_id, content, message_type))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        logger.error(f"Error in queue_message helper: {e}")
        conn.close()
        return None


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


@router.post("/messages/respond")
async def respond_to_message(
    text: str = Body(...),
    user_id: int = Body(default=1),
    conversation_id: Optional[int] = Body(default=None)
):
    try:
        conn = get_db_connection()
        
        if conn:
            try:
                check_and_close_stale_conversations(conn, user_id)
                conversation_id = get_or_create_conversation(conn, user_id, 'manual')
                append_to_transcript(conn, conversation_id, 'user', text)
            except Exception as e:
                logger.warning(f"Could not manage conversation: {e}")
        
        # a. Search Qdrant for relevant memories
        collections_list = ["life_stories", "merchant_navy", "family", "jokes", "preferences"]
        memories = []
        
        for coll in collections_list:
            results = await search_memories(text, [coll], limit=3)
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
        
        # d. Log assistant response to transcript
        if conn:
            try:
                append_to_transcript(conn, conversation_id, 'assistant', ai_response)
                conn.close()
            except Exception as e:
                logger.warning(f"Could not append assistant response: {e}")
        
        # e. Return response
        return {"response": ai_response, "conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Error in respond_to_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/pending")
async def get_pending_message(user_id: int = Query(default=1)):
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not configured, returning null message")
            return {"message": None}
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, message_type
                FROM messages
                WHERE user_id = %s AND read_at IS NULL
                ORDER BY created_at ASC
                LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("UPDATE messages SET read_at = NOW() WHERE id = %s", (row[0],))
                conn.commit()
                cursor.close()
                conn.close()
                return {
                    "message": {
                        "id": row[0],
                        "content": row[1],
                        "message_type": row[2]
                    }
                }
            cursor.close()
            conn.close()
            return {"message": None}
        except Exception as e:
            logger.error(f"Error in get_pending_message: {e}")
            conn.close()
            return {"message": None}
            
    except Exception as e:
        logger.error(f"Error in get_pending_message: {e}")
        return {"message": None}


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int):
    try:
        conn = get_db_connection()
        if not conn:
            return {"deleted": True}
        
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET spoken_at = NOW() WHERE id = %s", (message_id,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error in delete_message: {e}")
            conn.close()
        
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
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (user_id, content, message_type, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING id
            """, (user_id, content, message_type))
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error in queue_message: {e}")
            conn.close()
            raise HTTPException(status_code=500, detail=str(e))
        
        return {"queued": True, "message_id": new_id}
        
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
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (user_id, content, message_type, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, ai_response, intervention_type))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                logger.warning(f"Could not queue message: {e}")
        
        return {"triggered": True, "intervention_type": intervention_type}
        
    except Exception as e:
        logger.error(f"Error in trigger_intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get conversation details including transcript"""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database not configured"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, started_at, ended_at, transcript, trigger_type
            FROM conversations WHERE id = %s
        """, (conversation_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return {"error": "Conversation not found"}
        
        return {
            "id": row[0],
            "user_id": row[1],
            "started_at": row[2].isoformat() if row[2] else None,
            "ended_at": row[3].isoformat() if row[3] else None,
            "transcript": row[4],
            "trigger_type": row[5]
        }
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        if conn:
            conn.close()
        return {"error": str(e)}