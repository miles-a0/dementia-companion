from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user
from models import PhotoAlbumCreate, PhotoAlbumResponse, PhotoCreate, PhotoResponse

router = APIRouter(prefix="/photos", tags=["photos"])

@router.get("/albums", response_model=list[PhotoAlbumResponse])
async def get_albums(current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM photo_albums WHERE user_id = $1 ORDER BY created_at DESC", current_user["id"])
        return rows

@router.post("/albums", response_model=PhotoAlbumResponse)
async def create_album(album: PhotoAlbumCreate, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "INSERT INTO photo_albums (user_id, name) VALUES ($1, $2) RETURNING id, name",
            current_user["id"], album.name
        )
        return result

@router.get("/albums/{album_id}", response_model=list[PhotoResponse])
async def get_album_photos(album_id: int, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, image_url, caption FROM photos WHERE album_id = $1 ORDER BY created_at DESC", album_id)
        return rows

@router.post("/", response_model=PhotoResponse)
async def create_photo(photo: PhotoCreate, album_id: int = None, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        if album_id:
            result = await conn.fetchrow(
                "INSERT INTO photos (album_id, image_url, caption) VALUES ($1, $2, $3) RETURNING id, image_url, caption",
                album_id, photo.image_url, photo.caption
            )
        else:
            default_album = await conn.fetchrow("SELECT id FROM photo_albums WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1", current_user["id"])
            if default_album:
                result = await conn.fetchrow(
                    "INSERT INTO photos (album_id, image_url, caption) VALUES ($1, $2, $3) RETURNING id, image_url, caption",
                    default_album["id"], photo.image_url, photo.caption
                )
            else:
                new_album = await conn.fetchrow(
                    "INSERT INTO photo_albums (user_id, name) VALUES ($1, $2) RETURNING id",
                    current_user["id"], "Default Album"
                )
                result = await conn.fetchrow(
                    "INSERT INTO photos (album_id, image_url, caption) VALUES ($1, $2, $3) RETURNING id, image_url, caption",
                    new_album["id"], photo.image_url, photo.caption
                )
        return result

@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, current_user = Depends(get_current_user)):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM photos WHERE id = $1", photo_id)
        return {"message": "Deleted"}