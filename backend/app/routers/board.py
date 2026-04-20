from fastapi import APIRouter, Depends

from app.repositories.board_repository import BoardRepository
from app.schemas.board import BoardModel
from app.services.board_service import BoardService

router = APIRouter()

_board_service = BoardService(BoardRepository())


def get_board_service() -> BoardService:
    return _board_service


@router.get("/board", response_model=BoardModel)
def get_board(board_service: BoardService = Depends(get_board_service)) -> BoardModel:
    return board_service.get_board()


@router.put("/board", response_model=BoardModel)
def update_board(
    board: BoardModel,
    board_service: BoardService = Depends(get_board_service),
) -> BoardModel:
    return board_service.update_board(board)
