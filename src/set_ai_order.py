from enum import Enum

from src.algorithms import (
    get_move_random,
    get_move_greedy,
    get_move_advanced,
    get_move_minimax,
    get_move_mcts,
)
from src.utils import run_ai1_vs_ai2, print_stats


class Order(Enum):
    WEAK_FIRST = 1
    STRONG_FIRST = 2
    SAME_LEVEL = 3


def set_ai_order(AIvsAI_type: Order, verbose=False):
    ai_func_list = [
        get_move_random,
        get_move_greedy,
        get_move_advanced,
        get_move_minimax,
        get_move_mcts,
    ]
    num_games = 100  # 每对AI之间的对局数
    try:
        if AIvsAI_type == Order.WEAK_FIRST:
            for i in range(len(ai_func_list)):
                for j in range(i + 1, len(ai_func_list)):
                    ai1 = ai_func_list[i]
                    ai2 = ai_func_list[j]
                    stats = run_ai1_vs_ai2(
                        ai1,
                        ai2,
                        num_games=num_games,
                    )
                    print(
                        f"AI1: {ai1.__name__} vs AI2: {ai2.__name__}, 对局数: {num_games}"
                    )
                    print_stats(stats, verbose=verbose)
        elif AIvsAI_type == Order.STRONG_FIRST:
            for i in range(len(ai_func_list)):
                for j in range(i + 1, len(ai_func_list)):
                    ai1 = ai_func_list[i]
                    ai2 = ai_func_list[j]
                    stats = run_ai1_vs_ai2(
                        ai2,
                        ai1,
                        num_games=num_games,
                    )
                    print(
                        f"AI1: {ai2.__name__} vs AI2: {ai1.__name__}, 对局数: {num_games}"
                    )
                    print_stats(stats, verbose=verbose)
        elif AIvsAI_type == Order.SAME_LEVEL:
            for i in range(len(ai_func_list)):
                ai1 = ai_func_list[i]
                ai2 = ai_func_list[i]
                stats = run_ai1_vs_ai2(
                    ai1,
                    ai2,
                    num_games=num_games,
                )
                print(
                    f"AI1: {ai1.__name__} vs AI2: {ai2.__name__}, 对局数: {num_games}"
                )
                print_stats(stats, verbose=verbose)
    except Exception as e:
        print(f"An error occurred: {e}")
