import random

from src.game_state import GameState


def get_move_random(state: GameState, player: int) -> int | None:
    return random.choice(state._legal_moves) if state._legal_moves else None
