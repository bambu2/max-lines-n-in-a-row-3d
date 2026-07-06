from .ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
)
from .utils import run_multiple_games, print_stats


def single_ai_test():
    stats_random = run_multiple_games(
        num_games=100000, ai_func=get_ai_move_random, verbose=False
    )
    print_stats(stats_random)

    stats_greedy = run_multiple_games(
        num_games=1, ai_func=get_ai_move_greedy, verbose=True
    )
    print_stats(stats_greedy)

    stats_advanced = run_multiple_games(
        num_games=1, ai_func=get_ai_move_advanced, verbose=True
    )
    print_stats(stats_advanced)

    stats_minimax = run_multiple_games(
        num_games=1, ai_func=get_ai_move_minimax, verbose=True
    )
    print_stats(stats_minimax)
