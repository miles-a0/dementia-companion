from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user
from models import MusicFavoriteCreate, MusicFavoriteResponse

router = APIRouter(prefix="/music", tags=["music"])

@router.get("/", response_model=list[MusicFavoriteResponse])
async def get_music(current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, title, artist, audio_url, cover_url FROM music_favorites WHERE user_id = $1 ORDER BY created_at DESC", current_user["id"])
        return rows

@router.post("/", response_model=MusicFavoriteResponse)
async def create_music(song: MusicFavoriteCreate, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "INSERT INTO music_favorites (user_id, title, artist, audio_url, cover_url) VALUES ($1, $2, $3, $4, $5) RETURNING id, title, artist, audio_url, cover_url",
            current_user["id"], song.title, song.artist, song.audio_url, song.cover_url
        )
        return result

@router.delete("/{song_id}")
async def delete_music(song_id: int, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM music_favorites WHERE id = $1 AND user_id = $2", song_id, current_user["id"])
        return {"message": "Deleted"}