# TODO: implement in Phase 9

from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login():
    return {"token": "placeholder"}