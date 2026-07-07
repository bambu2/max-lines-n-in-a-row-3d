from src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
    get_ai_move_mcts,
)
from src.utils import run_multiple_games, print_stats


def single_ai_test():
    stats_random = run_multiple_games(
        num_games=10000, ai_func=get_ai_move_random, verbose=False
    )
    print_stats(stats_random)

    stats_greedy = run_multiple_games(
        num_games=100, ai_func=get_ai_move_greedy, verbose=False
    )
    print_stats(stats_greedy)

    stats_advanced = run_multiple_games(
        num_games=100, ai_func=get_ai_move_advanced, verbose=False
    )
    print_stats(stats_advanced)

    stats_minimax = run_multiple_games(
        num_games=10, ai_func=get_ai_move_minimax, verbose=False
    )
    print_stats(stats_minimax)

    stats_mcts = run_multiple_games(
        num_games=100,
        ai_func=get_ai_move_mcts,
        verbose=False,
    )
    print_stats(stats_mcts)
