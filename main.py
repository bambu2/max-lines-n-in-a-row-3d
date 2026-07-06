from .src.single_ai_test import single_ai_test
from .src.multiple_ai_test import multiple_ai_test


def main():
    print("Hello from 3x3x3-tic-tac-toe-without-the-center-cell!")

    single_ai_test()

    multiple_ai_test()

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
