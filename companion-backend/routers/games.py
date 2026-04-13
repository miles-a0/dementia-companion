import os
import logging
import random
import json
from fastapi import APIRouter, Body, Query
from services.qdrant_client import search_memories
from services.openrouter import get_ai_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["games"])

COLLECTIONS = ["life_stories", "merchant_navy", "family", "preferences"]
SEED_QUERIES = ["ship", "sea", "family", "food", "Lancashire", "Barrowford", "work", "memories"]

FALLBACK_QUESTION = {
    "question": "What do sailors travel on?",
    "word": "Sea",
    "choices": ["Ship", "Train", "Car"],
    "correct_index": 0,
    "encouragement": "That's right John, a ship!"
}


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


@router.get("/games/word-question")
async def get_word_question(user_id: int = Query(default=1)):
    try:
        collection = random.choice(COLLECTIONS)
        seed_query = random.choice(SEED_QUERIES)
        
        results = await search_memories(seed_query, [collection], limit=5)
        
        topic = seed_query
        if results and len(results) > 0:
            result_text = results[0].get("text", "")
            if result_text:
                words = result_text.split()
                for word in words:
                    word_clean = ''.join(c for c in word if c.isalnum())
                    if len(word_clean) >= 4:
                        topic = word_clean
                        break
        
        system_prompt = """You are creating a gentle word association game for an elderly man named John who has dementia. Create simple, encouraging questions."""
        user_message = """Create a word association question about: '{}'.
Return ONLY valid JSON in this exact format, nothing else:
{{"question": "What goes with a ship?",
 "word": "Ship",
 "choices": ["Captain", "Mountain", "Library"],
 "correct_index": 0,
 "encouragement": "Well done John!"}}""".format(topic)
        
        ai_response = await get_ai_response(system_prompt, user_message)
        
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx+1]
                question_obj = json.loads(json_str)
                
                if "question" in question_obj and "choices" in question_obj:
                    return question_obj
        except Exception as e:
            logger.warning("Failed to parse AI response: {}".format(e))
        
        return FALLBACK_QUESTION
    
    except Exception as e:
        logger.error("Error in get_word_question: {}".format(e))
        return FALLBACK_QUESTION


@router.post("/games/answer")
async def submit_answer(
    user_id: int = Body(...),
    correct: bool = Body(...),
    question_topic: str = Body(default="")
):
    try:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO game_log (user_id, game_type, correct, topic, played_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (user_id, "word_question", correct, question_topic))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                logger.warning("Could not log game result: {}".format(e))
                if conn:
                    conn.close()
    
    except Exception as e:
        logger.error("Error in submit_answer: {}".format(e))
    
    if correct:
        message = "Well done John!"
    else:
        message = "Never mind John, you did your best!"
    
    return {"correct": correct, "message": message}