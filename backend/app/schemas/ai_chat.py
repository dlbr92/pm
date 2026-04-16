from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.board import BoardModel


class AIChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[AIChatHistoryItem] = Field(default_factory=list)


class AIChatModelOutput(BaseModel):
    reply: str = Field(min_length=1)
    board_update: BoardModel | None = None


class AIChatResponse(BaseModel):
    reply: str
    boardUpdated: bool
    board: BoardModel
