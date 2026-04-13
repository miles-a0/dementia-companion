# TODO: implement in Phase 8

from fastapi import APIRouter

router = APIRouter(tags=["games"])


@router.get("/games/word-question")
async def get_word_question():
    return {"word": "placeholder", "choices": [], "correct_index": 0}