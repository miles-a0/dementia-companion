from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import logging

from database import init_db_pool
from routers import auth, messages, health_data, media, routines, medication, memories, games

load_dotenv()

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth, prefix="/api")
app.include_router(messages, prefix="/api")
app.include_router(health_data, prefix="/api")
app.include_router(media, prefix="/api")
app.include_router(routines, prefix="/api")
app.include_router(medication, prefix="/api")
app.include_router(memories, prefix="/api")
app.include_router(games, prefix="/api")


@app.on_event("startup")
async def startup():
    await init_db_pool()
    logger.info("Companion API started")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "companion-api"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)