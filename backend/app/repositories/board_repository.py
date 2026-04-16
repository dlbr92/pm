import json

from app.db import get_board_json, get_or_create_user, save_board_json
from app.schemas.board import BoardModel


class BoardRepository:
    def get_for_username(self, username: str) -> BoardModel | None:
        user_id = get_or_create_user(username)
        raw_board = get_board_json(user_id)
        if raw_board is None:
            return None
        return BoardModel.model_validate_json(raw_board)

    def save_for_username(self, username: str, board: BoardModel) -> BoardModel:
        user_id = get_or_create_user(username)
        payload = json.dumps(board.model_dump(mode="json"), sort_keys=True)
        save_board_json(user_id, payload)
        return board
