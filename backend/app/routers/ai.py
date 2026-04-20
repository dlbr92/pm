from fastapi import APIRouter, Depends, HTTPException

from app.routers.board import get_board_service
from app.schemas.ai_chat import AIChatRequest, AIChatResponse
from app.services.ai_chat_service import AIChatService
from app.services.ai_service import AI_DIAGNOSTIC_PROMPT, AIService, AIServiceError
from app.services.board_service import BoardService

router = APIRouter()


def get_ai_service() -> AIService:
    return AIService()


def get_ai_chat_service(
    ai_service: AIService = Depends(get_ai_service),
    board_service: BoardService = Depends(get_board_service),
) -> AIChatService:
    return AIChatService(ai_service=ai_service, board_service=board_service)


@router.get("/ai/diagnostic")
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


@router.post("/ai/chat", response_model=AIChatResponse)
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
