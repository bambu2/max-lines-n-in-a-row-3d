from src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
    get_ai_move_mcts,
)

from src.utils import run_ai_vs_ai, print_stats


def multiple_ai_test(weak_first=True):
    ai_func_list = [
        get_ai_move_random,
        get_ai_move_greedy,
        get_ai_move_advanced,
        get_ai_move_minimax,
        get_ai_move_mcts,
    ]
    num_games = 100  # 每对AI之间的对局数
    try:
        if weak_first:
            for i in range(len(ai_func_list)):
                for j in range(i + 1, len(ai_func_list)):
                    ai1 = ai_func_list[i]
                    ai2 = ai_func_list[j]
                    stats = run_ai_vs_ai(
                        ai1,
                        ai2,
                        num_games=num_games,
                    )
                    print(
                        f"AI1: {ai1.__name__} vs AI2: {ai2.__name__}, 对局数: {num_games}"
                    )
                    print_stats(stats, verbose=False)
        else:
            for i in range(len(ai_func_list)):
                for j in range(i + 1, len(ai_func_list)):
                    ai1 = ai_func_list[i]
                    ai2 = ai_func_list[j]
                    stats = run_ai_vs_ai(
                        ai2,
                        ai1,
                        num_games=num_games,
                    )
                    print(
                        f"AI1: {ai2.__name__} vs AI2: {ai1.__name__}, 对局数: {num_games}"
                    )
                    print_stats(stats, verbose=False)

    except Exception as e:
        print(f"An error occurred: {e}")
