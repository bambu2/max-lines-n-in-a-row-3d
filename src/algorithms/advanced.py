"""
高级启发式策略模块。

使用评估函数评估每个位置的潜力，综合进攻、防守和位置因素。
"""

from src.config import COLUMN_COUNT, LAYER_COUNT, ROW_COUNT
from src.state_and_stats import GameState
from src.utils import idx_to_xyz


def get_move_advanced(state: GameState, player: int) -> int | None:
    """
    高级启发式策略：使用评估函数选择潜力最高的位置。

    评分规则：
    - 进攻得分：
        - 差一步完成线（已有2子）：+100
        - 已有1子：+10
        - 空位（可发展）：+1
        - 线中有对手棋子则不计分
    - 防守得分：
        - 对手差一步完成线（已有2子）：+80
        - 对手已有1子：+5
        - 线中有己方棋子则不计分
    - 位置加成：
        - 角格（layer, row, col 都为0或2）：+3
        - 边心格（有一个坐标为1）：+2

    Args:
        state: 当前游戏状态
        player: 当前玩家（1或-1）

    Returns:
        int | None: 选中的位置索引，如果没有合法位置则返回None
    """
    best_score = -999
    best_move = None

    for idx in state.legal_moves:
        offense_score = 0
        for line in state.lines:
            if idx not in line:
                continue

            vals = [state.board[i] for i in line]

            if any(v == -player for v in vals):
                continue

            your_count = sum(1 for v in vals if v == player)
            empty_count = sum(1 for v in vals if v == 0)

            if empty_count > 0:
                if your_count == 2:
                    offense_score += 100
                elif your_count == 1:
                    offense_score += 10
                else:
                    offense_score += 1

        defense_score = 0
        for line in state.lines:
            if idx not in line:
                continue

            vals = [state.board[i] for i in line]

            if any(v == player for v in vals):
                continue

            opponent_count = sum(1 for v in vals if v == -player)
            empty_count = sum(1 for v in vals if v == 0)

            if empty_count > 0:
                if opponent_count == 2:
                    defense_score += 80
                elif opponent_count == 1:
                    defense_score += 5

        position_bonus = 0
        layer, row, column = idx_to_xyz(idx)
        if (
            layer in (0, LAYER_COUNT - 1)
            and row in (0, ROW_COUNT - 1)
            and column in (0, COLUMN_COUNT - 1)
        ):
            position_bonus = 3
        elif (
            (
                layer not in (0, LAYER_COUNT - 1)
                and row in (0, ROW_COUNT - 1)
                and column in (0, COLUMN_COUNT - 1)
            )
            or (
                row not in (0, ROW_COUNT - 1)
                and layer in (0, LAYER_COUNT - 1)
                and column in (0, COLUMN_COUNT - 1)
            )
            or (
                column not in (0, COLUMN_COUNT - 1)
                and layer in (0, LAYER_COUNT - 1)
                and row in (0, ROW_COUNT - 1)
            )
        ):
            position_bonus = 2
        else:
            position_bonus = 0

        total_score = offense_score + defense_score + position_bonus

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move
