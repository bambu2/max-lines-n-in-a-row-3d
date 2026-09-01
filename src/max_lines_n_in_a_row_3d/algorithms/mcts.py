"""
蒙特卡洛树搜索策略模块。

使用MCTS（Monte Carlo Tree Search）算法搜索最优走法，
包含UCT（Upper Confidence Bound for Trees）节点选择策略。
"""

import math
import random

from max_lines_n_in_a_row_3d.config import settings
from max_lines_n_in_a_row_3d.models import GameState


class MCTSNode:
    """
    MCTS节点类。

    每个节点代表一个游戏状态，记录：
    - 状态信息
    - 父节点和子节点
    - 访问次数和胜利次数
    - 即将行动的玩家

    Attributes:
        state: 游戏状态
        parent: 父节点
        move: 到达此节点的走法
        children: 子节点列表
        wins: 胜利次数（从该节点向下模拟获胜的次数）
        visits: 访问次数
        player_to_move: 即将在此节点行动的玩家
        untried_moves: 未尝试的合法走法
    """

    def __init__(self, state: GameState, parent=None, move=None, player_to_move=None):
        """
        初始化MCTS节点。

        Args:
            state: 游戏状态
            parent: 父节点（默认None）
            move: 到达此节点的走法（默认None）
            player_to_move: 即将行动的玩家（默认None）
        """
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0

        if parent is not None and parent.player_to_move is not None:
            self.player_to_move: int | None = -parent.player_to_move
        else:
            self.player_to_move: int | None = player_to_move

        self.untried_moves = list(state.legal_moves) if state else []

    def is_fully_expanded(self) -> bool:
        """
        判断节点是否已完全扩展。

        Returns:
            bool: True表示所有合法走法都已尝试，False表示还有未尝试的走法
        """
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        """
        判断节点是否为终止状态。

        Returns:
            bool: True表示游戏结束，False表示游戏继续
        """
        if self.state is None:
            return True
        return self.state.is_terminal()

    def best_child(
        self, exploration_constant: float = 1.414
    ) -> tuple[MCTSNode | None, float]:
        """
        使用UCT算法选择最优子节点。

        UCT公式: score = win_rate + C * sqrt(ln(parent_visits) / child_visits)
        其中C为探索常数，默认1.414（sqrt(2)）。

        优先选择未访问过的节点（给予无穷大分数）。

        Args:
            exploration_constant: 探索常数（默认1.414）

        Returns:
            tuple[MCTSNode | None, float]: (最优子节点, 分数)，子节点可能为None
        """
        if not self.children:
            return None, -float("inf")

        for child in self.children:
            if child.visits == 0:
                return child, float("inf")

        best_child: MCTSNode | None = None
        best_score = -float("inf")
        for child in self.children:
            win_rate = child.wins / child.visits
            exploration = exploration_constant * math.sqrt(
                math.log(self.visits) / child.visits
            )
            score = win_rate + exploration
            if score > best_score:
                best_score = score
                best_child = child
        return best_child, best_score


class MCTS:
    """
    蒙特卡洛树搜索（MCTS）算法类。

    MCTS包含四个阶段：
    1. **选择（Select）**: 使用UCT算法选择最优子节点，直到找到未完全扩展的节点
    2. **扩展（Expand）**: 创建新的子节点，对应一个未尝试的走法
    3. **模拟（Simulate）**: 从新节点开始随机模拟游戏直到结束
    4. **回传（Backpropagate）**: 将模拟结果反向传播到所有祖先节点

    Attributes:
        root: 根节点
        iterations: 迭代次数（默认500）
        exploration_constant: 探索常数（默认1.414）
        current_player: 当前玩家
    """

    def __init__(
        self,
        state: GameState,
        iterations: int = 500,
        exploration_constant: float = 1.414,
    ):
        """
        初始化MCTS实例。

        Args:
            state: 游戏状态
            iterations: 迭代次数（默认500）
            exploration_constant: 探索常数（默认1.414）

        Raises:
            ValueError: 如果state为None
        """
        if state is None:
            raise ValueError("state 不能为 None")

        self.root = MCTSNode(state, player_to_move=None)
        self.iterations = max(1, iterations)
        self.exploration_constant = exploration_constant
        self.current_player = 1

    def search(self) -> int | None:
        """
        执行MCTS搜索，返回最优走法。

        Returns:
            int | None: 最优走法的位置索引，如果没有合法走法则返回None
        """
        if self.root is None:
            print("❌ 错误：根节点为 None")
            return None

        if self.root.is_terminal():
            print("ℹ️ 游戏已结束，没有走法")
            return None

        valid_moves = self.root.state.legal_moves
        if not valid_moves:
            return None

        if len(valid_moves) == 1:
            return valid_moves[0]

        for iteration in range(self.iterations):
            try:
                node = self._select(self.root)
                if node is None:
                    continue

                if not node.is_terminal():
                    node = self._expand(node)
                    if node is None:
                        continue

                winner = self._simulate(node.state, player_to_start=node.player_to_move)
                self._backpropagate(node, winner)

            except (AttributeError, ValueError, IndexError) as e:
                print(f"⚠️ 第 {iteration} 次迭代出错: {e}")
                continue

        return self._get_best_move()

    def _select(self, node: MCTSNode) -> MCTSNode | None:
        """
        选择阶段：使用UCT算法递归选择最优子节点。

        选择策略：
        - 如果节点是终止状态，返回该节点
        - 如果节点未完全扩展，返回该节点（用于扩展）
        - 否则使用UCT算法选择最优子节点并递归

        Args:
            node: 当前节点

        Returns:
            MCTSNode | None: 选中的节点
        """
        if node is None:
            return None
        if node.is_terminal():
            return node
        if not node.is_fully_expanded():
            return node

        best_child, _ = node.best_child(self.exploration_constant)
        if best_child is None:
            return node
        return self._select(best_child)

    def _expand(self, node: MCTSNode) -> MCTSNode | None:
        """
        扩展阶段：创建新的子节点。

        从节点的未尝试走法中选择一个，创建对应的子节点。

        Args:
            node: 要扩展的节点

        Returns:
            MCTSNode | None: 新创建的子节点，或None（扩展失败）
        """
        if node is None or node.state is None:
            return node

        if node.is_terminal():
            return node

        if not node.untried_moves:
            node.untried_moves = [
                idx
                for idx in node.state.legal_moves
                if not any(c.move == idx for c in node.children)
            ]
            if not node.untried_moves:
                return node

        move = node.untried_moves.pop(0)

        if not node.state.is_legal_move(move):
            return node

        new_state = self._copy_state(node.state)
        if new_state is None:
            return node

        current_player = node.player_to_move
        success = new_state.make_move(move, current_player)
        if not success:
            print(f"❌ 走法 {move} 执行失败")
            return node

        child_node = MCTSNode(new_state, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def _simulate(self, state: GameState, player_to_start: int | None) -> int:
        """
        模拟阶段：从指定状态开始随机模拟游戏直到结束。

        Args:
            state: 模拟开始状态
            player_to_start: 开始模拟的玩家（可能为None）

        Returns:
            int: 模拟结果（1表示玩家1赢，-1表示玩家-1赢，0表示平局）
        """
        if state is None or player_to_start is None:
            return 0

        sim_state = self._copy_state(state)
        if sim_state is None:
            return 0

        player = player_to_start
        max_steps = settings.move_limit - sim_state.move_count
        if max_steps <= 0:
            return self._get_winner(sim_state)

        steps = 0
        max_sim_steps = min(max_steps, 30)
        while sim_state.move_count < settings.move_limit and steps < max_sim_steps:
            valid_moves = sim_state.legal_moves
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            sim_state.make_move(move, player)
            player = -player
            steps += 1

        return self._get_winner(sim_state)

    def _backpropagate(self, node: MCTSNode, winner: int) -> None:
        """
        回传阶段：将模拟结果反向传播到所有祖先节点。

        wins记录「刚落子到达该节点的玩家」的胜场。
        节点的player_to_move是即将行动的玩家，刚落子的是 -player_to_move。

        Args:
            node: 开始回传的节点
            winner: 模拟结果（1表示玩家1赢，-1表示玩家-1赢，0表示平局）
        """
        current = node
        while current is not None:
            current.visits += 1
            if current.player_to_move is not None and winner == -current.player_to_move:
                current.wins += 1
            current = current.parent

    def _get_best_move(self) -> int | None:
        """
        获取最优走法。

        选择胜率最高的子节点对应的走法。

        Returns:
            int | None: 最优走法的位置索引
        """
        if self.root is None or not self.root.children:
            valid_moves = self.root.state.legal_moves
            return valid_moves[0] if valid_moves else None

        best_child = max(
            self.root.children, key=lambda c: c.wins / c.visits if c.visits > 0 else 0
        )
        return best_child.move

    def _copy_state(self, state: GameState) -> GameState | None:
        """
        创建游戏状态的副本。

        Args:
            state: 原游戏状态

        Returns:
            GameState | None: 游戏状态副本
        """
        if state is None:
            return None
        new_state = GameState()
        new_state.board = state.board.copy()
        new_state.score_first_player = state.score_first_player
        new_state.score_second_player = state.score_second_player
        new_state.move_count = state.move_count
        return new_state

    def _get_winner(self, state: GameState) -> int:
        """
        判断游戏的胜者。

        Args:
            state: 游戏状态

        Returns:
            int: 胜者（1表示玩家1赢，-1表示玩家-1赢，0表示平局或未结束）
        """
        if (
            state is None
            or not hasattr(state, "is_terminal")
            or not state.is_terminal()
        ):
            return 0
        if state.score_first_player > state.score_second_player:
            return 1
        elif state.score_second_player > state.score_first_player:
            return -1
        return 0


def mcts_move(state: GameState, player: int, iterations: int = 500) -> int | None:
    """
    MCTS AI 主函数：使用蒙特卡洛树搜索获取最优走法。

    Args:
        state: 当前游戏状态
        player: 当前玩家（1或-1）
        iterations: MCTS迭代次数（默认500）

    Returns:
        int | None: 选中的位置索引，如果没有合法位置则返回None
    """
    if state is None:
        print("❌ 错误：state 为 None")
        return None

    valid_moves = state.legal_moves
    if not valid_moves:
        print("ℹ️ 没有合法走法")
        return None
    if len(valid_moves) == 1:
        return valid_moves[0]

    try:
        mcts = MCTS(state, iterations=iterations)
        mcts.current_player = player
        mcts.root.player_to_move = player
        best_move = mcts.search()

        if best_move is None:
            return valid_moves[0]
        return best_move
    except (AttributeError, ValueError, IndexError) as e:
        print(f"❌ MCTS 搜索失败: {e}")
        return valid_moves[0] if valid_moves else None
