from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routers import ai, board, health

BASE_DIR = Path(__file__).resolve().parent.parent
FALLBACK_STATIC_DIR = BASE_DIR / "static"
FRONTEND_STATIC_DIR = BASE_DIR / "frontend-static"
WEB_STATIC_DIR = (
    FRONTEND_STATIC_DIR
    if (FRONTEND_STATIC_DIR / "index.html").exists()
    else FALLBACK_STATIC_DIR
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="PM MVP Backend", lifespan=lifespan)
app.include_router(health.router, prefix="/api")
app.include_router(board.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

app.mount("/", StaticFiles(directory=WEB_STATIC_DIR, html=True), name="web")
