import time
from dataclasses import dataclass
from tqdm import tqdm
from src.utils import xyz_to_idx, idx_to_xyz, rate_to_percentage


@dataclass()
class GameState:
    board: list = [0] * 27  # 0=空, 1=玩家A, -1=玩家B
    score_first_player: int = 0
    score_second_player: int = 0
    move_count: int = 0
    current_player = 1
    move_history = []

    def __init__(self):
        self.lines = self._select_lines()
        self.banned_idx = 13
        self.legal_moves = []

    def is_legal_move(self, idx) -> bool:
        return (self.board[idx] == 0) and (idx in self.legal_moves)

    @property
    def legal_moves(self):
        return self.legal_moves

    @legal_moves.setter
    def legal_moves(self) -> list:
        moves = []
        for idx in self.legal_moves:
            if self.is_legal_move:
                moves.append(idx)
        print(moves)
        return moves

    def _select_lines(self):
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

    def make_move(self, idx, player) -> bool:
        """
        执行走法

        Args:
            idx: 落子位置 (0-26)
            player: 当前玩家 (1 或 -1)

        Returns:
            bool: 是否成功
        """
        if not self.is_legal_move(idx):
            return False

        undo_info = {
            "idx": idx,
            "previous_value": self.board[idx],
            "score_A_before": self.score_first_player,
            "score_B_before": self.score_second_player,
            "player": player,
        }

        self.board[idx] = player
        self.move_count += 1
        self.move_history.append(undo_info)

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
                    self.score_first_player += 1
                else:
                    self.score_second_player += 1
                lines_completed += 1

        self.current_player = -player

        return True

    def undo_move(self) -> bool:
        """
        Undo the last move.

        Returns:
            bool: True if undo was successful, False if no moves to undo
        """
        if not self.move_history:
            return False

        # Pop the last undo info
        undo_info = self.move_history.pop()

        # Restore the board
        self.board[undo_info["idx"]] = undo_info["previous_value"]

        # Restore scores
        self.score_first_player = undo_info["score_A_before"]
        self.score_second_player = undo_info["score_B_before"]

        # Decrement move count
        self.move_count -= 1

        return True

    def undo_move_without_history(
        self, idx, previous_value, score_A_before, score_B_before
    ):
        """
        Alternative: Undo a specific move without using history.
        Use this if you want to manually pass undo information.
        """
        self.board[idx] = previous_value
        self.score_first_player = score_A_before
        self.score_second_player = score_B_before
        self.move_count -= 1

    def is_terminal(self) -> bool:
        return self.move_count >= 26 or all(pos != 0 for pos in self.board)

    def copy(self):
        new_state = GameState()
        new_state.board = self.board.copy()
        new_state.score_first_player = self.score_first_player
        new_state.score_second_player = self.score_second_player
        new_state.move_count = self.move_count
        new_state.current_player = self.current_player
        # lines 和 center_idx 是只读的，可以共享
        return new_state

    def print_board(self):
        symbols = {0: "·", 1: "X", -1: "O"}

        for layer in range(3):
            print(f"\n=== 第 {layer + 1} 层 ===")
            for row in range(3):
                line = ""
                for col in range(3):
                    idx = xyz_to_idx(layer, row, col)
                    if idx == self.banned_idx:
                        line += " ✦ "  # 用特殊符号标记不可用中心
                    else:
                        line += f" {symbols[self.board[idx]]} "
                print(line)


@dataclass(slots=True)
class Stats:
    total_games: int
    wins_first_player: int = 0
    wins_second_player: int = 0
    draws: int = 0
    scores_first_player = []
    scores_second_player = []
    avg_score_first_player: float = 0.0
    avg_score_second_player: float = 0.0
    avg_time: float = 0.0
    win_rate_first_player: float = 0.0
    win_rate_second_player: float = 0.0
    draw_rate: float = 0.0
    total_time = []

    def update(self, state, game_time):
        self.scores_first_player.append(state.score_A)
        self.scores_second_player.append(state.score_B)
        self.total_time.append(game_time)

        if state.score_A > state.score_B:
            self.wins_first_player += 1
        elif state.score_B > state.score_A:
            self.wins_second_player += 1
        else:
            self.draws += 1

    def result_update(self):
        self.avg_score_first_player = (
            sum(self.scores_first_player) / self.total_games
            if self.total_games > 0
            else 0.0
        )
        self.avg_score_second_player = (
            sum(self.scores_second_player) / self.total_games
            if self.total_games > 0
            else 0.0
        )
        self.avg_time = (
            sum(self.total_time) / self.total_games if self.total_games > 0 else 0.0
        )
        self.win_rate_first_player = (
            self.wins_first_player / self.total_games if self.total_games > 0 else 0.0
        )
        self.win_rate_second_player = (
            self.wins_second_player / self.total_games if self.total_games > 0 else 0.0
        )
        self.draw_rate = self.draws / self.total_games if self.total_games > 0 else 0.0

    def print_stats(self) -> None:
        print("🏆 胜负统计:")
        print(
            f"  先手胜: {self.wins_first_player} ({rate_to_percentage(self.win_rate_first_player)})"
        )
        print(
            f"  后手胜: {self.wins_second_player} ({rate_to_percentage(self.win_rate_second_player)})"
        )
        print(f"  平局:    {self.draws} ({rate_to_percentage(self.draw_rate)})")
        print()
        print("📈连线数统计:")
        print("  先手连线数")
        print(
            f"    最高: {max(self.scores_first_player)}, 最低: {min(self.scores_first_player)}, 平均: {self.avg_score_first_player:.2f}"
        )
        print("  后手连线数")
        print(
            f"    最高: {max(self.scores_second_player)}, 最低: {min(self.scores_second_player)}, 平均: {self.avg_score_second_player:.2f}"
        )
        print(
            f"  平均连线数差: {self.avg_score_first_player - self.avg_score_second_player:.2f}"
        )
        print()
        print(f"  平均每局耗时: {self.avg_time:.4f}秒")
        print(f"  总耗时:   {sum(self.total_time):.2f}秒")


def get_stats(
    first_player, second_player, total_games=100, verbose=False, max_moves=26
) -> Stats:
    stats = Stats(total_games)

    print(
        f"先手: {first_player.__name__} vs 后手: {second_player.__name__}, 对局数: {total_games}"
    )

    for i in tqdm(range(total_games)):
        if verbose:
            print(f"第 {i + 1}/{total_games} 局")

        state = GameState()
        current_player = 1
        move_count = 0

        start_time = time.time()

        while move_count < max_moves:
            if current_player == 1:
                move = first_player(state, current_player)
            else:
                move = second_player(state, current_player)

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
            state.print_board()

    stats.result_update()

    return stats
