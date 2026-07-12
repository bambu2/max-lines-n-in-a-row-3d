def xyz_to_idx(layer, row, col):
    return layer * 9 + row * 3 + col


def idx_to_xyz(idx):
    layer = idx // 9
    row = (idx % 9) // 3
    col = idx % 3
    return layer, row, col


def rate_to_percentage(rate):
    return f"{rate * 100:.1f}%"


def print_stats(stats) -> None:
    print("🏆 胜负统计:")
    print(f"  玩家A胜: {stats.wins_A} ({rate_to_percentage(stats.win_rate_A)})")
    print(f"  玩家B胜: {stats.wins_B} ({rate_to_percentage(stats.win_rate_B)})")
    print(f"  平局:    {stats.draws} ({rate_to_percentage(stats.draw_rate)})")
    print()
    print("📈连线数统计:")
    print("  玩家 A 连线数")
    print(
        f"    最高: {max(stats.score_A_list)}, 最低: {min(stats.score_A_list)}, 平均: {stats.avg_score_A:.2f}"
    )
    print("  玩家 B 连线数")
    print(
        f"    最高: {max(stats.score_B_list)}, 最低: {min(stats.score_B_list)}, 平均: {stats.avg_score_B:.2f}"
    )
    print(f"  平均连线数差: {stats.avg_score_A - stats.avg_score_B:.2f}")
    print()
    print(f"  平均每局耗时: {stats.avg_time:.4f}秒")
    print(f"  总耗时:   {sum(stats.game_times):.2f}秒")
