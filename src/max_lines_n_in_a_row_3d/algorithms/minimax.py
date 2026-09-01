"""
极小极大策略模块。

使用带alpha-beta剪枝的minimax算法搜索最优走法。
"""

from max_lines_n_in_a_row_3d.models import GameState


def get_move_minimax(state: GameState, player: int, depth: int = 4) -> int | None:
    """
    使用minimax算法（带alpha-beta剪枝）获取最优走法。

    评估值始终从玩家1的视角返回：
    - 玩家1（先手）选择最大化评估值
    - 玩家-1（后手）选择最小化评估值

    Args:
        state: 当前游戏状态
        player: 当前玩家（1或-1）
        depth: 搜索深度（默认4层）

    Returns:
        int | None: 选中的位置索引，如果没有合法位置则返回None
    """
    if not state.legal_moves:
        return None
    if len(state.legal_moves) == 1:
        return state.legal_moves[0]

    is_maximizing = player == 1

    if is_maximizing:
        best_score = -float("inf")
    else:
        best_score = float("inf")

    best_move = state.legal_moves[0]

    for idx in state.legal_moves:
        state.make_move(idx, player)

        score = minimax(
            state, depth - 1, -float("inf"), float("inf"), not is_maximizing
        )

        state.undo_move()

        if is_maximizing:
            if score > best_score:
                best_score = score
                best_move = idx
        else:
            if score < best_score:
                best_score = score
                best_move = idx

    return best_move


def minimax(
    state: GameState, depth: int, alpha: float, beta: float, is_maximizing: bool
) -> float:
    """
    Minimax算法核心实现，带alpha-beta剪枝。

    评估值始终从玩家1的视角返回：
    - is_maximizing=True（玩家1回合）：最大化评估值
    - is_maximizing=False（玩家-1回合）：最小化评估值

    Args:
        state: 当前游戏状态
        depth: 剩余搜索深度
        alpha: alpha剪枝阈值
        beta: beta剪枝阈值
        is_maximizing: 当前是否为最大化玩家

    Returns:
        float: 评估值（正数有利于玩家1，负数有利于玩家-1）
    """
    if state.is_terminal() or depth == 0:
        return evaluate_board(state)

    legal_moves = state.legal_moves
    if not legal_moves:
        return evaluate_board(state)

    if is_maximizing:
        max_eval = -float("inf")
        for idx in legal_moves:
            state.make_move(idx, 1)
            eval_score = minimax(state, depth - 1, alpha, beta, False)
            state.undo_move()

            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for idx in legal_moves:
            state.make_move(idx, -1)
            eval_score = minimax(state, depth - 1, alpha, beta, True)
            state.undo_move()

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def evaluate_board(state: GameState) -> float:
    """
    评估当前棋盘状态。

    始终从玩家1的固定视角评估：
    - 正数有利于玩家1
    - 负数有利于玩家-1

    评估公式：score_diff × 10 + positional_bonus

    Args:
        state: 当前游戏状态

    Returns:
        float: 评估值
    """
    if state.is_terminal():
        if state.score_first_player > state.score_second_player:
            return 10000
        elif state.score_second_player > state.score_first_player:
            return -10000
        else:
            return 0

    score_diff = state.score_first_player - state.score_second_player
    positional_bonus = calculate_sophisticated_bonus(state, 1)

    return score_diff * 10 + positional_bonus


def get_position_importance(pos: int) -> int:
    """
    获取位置的战略重要性评分（0-10）。

    位置分类：
    - 角格（8个）： → 评分 8
    - 边格（12个）： → 评分 5
    - 面心格（6个）： → 评分 3
    - 中心格（1个）：→ 评分 0

    Args:
        pos: 位置索引（0-26）

    Returns:
        int: 战略重要性评分（0-10）
    """
    corners = [0, 2, 6, 8, 18, 20, 24, 26]
    if pos in corners:
        return 8

    edges = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    if pos in edges:
        return 5

    face_centers = [4, 10, 12, 14, 16, 22]
    if pos in face_centers:
        return 3

    return 0


def calculate_sophisticated_bonus(state: GameState, player: int) -> int:
    """
    计算位置加成分数。

    从玩家1视角计算：
    - 玩家1的棋子：加上位置重要性
    - 玩家-1的棋子：减去位置重要性

    Args:
        state: 当前游戏状态
        player: 参考玩家（通常为1）

    Returns:
        int: 位置加成分数
    """
    bonus = 0
    for pos in range(27):
        if pos in state.forbidden_indexes:
            continue
        if state.board[pos] == player:
            bonus += get_position_importance(pos)
        elif state.board[pos] == -player:
            bonus -= get_position_importance(pos)
    return bonus
