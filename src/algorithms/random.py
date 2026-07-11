import random


def get_move_random(state, player):
    """随机选择一个合法位置"""
    valid_moves = []
    for idx in range(27):
        if state.is_valid_move(idx):
            valid_moves.append(idx)

    if valid_moves:
        return random.choice(valid_moves)
    return None
