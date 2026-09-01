"""
贪心策略模块。

选择能立即形成最多线的位置，包含基本防守逻辑。
"""

from max_lines_n_in_a_row_3d.models import GameState


def get_move_greedy(state: GameState, player: int) -> int | None:
    """
    贪心策略：选择能立即形成最多线的位置。

    评分规则：
    - 进攻得分：落子后能完成的线数 × 10
    - 防守得分：能阻止对手成线的位置 × 5（对手已有两个子）

    Args:
        state: 当前游戏状态
        player: 当前玩家（1或-1）

    Returns:
        int | None: 选中的位置索引，如果没有合法位置则返回None
    """
    best_score = -1
    best_move = None

    for idx in state.legal_moves:
        board_copy = state.board.copy()
        board_copy[idx] = player

        score = 0
        for line in state.lines:
            if idx not in line:
                continue
            vals = [board_copy[i] for i in line]
            if all(v == player for v in vals):
                score += 1

        defense_score = 0
        for line in state.lines:
            if idx not in line:
                continue
            vals = [state.board[i] for i in line]
            if vals.count(-player) == 2 and vals.count(0) == 1:
                defense_score += 5

        total_score = score * 10 + defense_score

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move
