from src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
    get_ai_move_mcts,
)
from src.utils import run_multiple_games, print_stats


def single_ai_test():
    ai_func_list = [
        get_ai_move_random,
        get_ai_move_greedy,
        get_ai_move_advanced,
        get_ai_move_minimax,
        get_ai_move_mcts,
    ]
    try:
        for ai_func in ai_func_list:
            if ai_func == get_ai_move_random:
                num_games = 10000
            else:
                num_games = 100

            stats = run_multiple_games(
                num_games=num_games, ai_func=ai_func, verbose=False
            )
            print_stats(stats)
    except Exception as e:
        print(f"An error occurred: {e}")
