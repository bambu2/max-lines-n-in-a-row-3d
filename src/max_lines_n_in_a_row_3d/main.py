"""
空心立方井字棋程序入口

该程序实现了5种不同强度的AI算法，并支持三种对弈模式：
- WEAK_FIRST: 较弱算法先手，较强算法后手
- STRONG_FIRST: 较强算法先手，较弱算法后手
- SAME_LEVEL: 同一种算法自对弈

运行方式：
    python main.py
"""

from src.run_match import Order, run_match


def main() -> None:
    """
    程序主函数。

    依次运行三种对弈模式：
    1. WEAK_FIRST: 弱算法先手 vs 强算法后手
    2. STRONG_FIRST: 强算法先手 vs 弱算法后手
    3. SAME_LEVEL: 同算法自对弈
    """

    try:
        run_match(Order.WEAK_FIRST, verbose=False)
        run_match(Order.STRONG_FIRST, verbose=False)
        run_match(Order.SAME_LEVEL, verbose=False)
    except KeyboardInterrupt:
        print("程序被用户中断")


if __name__ == "__main__":
    main()
