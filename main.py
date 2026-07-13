"""
3x3x3 井字棋（移除中心位置）AI对弈程序入口。

该程序实现了5种不同强度的AI算法，并支持三种对弈模式：
- WEAK_FIRST: 较弱算法先手，较强算法后手
- STRONG_FIRST: 较强算法先手，较弱算法后手
- SAME_LEVEL: 同一种算法自对弈

运行方式：
    python main.py
"""

from src.run_in_order import run_in_order, Order


def main() -> None:
    """
    程序主函数。

    依次运行三种对弈模式：
    1. WEAK_FIRST: 弱算法先手 vs 强算法后手
    2. STRONG_FIRST: 强算法先手 vs 弱算法后手
    3. SAME_LEVEL: 同算法自对弈
    """
    print("Hello from tic-tac-toe-3x3x3-without-the-center-cell!")
    run_in_order(Order.WEAK_FIRST, verbose=False)
    run_in_order(Order.STRONG_FIRST, verbose=False)
    run_in_order(Order.SAME_LEVEL, verbose=False)


if __name__ == "__main__":
    main()
