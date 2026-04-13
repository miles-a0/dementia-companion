# TODO: implement in Phase 6

from fastapi import APIRouter

router = APIRouter(tags=["medication"])


@router.get("/medication/schedule")
async def get_medication_schedule():
    return {"medications": []}


@router.post("/medication/confirm")
async def confirm_medication():
    return {"confirmed": True}


@router.get("/medication/pending")
async def get_pending_medications():
    return {"pending": []}