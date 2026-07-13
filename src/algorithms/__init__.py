"""
AI算法模块。

提供5种不同强度的井字棋AI策略：

1. **get_move_random** - 随机策略
    - 从合法位置中随机选择
    - 最简单的策略，无任何决策逻辑

2. **get_move_greedy** - 贪心策略
    - 选择能立即形成最多线的位置
    - 包含基本防守逻辑（优先阻止对手成线）

3. **get_move_advanced** - 高级启发式策略
    - 使用评估函数评估每个位置的潜力
    - 综合进攻得分、防守得分和位置加成
    - 支持多步预判（差一步完成线的威胁识别）

4. **get_move_minimax** - 极小极大策略
    - 使用带alpha-beta剪枝的minimax算法
    - 搜索深度为4层
    - 从玩家1视角评估，正数有利于玩家1

5. **get_move_mcts** - 蒙特卡洛树搜索策略
    - 使用UCT算法进行节点选择
    - 默认迭代500次
    - 包含选择、扩展、模拟、回传四个阶段

所有策略函数签名：(state: GameState, player: int) -> int | None
"""

from src.algorithms.random import get_move_random
from src.algorithms.greedy import get_move_greedy
from src.algorithms.advanced import get_move_advanced
from src.algorithms.minimax import get_move_minimax
from src.algorithms.mcts import get_move_mcts

__all__ = [
    "get_move_random",
    "get_move_greedy",
    "get_move_advanced",
    "get_move_minimax",
    "get_move_mcts",
]
