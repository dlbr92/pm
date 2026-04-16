from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import init_db
from app.repositories.board_repository import BoardRepository
from app.schemas.board import BoardModel
from app.services.board_service import BoardService

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
board_service = BoardService(BoardRepository())


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/api/board", response_model=BoardModel)
def get_board() -> BoardModel:
    return board_service.get_board()


@app.put("/api/board", response_model=BoardModel)
def update_board(board: BoardModel) -> BoardModel:
    return board_service.update_board(board)

app.mount("/", StaticFiles(directory=WEB_STATIC_DIR, html=True), name="web")
