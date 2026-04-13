# TODO: implement in Phase 7

from fastapi import APIRouter

router = APIRouter(tags=["media"])


@router.get("/media/photos")
async def get_photos():
    return {"photos": []}


@router.get("/media/music")
async def get_music():
    return {"tracks": []}