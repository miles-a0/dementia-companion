from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user
from models import FamilyMemberCreate, FamilyMemberResponse

router = APIRouter(prefix="/family", tags=["family"])

@router.get("/", response_model=list[FamilyMemberResponse])
async def get_family(current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, relationship, photo_url FROM family_members WHERE user_id = $1 ORDER BY name", current_user["id"])
        return rows

@router.post("/", response_model=FamilyMemberResponse)
async def create_family_member(member: FamilyMemberCreate, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "INSERT INTO family_members (user_id, name, relationship, photo_url) VALUES ($1, $2, $3, $4) RETURNING id, name, relationship, photo_url",
            current_user["id"], member.name, member.relationship, member.photo_url
        )
        return result

@router.delete("/{member_id}")
async def delete_family_member(member_id: int, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM family_members WHERE id = $1 AND user_id = $2", member_id, current_user["id"])
        return {"message": "Deleted"}