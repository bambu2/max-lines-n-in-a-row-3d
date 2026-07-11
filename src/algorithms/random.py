import random


def get_move_random(state, player) -> int | None:
    valid_moves = [idx for idx in range(27) if state.is_valid_move(idx)]
    return random.choice(valid_moves) if valid_moves else None
