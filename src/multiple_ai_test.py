from src.ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
    get_ai_move_mcts,
)

from src.utils import run_ai_vs_ai


def multiple_ai_test():
    random_vs_greedy_stats = run_ai_vs_ai(
        get_ai_move_random,  # AI1（先手）
        get_ai_move_greedy,  # AI2（后手）
        num_games=100,
    )

    print(f"\n⚔️ 随机AI vs 贪心AI (100局)")
    print(
        f"  随机AI胜: {random_vs_greedy_stats['wins_ai1']} ({random_vs_greedy_stats['win_rate_ai1']:.1f}%)"
    )
    print(
        f"  贪心AI胜: {random_vs_greedy_stats['wins_ai2']} ({random_vs_greedy_stats['win_rate_ai2']:.1f}%)"
    )
    print(
        f"  平局: {random_vs_greedy_stats['draws']} ({random_vs_greedy_stats['draw_rate']:.1f}%)"
    )
    print(
        f"  平均得分: 随机AI {random_vs_greedy_stats['avg_score_ai1']:.2f} vs 贪心AI {random_vs_greedy_stats['avg_score_ai2']:.2f}"
    )
