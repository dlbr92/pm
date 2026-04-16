from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import init_db

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


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}

app.mount("/", StaticFiles(directory=WEB_STATIC_DIR, html=True), name="web")
