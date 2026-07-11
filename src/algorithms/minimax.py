def get_move_minimax(state, player, depth=4):
    """Minimax AI主函数"""
    best_score = -float("inf")
    best_move = None

    for idx in range(27):
        if state.is_valid_move(idx):
            board_backup = state.board.copy()
            score_backup = (state.score_A, state.score_B)
            state.make_move(idx, player)

            score = minimax(
                state, depth - 1, -float("inf"), float("inf"), False, -player
            )

            state.board = board_backup
            state.score_A, state.score_B = score_backup
            state.move_count -= 1

            if score > best_score:
                best_score = score
                best_move = idx

    return best_move


def minimax(state, depth, alpha, beta, is_maximizing, player):
    """Minimax搜索 + Alpha-Beta剪枝"""
    # 如果到达终局或深度限制
    if state.is_terminal() or depth == 0:
        # 评估当前局面
        return evaluate_board(state, player)

    if is_maximizing:
        max_eval = -float("inf")
        for idx in range(27):
            if state.is_valid_move(idx):
                # 模拟落子
                board_backup = state.board.copy()
                score_backup = (state.score_A, state.score_B)
                state.make_move(idx, player)

                eval = minimax(state, depth - 1, alpha, beta, False, -player)

                # 恢复状态
                state.board = board_backup
                state.score_A, state.score_B = score_backup
                state.move_count -= 1

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float("inf")
        for idx in range(27):
            if state.is_valid_move(idx):
                board_backup = state.board.copy()
                score_backup = (state.score_A, state.score_B)
                state.make_move(idx, -player)

                eval = minimax(state, depth - 1, alpha, beta, True, player)

                state.board = board_backup
                state.score_A, state.score_B = score_backup
                state.move_count -= 1

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval


def evaluate_board(state, player):
    if state.move_count >= 26:
        # 从player视角看：player得分高就赢
        if player == 1:
            my_score, opp_score = state.score_A, state.score_B
        else:
            my_score, opp_score = state.score_B, state.score_A

        if my_score > opp_score:
            return 1000
        elif opp_score > my_score:
            return -1000
        else:
            return 0

    # 中间局面：从player视角计算差值
    if player == 1:
        return (state.score_A - state.score_B) * 10
    else:
        return (state.score_B - state.score_A) * 10
