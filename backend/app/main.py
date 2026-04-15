from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
FALLBACK_STATIC_DIR = BASE_DIR / "static"
FRONTEND_STATIC_DIR = BASE_DIR / "frontend-static"
WEB_STATIC_DIR = (
    FRONTEND_STATIC_DIR
    if (FRONTEND_STATIC_DIR / "index.html").exists()
    else FALLBACK_STATIC_DIR
)

app = FastAPI(title="PM MVP Backend")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}

app.mount("/", StaticFiles(directory=WEB_STATIC_DIR, html=True), name="web")
