# TODO: implement in Phase 5

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.post("/health/biometrics")
async def receive_biometrics():
    return {"received": True}