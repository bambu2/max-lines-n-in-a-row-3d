import time
from .game_state import GameState
from .ai_move import (
    get_ai_move_random,
    get_ai_move_greedy,
    get_ai_move_advanced,
    get_ai_move_minimax,
)


def idx_to_xyz(idx):
    return idx // 9, (idx // 3) % 3, idx % 3


def xyz_to_idx(l, r, c):
    return l * 9 + r * 3 + c


def generate_all_lines_no_center():
    """生成所有不经过中心的线，返回索引列表"""
    all_lines = []

    # 使用坐标生成所有线
    coord_lines = generate_coord_lines()  # 返回坐标元组列表

    for line in coord_lines:
        if (1, 1, 1) not in line:  # 排除经过中心的线
            # 将坐标转换为索引
            idx_line = [xyz_to_idx(*coord) for coord in line]
            all_lines.append(idx_line)

    return all_lines


def generate_coord_lines():
    """生成所有49条线的坐标表示"""
    lines = []

    # 1. X轴方向 (每层每行)
    for l in range(3):
        for r in range(3):
            lines.append([(l, r, 0), (l, r, 1), (l, r, 2)])

    # 2. Y轴方向 (每层每列)
    for l in range(3):
        for c in range(3):
            lines.append([(l, 0, c), (l, 1, c), (l, 2, c)])

    # 3. Z轴方向 (跨层)
    for r in range(3):
        for c in range(3):
            lines.append([(0, r, c), (1, r, c), (2, r, c)])

    # 4. 每层对角线 (3层 × 2条)
    for l in range(3):
        lines.append([(l, 0, 0), (l, 1, 1), (l, 2, 2)])
        lines.append([(l, 0, 2), (l, 1, 1), (l, 2, 0)])

    # 5. 跨层对角线
    for r in range(3):
        lines.append([(0, r, 0), (1, r, 1), (2, r, 2)])
        lines.append([(0, r, 2), (1, r, 1), (2, r, 0)])

    for c in range(3):
        lines.append([(0, 0, c), (1, 1, c), (2, 2, c)])
        lines.append([(0, 2, c), (1, 1, c), (2, 0, c)])

    # 6. 体对角线 (4条)
    lines.append([(0, 0, 0), (1, 1, 1), (2, 2, 2)])
    lines.append([(0, 0, 2), (1, 1, 1), (2, 2, 0)])
    lines.append([(0, 2, 0), (1, 1, 1), (2, 0, 2)])
    lines.append([(0, 2, 2), (1, 1, 1), (2, 0, 0)])

    return lines


def print_board(board):
    """打印3x3x3棋盘的当前状态"""
    symbols = {0: "·", 1: "X", -1: "O"}

    for layer in range(3):
        print(f"\n=== 第 {layer + 1} 层 ===")
        for row in range(3):
            line = ""
            for col in range(3):
                idx = layer * 9 + row * 3 + col
                if idx == 13:  # 中心格 (1,1,1)
                    line += " ✦ "  # 用特殊符号标记不可用中心
                else:
                    line += f" {symbols[board[idx]]} "
            print(line)
        print("   " + "-" * 11)


def run_multiple_games(num_games=100, ai_func=None, verbose=False, max_moves=26):
    """
    运行多次对局并统计结果

    Args:
        num_games: 对局次数
        ai_func: AI函数，如果为None则使用随机AI
        verbose: 是否打印每局详细信息
        max_moves: 最大步数（26步，因为中心不可用）

    Returns:
        dict: 统计结果
    """
    stats = {
        "total_games": num_games,
        "wins_A": 0,  # 玩家A胜
        "wins_B": 0,  # 玩家B胜
        "draws": 0,  # 平局
        "score_A_list": [],  # 每局A的得分
        "score_B_list": [],  # 每局B的得分
        "move_counts": [],  # 每局总步数
        "game_times": [],  # 每局耗时（秒）
        "first_player_win": 0,  # 先手胜
        "second_player_win": 0,  # 后手胜
    }
    # 如果没有指定AI，使用随机AI
    if ai_func is None:
        ai_func = get_ai_move_random

    for game_num in range(num_games):
        if verbose:
            print(f"\n{'='*50}")
            print(f"第 {game_num + 1}/{num_games} 局")
            print("=" * 50)

        start_time = time.time()

        # 创建新游戏
        state = GameState()
        current_player = 1  # A先手
        move_count = 0

        # 记录第一步
        first_move = None

        while move_count < max_moves:
            # AI走棋
            move = ai_func(state, current_player)

            if move is None:
                if verbose:
                    print(f"⚠️ 没有合法移动，游戏提前结束")
                break

            if move_count == 0:
                first_move = move

            state.make_move(move, current_player)
            move_count += 1

            if verbose:
                print(
                    f"Step {move_count}: Player {'A' if current_player == 1 else 'B'} -> 位置 {move} ({idx_to_xyz(move)})"
                )

            # 切换玩家
            current_player = -current_player

        end_time = time.time()
        game_time = end_time - start_time

        # 记录数据
        stats["score_A_list"].append(state.score_A)
        stats["score_B_list"].append(state.score_B)
        stats["move_counts"].append(move_count)
        stats["game_times"].append(game_time)

        # 胜负判断
        if state.score_A > state.score_B:
            stats["wins_A"] += 1
            if move_count > 0:  # 先手A获胜
                stats["first_player_win"] += 1
            if verbose:
                print(f"🏆 玩家A获胜！ A: {state.score_A}, B: {state.score_B}")
        elif state.score_B > state.score_A:
            stats["wins_B"] += 1
            if move_count > 0:  # 后手B获胜
                stats["second_player_win"] += 1
            if verbose:
                print(f"🏆 玩家B获胜！ A: {state.score_A}, B: {state.score_B}")
        else:
            stats["draws"] += 1
            if verbose:
                print(f"🤝 平局！ A: {state.score_A}, B: {state.score_B}")

        if verbose:
            print(f"⏱️ 耗时: {game_time:.4f}秒")
            print(
                f"📊 当前统计: A胜{stats['wins_A']}, B胜{stats['wins_B']}, 平局{stats['draws']}"
            )

    # 计算平均值和统计信息
    stats["avg_score_A"] = (
        sum(stats["score_A_list"]) / num_games if num_games > 0 else 0
    )
    stats["avg_score_B"] = (
        sum(stats["score_B_list"]) / num_games if num_games > 0 else 0
    )
    stats["avg_moves"] = sum(stats["move_counts"]) / num_games if num_games > 0 else 0
    stats["avg_time"] = sum(stats["game_times"]) / num_games if num_games > 0 else 0
    stats["win_rate_A"] = stats["wins_A"] / num_games * 100 if num_games > 0 else 0
    stats["win_rate_B"] = stats["wins_B"] / num_games * 100 if num_games > 0 else 0
    stats["draw_rate"] = stats["draws"] / num_games * 100 if num_games > 0 else 0
    stats["first_win_rate"] = (
        stats["first_player_win"] / num_games * 100 if num_games > 0 else 0
    )

    return stats


def print_stats(stats):
    """打印统计结果"""
    print("\n" + "=" * 60)
    print("📊 统计结果")
    print("=" * 60)
    print(f"总对局数: {stats['total_games']}")
    print(f"\n🏆 胜负统计:")
    print(f"  玩家A胜: {stats['wins_A']} ({stats['win_rate_A']:.1f}%)")
    print(f"  玩家B胜: {stats['wins_B']} ({stats['win_rate_B']:.1f}%)")
    print(f"  平局:    {stats['draws']} ({stats['draw_rate']:.1f}%)")
    print(f"\n📈 先手/后手统计:")
    print(f"  先手胜:  {stats['first_player_win']} ({stats['first_win_rate']:.1f}%)")
    print(
        f"  后手胜:  {stats['second_player_win']} ({100 - stats['first_win_rate']:.1f}%)"
    )
    print(f"\n📊 得分统计:")
    print(f"  玩家A平均得分: {stats['avg_score_A']:.2f}")
    print(f"  玩家B平均得分: {stats['avg_score_B']:.2f}")
    print(f"  总得分差:      {stats['avg_score_A'] - stats['avg_score_B']:.2f}")
    print(f"\n⏱️ 步数/时间:")
    print(f"  平均步数: {stats['avg_moves']:.1f}")
    print(f"  平均耗时: {stats['avg_time']:.4f}秒")
    print(f"  总耗时:   {sum(stats['game_times']):.2f}秒")

    # 得分分布（如果有数据）
    if stats["score_A_list"]:
        print(f"\n📊 得分分布:")
        print(
            f"  玩家A - 最高: {max(stats['score_A_list']):.0f}, 最低: {min(stats['score_A_list']):.0f}"
        )
        print(
            f"  玩家B - 最高: {max(stats['score_B_list']):.0f}, 最低: {min(stats['score_B_list']):.0f}"
        )

    print("=" * 60)


def compare_ais(ai1, ai1_name, ai2, ai2_name, num_games=100):
    """
    比较两个AI的胜负

    Args:
        ai1: 第一个AI函数（先手）
        ai1_name: AI1的名称
        ai2: 第二个AI函数（后手）
        ai2_name: AI2的名称
        num_games: 对局次数
    """
    print(f"\n⚔️ AI对战: {ai1_name} vs {ai2_name}")
    print(f"对局数: {num_games}")
    print("-" * 40)

    # 运行对局（使用自定义AI）
    stats = run_multiple_games(num_games, ai_func=None, verbose=False)

    # 但这里需要修改为两个AI交替
    # 更准确的方式：自定义对战逻辑
    stats = run_ai_vs_ai(ai1, ai2, num_games)
    print_stats(stats)


def run_ai_vs_ai(ai1, ai2, num_games=100):
    """
    运行两个AI对战（AI1先手，AI2后手）
    """
    stats = {
        "total_games": num_games,
        "wins_ai1": 0,
        "wins_ai2": 0,
        "draws": 0,
        "score_ai1_list": [],
        "score_ai2_list": [],
        "move_counts": [],
        "game_times": [],
    }

    for game_num in range(num_games):
        state = GameState()
        current_player = 1
        move_count = 0

        start_time = time.time()

        while move_count < 26:
            # 选择AI
            if current_player == 1:
                move = ai1(state, current_player)
            else:
                move = ai2(state, current_player)

            if move is None:
                break

            state.make_move(move, current_player)
            move_count += 1
            current_player = -current_player

        end_time = time.time()

        stats["score_ai1_list"].append(state.score_A)
        stats["score_ai2_list"].append(state.score_B)
        stats["move_counts"].append(move_count)
        stats["game_times"].append(end_time - start_time)

        if state.score_A > state.score_B:
            stats["wins_ai1"] += 1
        elif state.score_B > state.score_A:
            stats["wins_ai2"] += 1
        else:
            stats["draws"] += 1

    # 计算统计信息
    stats["avg_score_ai1"] = sum(stats["score_ai1_list"]) / num_games
    stats["avg_score_ai2"] = sum(stats["score_ai2_list"]) / num_games
    stats["avg_moves"] = sum(stats["move_counts"]) / num_games
    stats["win_rate_ai1"] = stats["wins_ai1"] / num_games * 100
    stats["win_rate_ai2"] = stats["wins_ai2"] / num_games * 100
    stats["draw_rate"] = stats["draws"] / num_games * 100

    return stats
