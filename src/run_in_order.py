"""
对弈顺序控制模块。

提供不同AI算法之间的对弈安排功能，支持三种对弈模式：
- WEAK_FIRST: 较弱算法先手，较强算法后手
- STRONG_FIRST: 较强算法先手，较弱算法后手
- SAME_LEVEL: 同一种算法自对弈

算法强度排序（从弱到强）：
1. get_move_random - 随机策略
2. get_move_greedy - 贪心策略
3. get_move_advanced - 高级启发式策略
4. get_move_minimax - 极小极大策略（带alpha-beta剪枝）
5. get_move_mcts - 蒙特卡洛树搜索策略
"""

from enum import Enum
from collections.abc import Callable

from src.algorithms import (
    get_move_random,
    get_move_greedy,
    get_move_advanced,
    get_move_minimax,
    get_move_mcts,
)
from src.state_and_stat import get_stat, GameState


class Order(Enum):
    """
    对弈顺序枚举。

    WEAK_FIRST: 较弱算法先手，较强算法后手
    STRONG_FIRST: 较强算法先手，较弱算法后手
    SAME_LEVEL: 同一种算法自对弈
    """

    WEAK_FIRST = 1
    STRONG_FIRST = 2
    SAME_LEVEL = 3


def get_total_games(
    first_player: Callable[[GameState, int], int | None],
    second_player: Callable[[GameState, int], int | None],
    order: Order,
) -> int:
    """
    根据对弈双方和模式确定对局数。

    不同组合的对局数策略：
    - 一般情况：100局
    - random vs random：10000局（速度快，增加样本量）
    - minimax vs minimax：10局（速度慢，减少对局数）
    - mcts vs mcts：10局（速度慢，减少对局数）
    - 非同一种算法的 SAME_LEVEL：0局（不执行）

    Args:
        first_player: 先手玩家策略函数
        second_player: 后手玩家策略函数
        order: 对弈顺序模式

    Returns:
        int: 对局数
    """
    if order == Order.WEAK_FIRST:
        return 100
    elif order == Order.STRONG_FIRST:
        return 100
    elif order == Order.SAME_LEVEL:
        if (
            first_player.__name__ == "get_move_random"
            and second_player.__name__ == "get_move_random"
        ):
            return 10000
        elif (
            first_player.__name__ == "get_move_minimax"
            and second_player.__name__ == "get_move_minimax"
        ):
            return 10
        elif (
            first_player.__name__ == "get_move_mcts"
            and second_player.__name__ == "get_move_mcts"
        ):
            return 10
        return 0
    else:
        return 100


def run_in_order(order: Order, verbose: bool = False) -> None:
    """
    按指定顺序运行所有算法对弈。

    Args:
        order: 对弈顺序模式
        verbose: 是否打印每局详细信息（默认 False）
    """
    fn_list = [
        get_move_random,
        get_move_greedy,
        get_move_advanced,
        get_move_minimax,
        get_move_mcts,
    ]
    try:
        if order == Order.WEAK_FIRST:
            for i in range(len(fn_list)):
                for j in range(i + 1, len(fn_list)):
                    first_player = fn_list[i]
                    second_player = fn_list[j]
                    run(first_player, second_player, order, verbose=verbose)
        elif order == Order.STRONG_FIRST:
            for i in range(len(fn_list)):
                for j in range(i + 1, len(fn_list)):
                    first_player = fn_list[j]
                    second_player = fn_list[i]
                    run(first_player, second_player, order, verbose=verbose)
        elif order == Order.SAME_LEVEL:
            for i in range(len(fn_list)):
                first_player = fn_list[i]
                second_player = fn_list[i]
                run(first_player, second_player, order, verbose=verbose)
    except Exception as e:
        print(f"An error occurred: {e}")


def run(
    first_player: Callable[[GameState, int], int | None],
    second_player: Callable[[GameState, int], int | None],
    order: Order,
    verbose: bool = False,
) -> None:
    """
    执行一组对弈并打印统计结果。

    Args:
        first_player: 先手玩家策略函数
        second_player: 后手玩家策略函数
        order: 对弈顺序模式
        verbose: 是否打印每局详细信息（默认 False）
    """
    total_games = get_total_games(first_player, second_player, order)
    if total_games == 0:
        return
    stats = get_stat(
        first_player, second_player, total_games=total_games, verbose=verbose
    )
    stats.print_stats()
