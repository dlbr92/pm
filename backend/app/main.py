from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from app.db import init_db
from app.repositories.board_repository import BoardRepository
from app.schemas.ai_chat import AIChatRequest, AIChatResponse
from app.schemas.board import BoardModel
from app.services.ai_chat_service import AIChatService
from app.services.ai_service import AI_DIAGNOSTIC_PROMPT, AIService, AIServiceError
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


def get_ai_service() -> AIService:
    return AIService()


def get_board_service() -> BoardService:
    return board_service


def get_ai_chat_service(
    ai_service: AIService = Depends(get_ai_service),
    board_service_dep: BoardService = Depends(get_board_service),
) -> AIChatService:
    return AIChatService(ai_service=ai_service, board_service=board_service_dep)


@app.get("/api/ai/diagnostic")
def ai_diagnostic(ai_service: AIService = Depends(get_ai_service)) -> dict[str, str]:
    try:
        response_text = ai_service.run_diagnostic()
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "prompt": AI_DIAGNOSTIC_PROMPT,
        "response": response_text,
        "model": ai_service.model,
    }


@app.post("/api/ai/chat", response_model=AIChatResponse)
def ai_chat(
    request: AIChatRequest,
    ai_chat_service: AIChatService = Depends(get_ai_chat_service),
) -> AIChatResponse:
    try:
        reply, board, board_updated = ai_chat_service.run(
            message=request.message,
            history=request.history,
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return AIChatResponse(reply=reply, boardUpdated=board_updated, board=board)

app.mount("/", StaticFiles(directory=WEB_STATIC_DIR, html=True), name="web")
