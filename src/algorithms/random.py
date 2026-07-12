import random


def get_move_random(state, player) -> int | None:
    return random.choice(state.valid_moves) if state.valid_moves else None
