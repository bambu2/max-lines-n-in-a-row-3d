import random

from game_state import GameState
from utils import idx_to_xyz


def get_ai_move_random(state, player):
    """随机选择一个合法位置"""
    valid_moves = []
    for idx in range(27):
        if state.is_valid_move(idx):
            valid_moves.append(idx)

    if valid_moves:
        return random.choice(valid_moves)
    return None


def get_ai_move_greedy(state, player):
    """选择能立即形成最多线的位置"""
    best_score = -1
    best_move = None

    for idx in range(27):
        if not state.is_valid_move(idx):
            continue

        # 模拟落子
        board_copy = state.board.copy()
        board_copy[idx] = player

        # 计算如果下这里，能完成几条线
        score = 0
        for line in state.lines:
            if idx not in line:
                continue
            vals = [board_copy[i] for i in line]
            if all(v == player for v in vals):
                score += 1

        # 防守：如果对手下一步能完成线，优先堵
        defense_score = 0
        for line in state.lines:
            if idx not in line:
                continue
            vals = [state.board[i] for i in line]
            # 如果对手已经有两个子，且第三个是空位
            if vals.count(-player) == 2 and vals.count(0) == 1:
                defense_score += 5  # 高优先级防守

        total_score = score * 10 + defense_score

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move


def get_ai_move_advanced(state, player):
    """使用评估函数，选择潜力最高的位置"""
    best_score = -999
    best_move = None
    center_idx = 13

    for idx in range(27):
        if not state.is_valid_move(idx):
            continue

        # 进攻得分
        offense_score = 0
        for line in state.lines:
            if idx not in line:
                continue

            vals = [state.board[i] for i in line]

            # 如果线中有对手棋子，这条线被堵
            if any(v == -player for v in vals):
                continue

            your_count = sum(1 for v in vals if v == player)
            empty_count = sum(1 for v in vals if v == 0)

            if empty_count > 0:
                if your_count == 2:  # 差一步完成
                    offense_score += 100
                elif your_count == 1:
                    offense_score += 10
                else:
                    offense_score += 1

        # 防守得分（阻止对手）
        defense_score = 0
        for line in state.lines:
            if idx not in line:
                continue

            vals = [state.board[i] for i in line]

            # 检查对手的威胁
            if any(v == player for v in vals):
                continue

            opponent_count = sum(1 for v in vals if v == -player)
            empty_count = sum(1 for v in vals if v == 0)

            if empty_count > 0:
                if opponent_count == 2:  # 对手差一步
                    defense_score += 80
                elif opponent_count == 1:
                    defense_score += 5

        # 位置加成
        position_bonus = 0
        l, r, c = idx_to_xyz(idx)
        if idx == 13:  # 中心（虽然不能用，但还是留着）
            position_bonus = 0
        elif l in (0, 2) and r in (0, 2) and c in (0, 2):
            position_bonus = 3  # 角格
        elif (
            (l == 1 and r in (0, 2) and c in (0, 2))
            or (r == 1 and l in (0, 2) and c in (0, 2))
            or (c == 1 and l in (0, 2) and r in (0, 2))
        ):
            position_bonus = 2  # 边心格

        total_score = offense_score + defense_score + position_bonus

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move


def minimax(state, depth, alpha, beta, is_maximizing, player):
    """Minimax搜索 + Alpha-Beta剪枝"""
    # 如果到达终局或深度限制
    if state.move_count >= 26 or depth == 0:
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


def get_ai_move_minimax(state, player, depth=4):
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


def evaluate_board(state, player):
    """评估当前局面的得分"""
    # 终局评估
    if state.move_count >= 26:
        if state.score_A > state.score_B:
            return 1000 if player == 1 else -1000
        elif state.score_B > state.score_A:
            return 1000 if player == -1 else -1000
        else:
            return 0

    # 中间局面评估
    score_diff = state.score_A - state.score_B
    return score_diff * 10  # 转换回玩家视角
