import random

from src.state_and_stat import GameState


def get_move_random(state: GameState, player: int) -> int | None:
    return random.choice(state.legal_moves) if state.legal_moves else None
