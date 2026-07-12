import random

from src.utils import GameState


def get_move_random(state: GameState, player: int) -> int | None:
    return random.choice(state.valid_moves) if state.valid_moves else None
