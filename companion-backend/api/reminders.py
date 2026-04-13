from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("/")
async def get_reminders(current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM reminders WHERE user_id = $1 ORDER BY due_date", current_user["id"])
        return rows

@router.post("/")
async def create_reminder(title: str, due_date: str, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "INSERT INTO reminders (user_id, title, due_date) VALUES ($1, $2, $3) RETURNING *",
            current_user["id"], title, due_date
        )
        return result