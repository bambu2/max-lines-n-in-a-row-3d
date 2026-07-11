def get_move_greedy(state, player) -> int | None:
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
