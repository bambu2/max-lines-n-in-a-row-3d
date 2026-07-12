from dataclasses import dataclass

from src.utils import xyz_to_idx


@dataclass()
class GameState:
    board: list = [0] * 27  # 0=空, 1=玩家A, -1=玩家B
    score_A: int = 0
    score_B: int = 0
    move_count: int = 0
    current_player = 1
    move_history = []

    def __init__(self):
        self.lines = self._select_lines()
        self.banned_idx = 13
        self._legal_moves = []

    def _is_legal_move(self, idx) -> bool:
        """检查走法是否合法"""
        if idx not in self._legal_moves:
            return False
        return self.board[idx] == 0

    @property
    def _legal_moves(self):
        return self._legal_moves

    @_legal_moves.setter
    def _legal_moves(self) -> list:
        moves = []
        for idx in range(27):
            if self._is_legal_move:
                moves.append(idx)
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
        if not self._is_legal_move(idx):
            return False

        undo_info = {
            "idx": idx,
            "previous_value": self.board[idx],
            "score_A_before": self.score_A,
            "score_B_before": self.score_B,
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
                    self.score_A += 1
                else:
                    self.score_B += 1
                lines_completed += 1

        self.current_player = -player

        return True

    def undo_move(self):
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
        self.score_A = undo_info["score_A_before"]
        self.score_B = undo_info["score_B_before"]

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
        self.score_A = score_A_before
        self.score_B = score_B_before
        self.move_count -= 1

    def is_terminal(self) -> bool:
        return self.move_count >= 26 or all(pos != 0 for pos in self.board)

    def copy(self):
        new_state = GameState()
        new_state.board = self.board.copy()
        new_state.score_A = self.score_A
        new_state.score_B = self.score_B
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
