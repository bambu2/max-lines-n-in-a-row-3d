import time


class State:
    """3x3x3 无中心块井字棋游戏状态"""

    def __init__(self):
        self.board = [0] * 27  # 0=空, 1=玩家A, -1=玩家B
        self.lines = self._generate_all_lines_no_center()
        self.score_A = 0
        self.score_B = 0
        self.move_count = 0
        self.center_idx = 13
        self.current_player = 1

    def _generate_all_lines_no_center(self):
        all_lines = self._generate_all_lines()
        selected_lines = []

        for line in all_lines:
            if (1, 1, 1) not in line:  # 排除经过中心的线
                idx_line = [xyz_to_idx(*coord) for coord in line]
                selected_lines.append(idx_line)

        return selected_lines

    def _generate_all_lines(self):
        lines = []

        # 1. X轴方向 (每层每行)
        for layer in range(3):
            for r in range(3):
                lines.append([(layer, r, 0), (layer, r, 1), (layer, r, 2)])

        # 2. Y轴方向 (每层每列)
        for layer in range(3):
            for c in range(3):
                lines.append([(layer, 0, c), (layer, 1, c), (layer, 2, c)])

        # 3. Z轴方向 (跨层)
        for r in range(3):
            for c in range(3):
                lines.append([(0, r, c), (1, r, c), (2, r, c)])

        # 4. 每层对角线 (3层 × 2条)
        for layer in range(3):
            lines.append([(layer, 0, 0), (layer, 1, 1), (layer, 2, 2)])
            lines.append([(layer, 0, 2), (layer, 1, 1), (layer, 2, 0)])

        # 5. 跨层对角线
        for r in range(3):
            lines.append([(0, r, 0), (1, r, 1), (2, r, 2)])
            lines.append([(0, r, 2), (1, r, 1), (2, r, 0)])

        for c in range(3):
            lines.append([(0, 0, c), (1, 1, c), (2, 2, c)])
            lines.append([(0, 2, c), (1, 1, c), (2, 0, c)])

        # 6. 体对角线 (4条)
        lines.append([(0, 0, 0), (1, 1, 1), (2, 2, 2)])
        lines.append([(0, 0, 2), (1, 1, 1), (2, 2, 0)])
        lines.append([(0, 2, 0), (1, 1, 1), (2, 0, 2)])
        lines.append([(0, 2, 2), (1, 1, 1), (2, 0, 0)])

        return lines

    def is_valid_move(self, idx) -> bool:
        """检查走法是否合法"""
        if idx == self.center_idx:  # 中心不可用
            return False
        if idx < 0 or idx >= 27:  # 索引范围
            return False
        return self.board[idx] == 0  # 空位

    def get_valid_moves(self) -> list:
        moves = []
        for idx in range(27):
            if self.is_valid_move(idx):
                moves.append(idx)
        return moves

    def make_move(self, idx, player) -> bool:
        """
        执行走法

        Args:
            idx: 落子位置 (0-26)
            player: 当前玩家 (1 或 -1)

        Returns:
            bool: 是否成功
        """

        self.board[idx] = player
        self.move_count += 1

        # ========== 检查新完成的线 ==========
        lines_completed = 0
        for line in self.lines:
            if idx not in line:
                continue

            # 检查这条线是否全部是当前玩家
            is_complete = True
            for pos in line:
                if self.board[pos] != player:
                    is_complete = False
                    break

            if is_complete:
                if player == 1:
                    self.score_A += 1
                else:
                    self.score_B += 1
                lines_completed += 1

        self.current_player = -player

        return True

    def is_terminal(self) -> bool:
        return self.move_count >= 26

    def get_score(self, player) -> int:
        """获取指定玩家的得分"""
        if player == 1:
            return self.score_A
        elif player == -1:
            return self.score_B
        else:
            return 0

    def copy(self):
        new_state = State()
        new_state.board = self.board.copy()
        new_state.score_A = self.score_A
        new_state.score_B = self.score_B
        new_state.move_count = self.move_count
        new_state.current_player = self.current_player
        # lines 和 center_idx 是只读的，可以共享
        return new_state


class Stats:
    def __init__(self):
        self.total_games = 0
        self.wins_A = 0
        self.wins_B = 0
        self.draws = 0
        self.score_A_list = []
        self.score_B_list = []
        self.avg_score_A = 0.0
        self.avg_score_B = 0.0
        self.avg_time = 0.0
        self.win_rate_A = 0.0
        self.win_rate_B = 0.0
        self.draw_rate = 0.0
        self.game_times = []

    def update(self, state, game_time):
        self.score_A_list.append(state.score_A)
        self.score_B_list.append(state.score_B)
        self.game_times.append(game_time)

        if state.score_A > state.score_B:
            self.wins_A += 1
        elif state.score_B > state.score_A:
            self.wins_B += 1
        else:
            self.draws += 1

    def result_update(self):
        self.avg_score_A = (
            sum(self.score_A_list) / self.total_games if self.total_games > 0 else 0.0
        )
        self.avg_score_B = (
            sum(self.score_B_list) / self.total_games if self.total_games > 0 else 0.0
        )
        self.avg_time = (
            sum(self.game_times) / self.total_games if self.total_games > 0 else 0.0
        )
        self.win_rate_A = (
            self.wins_A / self.total_games if self.total_games > 0 else 0.0
        )
        self.win_rate_B = (
            self.wins_B / self.total_games if self.total_games > 0 else 0.0
        )
        self.draw_rate = self.draws / self.total_games if self.total_games > 0 else 0.0


def print_board(state: State):
    symbols = {0: "·", 1: "X", -1: "O"}

    for layer in range(3):
        print(f"\n=== 第 {layer + 1} 层 ===")
        for row in range(3):
            line = ""
            for col in range(3):
                idx = xyz_to_idx(layer, row, col)
                if idx == state.center_idx:
                    line += " ✦ "  # 用特殊符号标记不可用中心
                else:
                    line += f" {symbols[state.board[idx]]} "
            print(line)


def xyz_to_idx(layer, row, col):
    return layer * 9 + row * 3 + col


def idx_to_xyz(idx):
    layer = idx // 9
    row = (idx % 9) // 3
    col = idx % 3
    return layer, row, col


def rate_to_percentage(rate):
    return f"{rate * 100:.1f}%"


def print_stats(stats, verbose=False) -> None:
    print("🏆 胜负统计:")
    print(f"  玩家A胜: {stats.wins_A} ({rate_to_percentage(stats.win_rate_A)})")
    print(f"  玩家B胜: {stats.wins_B} ({rate_to_percentage(stats.win_rate_B)})")
    print(f"  平局:    {stats.draws} ({rate_to_percentage(stats.draw_rate)})")
    print()
    print("📈连线数统计:")
    print("  玩家 A 连线数")
    print(
        f"    最高: {max(stats.score_A_list)}, 最低: {min(stats.score_A_list)}, 平均: {stats.avg_score_A:.2f}"
    )
    print("  玩家 B 连线数")
    print(
        f"    最高: {max(stats.score_B_list)}, 最低: {min(stats.score_B_list)}, 平均: {stats.avg_score_B:.2f}"
    )
    print(f"  平均连线数差: {stats.avg_score_A - stats.avg_score_B:.2f}")
    print()
    if verbose:
        print("⏱️ 步数/时间:")
        print(f"  平均每局耗时: {stats.avg_time:.4f}秒")
        print(f"  总耗时:   {sum(stats.game_times):.2f}秒")
        print()


def run_ai1_vs_ai2(ai1, ai2, total_games=100, verbose=False, max_moves=26) -> Stats:
    """
    运行两个AI对战（AI1先手，AI2后手）
    """

    stats = Stats()
    stats.total_games = total_games

    for i in range(total_games):
        if verbose:
            print(f"第 {i + 1}/{total_games} 局")

        state = State()
        current_player = 1
        move_count = 0

        start_time = time.time()

        while move_count < max_moves:
            if current_player == 1:
                move = ai1(state, current_player)
            else:
                move = ai2(state, current_player)

            if move is None:
                break

            state.make_move(move, current_player)
            move_count += 1
            current_player = -current_player

            if verbose:
                print(f"第 {move_count} 步: {idx_to_xyz(move)}")

        end_time = time.time()
        game_time = end_time - start_time

        stats.update(state, game_time)

        if verbose:
            print_board(state)

    stats.result_update()

    return stats
