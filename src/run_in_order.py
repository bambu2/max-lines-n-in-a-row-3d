from enum import Enum

from src.algorithms import (
    get_move_random,
    get_move_greedy,
    get_move_advanced,
    get_move_minimax,
    get_move_mcts,
)
from src.state_and_stat import get_stat


class Order(Enum):
    WEAK_FIRST = 1
    STRONG_FIRST = 2
    SAME_LEVEL = 3


def get_total_games(first_player, second_player, order: Order) -> int:
    if order == Order.WEAK_FIRST:
        return 100
    elif order == Order.STRONG_FIRST:
        return 100
    elif order == Order.SAME_LEVEL:
        if (
            first_player.__name__ == "get_move_random"
            and second_player.__name__ == "get_move_random"
        ):
            return 10000  # random vs random is fast, so increase the number of games
        elif (
            first_player.__name__ == "get_move_minimax"
            and second_player.__name__ == "get_move_minimax"
        ):
            return 10  # minimax vs minimax is slow, so reduce the number of games
        elif (
            first_player.__name__ == "get_move_mcts"
            and second_player.__name__ == "get_move_mcts"
        ):
            return 10  # mcts vs mcts is slow, so reduce the number of games
        return 100
    else:
        return 100


def run_in_order(order: Order, verbose=False):
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


def run(first_player, second_player, order: Order, verbose=False):
    total_games = get_total_games(first_player, second_player, order)
    if total_games == 0:
        return
    stats = get_stat(
        first_player, second_player, total_games=total_games, verbose=verbose
    )
    stats.print_stats()
