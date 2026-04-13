# TODO: implement in Phase 9

from fastapi import APIRouter

router = APIRouter(tags=["memories"])


@router.post("/carer/memories/upload")
async def upload_memory():
    return {"stored": True}


@router.get("/carer/log")
async def get_carer_log():
    return {"log": []}