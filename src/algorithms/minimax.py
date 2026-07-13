from src.state_and_stat import GameState


def get_move_minimax(state: GameState, player: int, depth: int = 4) -> int | None:
    """Get best move using minimax with alpha-beta pruning."""

    if not state.legal_moves:
        return None
    if len(state.legal_moves) == 1:
        return state.legal_moves[0]

    # ✅ 修复: 始终从玩家1视角评估，玩家1最大化，玩家-1最小化
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

        # ✅ 修复: 玩家1选最大值，玩家-1选最小值
        if is_maximizing:
            if score > best_score:
                best_score = score
                best_move = idx
        else:
            if score < best_score:
                best_score = score
                best_move = idx

    return best_move


def minimax(state: GameState, depth: int, alpha, beta, is_maximizing) -> float:
    """Minimax with alpha-beta pruning using undo.

    ✅ 评估值始终从玩家1的视角返回：
       - 玩家1的回合 (is_maximizing=True)  → 最大化
       - 玩家-1的回合 (is_maximizing=False) → 最小化
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


# ✅ 修复: 始终从玩家1的固定视角评估，不再随 current_player 翻转
def evaluate_board(state: GameState) -> float:
    if state.is_terminal():
        if state.score_first_player > state.score_second_player:
            return 10000  # 玩家1赢
        elif state.score_second_player > state.score_first_player:
            return -10000  # 玩家-1赢
        else:
            return 0  # 平局

    # 始终从玩家1视角: 正数有利于玩家1，负数有利于玩家-1
    score_diff = state.score_first_player - state.score_second_player

    positional_bonus = calculate_sophisticated_bonus(state, 1)

    # ✅ 修复: 移除失效的 calculate_mobility_bonus
    # 棋盘是共享的，双方合法走法相同，mobility 差值始终为 0，无意义

    return score_diff * 10 + positional_bonus


def get_position_importance(pos):
    """Return the strategic importance of a position (0-10)"""
    # Corners - most important
    corners = [0, 2, 6, 8, 18, 20, 24, 26]
    if pos in corners:
        return 8

    # Edges - medium importance
    edges = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    if pos in edges:
        return 5

    # Face centers - lower importance
    face_centers = [4, 10, 12, 14, 16, 22]
    if pos in face_centers:
        return 3

    # Center (13) - banned, should never be here
    return 0


def calculate_sophisticated_bonus(state: GameState, player: int):
    """Calculate positional bonus using weighted importance.
    ✅ 从玩家1视角: player=1 的棋子加分，player=-1 的棋子减分
    """
    bonus = 0
    for pos in range(27):
        if pos == state.banned_idx:
            continue
        if state.board[pos] == player:
            bonus += get_position_importance(pos)
        elif state.board[pos] == -player:
            bonus -= get_position_importance(pos)
    return bonus
