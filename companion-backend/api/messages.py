from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user
from models import MessageCreate, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/", response_model=list[MessageResponse])
async def get_messages(current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT m.id, m.user_id, m.from_family_id, m.audio_url, m.text_content, m.is_read, m.created_at
            FROM messages m
            WHERE m.user_id = $1
            ORDER BY m.created_at DESC
        """, current_user["id"])
        return rows

@router.post("/", response_model=MessageResponse)
async def create_message(message: MessageCreate, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "INSERT INTO messages (user_id, from_family_id, text_content, audio_url) VALUES ($1, $2, $3, $4) RETURNING *",
            current_user["id"], message.from_family_id, message.text_content, message.audio_url
        )
        return result

@router.post("/{message_id}/read")
async def mark_as_read(message_id: int, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE messages SET is_read = TRUE WHERE id = $1 AND user_id = $2", message_id, current_user["id"])
        return {"message": "Marked as read"}