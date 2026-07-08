from src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
    get_ai_move_mcts,
)

from src.utils import run_ai_vs_ai, print_stats


def multiple_ai_test():
    ai_func_list = [
        get_ai_move_random,
        get_ai_move_greedy,
        get_ai_move_advanced,
        get_ai_move_minimax,
        get_ai_move_mcts,
    ]
    try:
        for i in range(len(ai_func_list)):
            for j in range(i + 1, len(ai_func_list)):
                ai1 = ai_func_list[i]
                ai2 = ai_func_list[j]
                stats = run_ai_vs_ai(
                    ai1,  # AI1（先手）
                    ai2,  # AI2（后手）
                    num_games=100,
                )
                print_stats(stats)
    except Exception as e:
        print(f"An error occurred: {e}")
