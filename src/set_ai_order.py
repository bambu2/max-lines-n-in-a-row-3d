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


def get_num_games(ai1, ai2, order: Order) -> int:
    if order == Order.WEAK_FIRST:
        return 100
    elif order == Order.STRONG_FIRST:
        return 100
    elif order == Order.SAME_LEVEL:
        if ai1.__name__ == "get_move_minimax" and ai2.__name__ == "get_move_minimax":
            return 10  # minimax vs minimax is slow, so reduce the number of games
        elif ai1.__name__ == "get_move_mcts" and ai2.__name__ == "get_move_mcts":
            return 10  # mcts vs mcts is slow, so reduce the number of games
        return 100
    else:
        return 100


def set_ai_order(order: Order, verbose=False):
    ai_func_list = [
        get_move_random,
        get_move_greedy,
        get_move_advanced,
        get_move_minimax,
        get_move_mcts,
    ]
    try:
        if order == Order.WEAK_FIRST:
            for i in range(len(ai_func_list)):
                for j in range(i + 1, len(ai_func_list)):
                    ai1 = ai_func_list[i]
                    ai2 = ai_func_list[j]
                    run(ai1, ai2, order, verbose=verbose)
        elif order == Order.STRONG_FIRST:
            for i in range(len(ai_func_list)):
                for j in range(i + 1, len(ai_func_list)):
                    ai1 = ai_func_list[j]
                    ai2 = ai_func_list[i]
                    run(ai1, ai2, order, verbose=verbose)
        elif order == Order.SAME_LEVEL:
            for i in range(len(ai_func_list)):
                ai1 = ai_func_list[i]
                ai2 = ai_func_list[i]
                run(ai1, ai2, order, verbose=verbose)
    except Exception as e:
        print(f"An error occurred: {e}")


def run(ai1, ai2, order, verbose=False):
    num_games = get_num_games(ai1, ai2, order)
    if num_games == 0:
        return
    stats = run_ai1_vs_ai2(ai1, ai2, total_games=num_games, verbose=verbose)
    print(f"AI1: {ai1.__name__} vs AI2: {ai2.__name__}, 对局数: {num_games}")
    print_stats(stats, verbose=verbose)
