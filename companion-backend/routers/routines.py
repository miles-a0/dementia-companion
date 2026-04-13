# TODO: implement in Phase 4

from fastapi import APIRouter

router = APIRouter(tags=["routines"])


@router.post("/routines/morning-greeting")
async def trigger_morning_greeting():
    return {"queued": True}