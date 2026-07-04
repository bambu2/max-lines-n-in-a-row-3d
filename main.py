from .src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
)
from .src.utils import run_multiple_games, print_stats, run_ai_vs_ai


def main():
    print("Hello from 3x3x3-tic-tac-toe-without-the-center-cell!")

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

    """
    print("⚔️ 比较AI性能...")

    stats_comparison = run_ai_vs_ai(
        get_ai_move_random,  # AI1（先手）
        get_ai_move_greedy,  # AI2（后手）
        num_games=50,
    )

    print(f"\n⚔️ 高级AI vs 贪心AI (50局)")
    print(
        f"  随机AI胜: {stats_comparison['wins_ai1']} ({stats_comparison['win_rate_ai1']:.1f}%)"
    )
    print(
        f"  贪心AI胜: {stats_comparison['wins_ai2']} ({stats_comparison['win_rate_ai2']:.1f}%)"
    )
    print(f"  平局: {stats_comparison['draws']} ({stats_comparison['draw_rate']:.1f}%)")
    print(
        f"  平均得分: 随机AI {stats_comparison['avg_score_ai1']:.2f} vs 贪心AI {stats_comparison['avg_score_ai2']:.2f}"
    )"""


if __name__ == "__main__":
    main()
