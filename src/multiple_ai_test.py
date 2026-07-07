from src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
    get_ai_move_mcts,
)

from src.utils import run_ai_vs_ai, print_stats


def multiple_ai_test():
    random_vs_greedy_stats = run_ai_vs_ai(
        get_ai_move_random,  # AI1（先手）
        get_ai_move_greedy,  # AI2（后手）
        num_games=100,
    )

    print_stats(random_vs_greedy_stats)
