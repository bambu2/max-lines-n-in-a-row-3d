"""
游戏状态和统计模块。

包含：
- GameState: 3x3x3 井字棋游戏状态管理（移除中心位置）
- Stat: 对局统计数据类
- get_stat: 运行多局对弈并收集统计信息
"""

import time
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from max_lines_n_in_a_row_3d.config import settings
from max_lines_n_in_a_row_3d.logger import get_logger
from max_lines_n_in_a_row_3d.utils import coord_to_idx, idx_to_coord, rate_to_percentage

logger = get_logger(__name__)


class GameState:
    """
    3x3x3 井字棋游戏状态类（移除中心位置）。

    棋盘结构：
    - 3层 × 3行 × 3列 = TOTAL_CELLS_COUNT 个位置
    - 中心位置 (1,1,1) 即索引 13 被禁止使用
    - 实际可用位置：MAX_MOVE_COUNT 个

    玩家标记：
    - 0: 空位
    - 1: 先手玩家（玩家A）
    - -1: 后手玩家（玩家B）

    胜负判定：
    - 完成一条线（3个连续同色棋子）得1分
    - 线的类型：X轴方向、Y轴方向、Z轴方向、平面对角线、体对角线
    - 不含中心位置的线才有效
    - 游戏结束时得分高者获胜，得分相同为平局
    """

    def __init__(self):
        """初始化游戏状态。"""
        self.board: list = [0] * settings.total_cells  # 0=空, 1=玩家A, -1=玩家B
        self.score_first_player: int = 0  # 先手玩家得分
        self.score_second_player: int = 0  # 后手玩家得分
        self.move_count: int = 0  # 已落子数
        self.current_player: int = 1  # 当前玩家（1或-1）
        self.move_history: list = []  # 落子历史记录，用于 undo
        self.lines = self._select_lines()  # 有效连线列表
        self.forbidden_indexes = settings.forbidden_indexes  # 禁止使用的中心位置索引
        self._legal_moves = [
            idx
            for idx in range(settings.total_cells)
            if idx not in self.forbidden_indexes
        ]

    def is_legal_move(self, idx: int) -> bool:
        """
        判断指定位置是否为合法落子位置。

        Args:
            idx: 位置索引（0-26）

        Returns:
            bool: True 表示合法（空位且非禁止位置），False 表示非法
        """
        return (self.board[idx] == 0) and (idx in self._legal_moves)

    @property
    def legal_moves(self) -> list[int]:
        """
        获取当前所有合法落子位置。

        Returns:
            list[int]: 合法位置索引列表
        """
        return [idx for idx in self._legal_moves if self.board[idx] == 0]

    def _select_lines(self) -> list[list[int]]:
        """
        筛选出所有不包含中心位置的有效连线。

        Returns:
            list[list[int]]: 有效连线列表，每条连线包含3个位置索引
        """
        all_lines = self._generate_all_lines()
        selected_lines = []

        for line in all_lines:
            if (1, 1, 1) not in line:
                idx_line = [coord_to_idx(*coord) for coord in line]
                selected_lines.append(idx_line)

        return selected_lines

    def _generate_all_lines(self) -> list[list[tuple[int, int, int]]]:
        """
        生成3x3x3棋盘中所有可能的连线。

        Returns:
            list[list[tuple[int, int, int]]]: 所有连线的三维坐标列表
        """
        lines = []

        # 1. X轴方向（每层每行）：9条
        for layer in range(3):
            for row in range(3):
                lines.append([(layer, row, 0), (layer, row, 1), (layer, row, 2)])

        # 2. Y轴方向（每层每列）：9条
        for layer in range(3):
            for column in range(3):
                lines.append(
                    [(layer, 0, column), (layer, 1, column), (layer, 2, column)]
                )

        # 3. Z轴方向（跨层同一位置）：9条
        for row in range(3):
            for column in range(3):
                lines.append([(0, row, column), (1, row, column), (2, row, column)])

        # 4. 平面对角线：18条
        for layer in range(3):
            lines.append([(layer, 0, 0), (layer, 1, 1), (layer, 2, 2)])
            lines.append([(layer, 0, 2), (layer, 1, 1), (layer, 2, 0)])

        for row in range(3):
            lines.append([(0, row, 0), (1, row, 1), (2, row, 2)])
            lines.append([(0, row, 2), (1, row, 1), (2, row, 0)])

        for column in range(3):
            lines.append([(0, 0, column), (1, 1, column), (2, 2, column)])
            lines.append([(0, 2, column), (1, 1, column), (2, 0, column)])

        # 5. 体对角线：4条
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
            "score_first_player_before": self.score_first_player,
            "score_second_player_before": self.score_second_player,
            "player": player,
            "current_player_before": self.current_player,
        }

        self.board[idx] = player
        self.move_count += 1
        self.move_history.append(undo_info)

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
        撤销最后一步落子。

        从 move_history 中恢复之前的状态。

        Returns:
            bool: True 表示撤销成功，False 表示无可撤销的落子
        """
        if not self.move_history:
            return False

        undo_info = self.move_history.pop()
        self.board[undo_info["idx"]] = undo_info["previous_value"]
        self.score_first_player = undo_info["score_first_player_before"]
        self.score_second_player = undo_info["score_second_player_before"]
        self.current_player = undo_info["current_player_before"]
        self.move_count -= 1

        return True

    def undo_move_without_history(
        self,
        idx: int,
        previous_value: int,
        score_first_player_before: int,
        score_second_player_before: int,
    ) -> None:
        """
        手动撤销指定位置的落子，不使用历史记录。

        适用于 minimax 等算法中的临时落子撤销。

        Args:
            idx: 落子位置索引
            previous_value: 该位置之前的值（通常为0）
            score_first_player_before: 先手玩家之前的得分
            score_second_player_before: 后手玩家之前的得分
        """
        self.board[idx] = previous_value
        self.score_first_player = score_first_player_before
        self.score_second_player = score_second_player_before
        self.move_count -= 1

    def is_terminal(self) -> bool:
        """
        判断游戏是否结束。

        游戏结束条件：
        - 所有可用位置都已落子
        - 没有合法落子位置

        Returns:
            bool: True 表示游戏结束，False 表示游戏继续
        """
        return self.move_count >= settings.move_limit or len(self.legal_moves) == 0

    def copy(self) -> GameState:
        """
        创建游戏状态的副本。

        深拷贝 board，浅拷贝只读属性。

        Returns:
            GameState: 游戏状态副本
        """
        new_state = GameState()
        new_state.board = self.board.copy()
        new_state.score_first_player = self.score_first_player
        new_state.score_second_player = self.score_second_player
        new_state.move_count = self.move_count
        new_state.current_player = self.current_player
        return new_state

    def print_board(self) -> None:
        """
        打印当前棋盘状态。

        使用符号表示：
        - ·: 空位
        - X: 玩家1（先手）
        - O: 玩家-1（后手）
        - ✦: 禁止使用的位置
        """
        symbols = {0: "·", 1: "X", -1: "O"}

        for layer in range(3):
            print(f"\n=== 第 {layer + 1} 层 ===")
            for row in range(3):
                line = ""
                for col in range(3):
                    idx = coord_to_idx(layer, row, col)
                    if idx in self.forbidden_indexes:
                        line += " ✦ "
                    else:
                        line += f" {symbols[self.board[idx]]} "
                print(line)


@dataclass(slots=True)
class Stats:
    """
    对局统计数据类。

    记录多局对弈的统计信息，包括胜负次数、得分、耗时等。

    Attributes:
        total_games: 总对局数
        wins_first_player: 先手玩家获胜次数
        wins_second_player: 后手玩家获胜次数
        draws: 平局次数
        scores_first_player: 每局先手玩家得分列表
        scores_second_player: 每局后手玩家得分列表
        avg_score_first_player: 先手玩家平均得分
        avg_score_second_player: 后手玩家平均得分
        avg_time: 平均每局耗时（秒）
        win_rate_first_player: 先手玩家胜率（0-1）
        win_rate_second_player: 后手玩家胜率（0-1）
        draw_rate: 平局率（0-1）
        total_time: 每局耗时列表（秒）
    """

    total_games: int
    wins_first_player: int = 0
    wins_second_player: int = 0
    draws: int = 0
    scores_first_player: list[int] = field(default_factory=list)
    scores_second_player: list[int] = field(default_factory=list)
    avg_score_first_player: float = 0.0
    avg_score_second_player: float = 0.0
    avg_time: float = 0.0
    win_rate_first_player: float = 0.0
    win_rate_second_player: float = 0.0
    draw_rate: float = 0.0
    total_time: list[float] = field(default_factory=list)

    def update(self, state: GameState, game_time: float) -> None:
        """
        更新单局游戏的统计数据。

        Args:
            state: 游戏结束时的状态
            game_time: 本局耗时（秒）
        """
        self.scores_first_player.append(state.score_first_player)
        self.scores_second_player.append(state.score_second_player)
        self.total_time.append(game_time)

        if state.score_first_player > state.score_second_player:
            self.wins_first_player += 1
        elif state.score_second_player > state.score_first_player:
            self.wins_second_player += 1
        else:
            self.draws += 1

    def result_update(self) -> None:
        """
        计算并更新统计结果（胜率、平均得分、平均耗时）。

        基于已收集的原始数据计算派生统计值。
        """
        if self.total_games <= 0:
            return

        self.avg_score_first_player = sum(self.scores_first_player) / self.total_games
        self.avg_score_second_player = sum(self.scores_second_player) / self.total_games
        self.avg_time = sum(self.total_time) / self.total_games

        self.win_rate_first_player = self.wins_first_player / self.total_games
        self.win_rate_second_player = self.wins_second_player / self.total_games
        self.draw_rate = self.draws / self.total_games

    def print_stats(self) -> None:
        """打印统计结果到控制台。"""
        sns.set_theme()

        df_scores = pd.DataFrame(
            {
                "player": ["first"] * self.total_games + ["second"] * self.total_games,
                "lines": self.scores_first_player + self.scores_second_player,
            }
        )
        _fig, ax = plt.subplots(figsize=(8, 5))
        sns.violinplot(
            data=df_scores,
            x="player",
            y="lines",
            hue="player",
            palette="Set2",
            width=0.8,
            legend=False,
            ax=ax,
        )
        means = [self.avg_score_first_player, self.avg_score_second_player]
        for i, mean_val in enumerate(means):
            ax.text(
                i,
                mean_val,
                f"avg: {mean_val:.2f}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=10,
                color="black",
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.7},
            )
        ax.set_xlabel("player")
        ax.set_ylabel("lines")
        ax.set_title("lines distribution for first and second player")
        plt.show(block=False)
        plt.pause(10)
        plt.close()

        df_wins = pd.DataFrame(
            {
                "result": [
                    "First player win",
                    "Second player win",
                    "Draw",
                ],
                "count": [
                    self.wins_first_player,
                    self.wins_second_player,
                    self.draws,
                ],
            }
        )
        _fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(
            data=df_wins,
            x="result",
            y="count",
            hue="result",
            palette="Set2",
            legend=False,
            ax=ax,
        )
        for i, (_, row) in enumerate(df_wins.iterrows()):
            pct = row["count"] / self.total_games * 100
            ax.text(
                i,
                row["count"],
                f"{row['count']} ({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=10,
            )
        ax.set_xlabel("result")
        ax.set_ylabel("count")
        ax.set_title("win / draw rate")
        plt.show(block=False)
        plt.pause(10)
        plt.close()

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
        if settings.debug:
            logger.debug(f"平均每局耗时: {self.avg_time:.4f}秒")
            logger.debug(f"总耗时: {sum(self.total_time):.2f}秒")


def get_stats(first_player, second_player, total_games: int) -> Stats:
    """
    运行多局对弈并收集统计信息。

    Args:
        first_player: 先手玩家的策略函数，签名为 (state, player) -> int | None
        second_player: 后手玩家的策略函数，签名为 (state, player) -> int | None
        total_games: 总对局数

    Returns:
        Stat: 统计结果对象
    """
    stat = Stats(total_games)

    logger.info(
        f"先手: {first_player.__name__} vs 后手: {second_player.__name__}, 对局数: {total_games}"
    )

    for i in tqdm(range(total_games)):
        if settings.debug:
            logger.debug(f"第 {i + 1}/{total_games} 局")

        state = GameState()
        current_player = 1

        start_time = time.time()

        while not state.is_terminal():
            if current_player == 1:
                move = first_player(state, current_player)
            else:
                move = second_player(state, current_player)

            if move is None:
                break

            state.make_move(move, current_player)
            current_player = -current_player

            if settings.debug:
                print(f"第 {state.move_count} 步: {idx_to_coord(move)}")

        end_time = time.time()
        game_time = end_time - start_time

        stat.update(state, game_time)

        if settings.debug:
            state.print_board()

    stat.result_update()

    return stat
