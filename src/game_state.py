from utils import generate_all_lines_no_center


class GameState:
    def __init__(self):
        self.board = [0] * 27
        self.lines = generate_all_lines_no_center()
        self.score_A = 0
        self.score_B = 0
        self.move_count = 0
        self.center_idx = 13

    def is_valid_move(self, idx):
        """检查落子是否合法"""
        if idx == self.center_idx:
            return False
        if idx < 0 or idx >= 27:
            return False
        return self.board[idx] == 0

    def make_move(self, idx, player):
        """执行落子，返回是否成功"""
        if not self.is_valid_move(idx):
            return False

        # 落子
        self.board[idx] = player
        self.move_count += 1

        # 检查经过此格的所有线
        for line in self.lines:
            if idx not in line:
                continue

            # 统计这条线的状态
            player_count = 0
            opponent_count = 0
            empty_count = 0

            for pos in line:
                if self.board[pos] == player:
                    player_count += 1
                elif self.board[pos] == -player:
                    opponent_count += 1
                else:
                    empty_count += 1

            # 如果3个都是当前玩家，这条线刚完成
            if player_count == 3 and opponent_count == 0:
                if player == 1:
                    self.score_A += 1
                else:
                    self.score_B += 1

        return True

    def get_valid_moves(self):
        """获取所有合法移动"""
        moves = []
        for idx in range(27):
            if self.is_valid_move(idx):
                moves.append(idx)
        return moves
