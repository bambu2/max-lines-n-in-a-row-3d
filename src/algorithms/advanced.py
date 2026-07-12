from src.utils import idx_to_xyz


def get_move_advanced(state, player) -> int | None:
    """使用评估函数，选择潜力最高的位置"""
    best_score = -999
    best_move = None

    for idx in state.valid_moves:
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
        layer, r, c = idx_to_xyz(idx)
        if layer in (0, 2) and r in (0, 2) and c in (0, 2):
            position_bonus = 3  # 角格
        elif (
            (layer == 1 and r in (0, 2) and c in (0, 2))
            or (r == 1 and layer in (0, 2) and c in (0, 2))
            or (c == 1 and layer in (0, 2) and r in (0, 2))
        ):
            position_bonus = 2  # 边心格
        else:
            position_bonus = 0

        total_score = offense_score + defense_score + position_bonus

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move
