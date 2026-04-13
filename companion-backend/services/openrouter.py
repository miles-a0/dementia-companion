import os
import logging

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")

FALLBACK_RESPONSE = "I'm here with you John. Would you like me to tell you something about your day?"

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY not set in environment. OpenRouter features will be limited.")


async def get_ai_response(system_prompt: str, user_message: str, model: str = None) -> str:
    """Call OpenRouter chat completions API."""
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set, returning fallback response")
        return FALLBACK_RESPONSE
    
    use_model = model if model else OPENROUTER_MODEL
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://companion-for-john.local",
        "X-Title": "Companion for John"
    }
    
    body = {
        "model": use_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
    except Exception as e:
        logger.error(f"Error in get_ai_response: {e}")
        return FALLBACK_RESPONSE


async def get_embedding(text: str) -> list:
    """Call OpenRouter embeddings API."""
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set, returning fallback embedding")
        return [0.0] * 1536  # Fallback — real embedding will be used when API is available
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://companion-for-john.local",
        "X-Title": "Companion for John"
    }
    
    body = {
        "model": "openai/text-embedding-ada-002",
        "input": text
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            return data["data"][0]["embedding"]
            
    except Exception as e:
        logger.error(f"Error in get_embedding: {e}")
        return [0.0] * 1536  # Fallback — real embedding will be used when API is available