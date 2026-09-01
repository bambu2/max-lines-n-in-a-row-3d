"""
随机策略模块。

从合法位置中随机选择一个位置落子，是最简单的AI策略。
"""

import random

from max_lines_n_in_a_row_3d.models import GameState


def get_move_random(state: GameState, player: int) -> int | None:
    """
    随机选择一个合法落子位置。

    Args:
        state: 当前游戏状态
        player: 当前玩家（1或-1）

    Returns:
        int | None: 选中的位置索引，如果没有合法位置则返回None
    """
    return random.choice(state.legal_moves) if state.legal_moves else None
