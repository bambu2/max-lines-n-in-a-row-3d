import random
import math
import copy

from src.utils import State


class MCTSNode:
    """MCTS 节点"""

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.player_to_move = 1  # 默认当前玩家为1
        self.untried_moves = state.get_valid_moves() if state else []

    def is_fully_expanded(self):
        """检查是否所有合法走法都已尝试"""
        return len(self.untried_moves) == 0

    def is_terminal(self):
        """检查游戏是否结束"""
        if self.state is None:
            return True
        return self.state.is_terminal()

    def best_child(self, exploration_constant=1.41):
        if not self.children:
            return None, -float("inf")

        # 优先选择未访问的子节点
        for child in self.children:
            if child.visits == 0:
                return child, float("inf")

        # 计算UCT
        best_child = None
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
    """蒙特卡洛树搜索"""

    def __init__(self, state, iterations=500, exploration_constant=1.41):
        """
        初始化 MCTS

        Args:
            state: State 对象
            iterations: 模拟次数
            exploration_constant: 探索常数（越大越倾向于探索）
        """
        if state is None:
            raise Exception("state 不能为 None")

        self.root = MCTSNode(state)
        self.iterations = max(1, iterations)  # 至少1次
        self.exploration_constant = exploration_constant
        self.current_player = 1  # 默认当前玩家

    def search(self):
        """
        执行 MCTS 搜索，返回最佳走法

        Returns:
            int: 最佳走法的索引，如果没有合法走法返回 None
        """
        # ========== 防御1：检查根节点 ==========
        if self.root is None:
            print("❌ 错误：根节点为 None")
            return None

        # ========== 防御2：检查是否终局 ==========
        if self.root.is_terminal():
            print("ℹ️ 游戏已结束，没有走法")
            return None

        # ========== 防御3：检查是否有合法走法 ==========
        valid_moves = self.root.state.get_valid_moves()
        if not valid_moves:
            print("ℹ️ 没有合法走法")
            return None

        # ========== 防御4：如果只有一个合法走法，直接返回 ==========
        if len(valid_moves) == 1:
            print(f"ℹ️ 只有一个合法走法: {valid_moves[0]}")
            return valid_moves[0]

        # ========== 执行搜索 ==========
        for iteration in range(self.iterations):
            try:
                # 1. 选择
                node = self._select(self.root)

                # ========== 防御5：检查选择结果 ==========
                if node is None:
                    print(f"⚠️ 第 {iteration} 次迭代：select 返回 None，跳过")
                    continue

                # 2. 扩展
                if not node.is_terminal():
                    node = self._expand(node)

                # ========== 防御6：检查扩展结果 ==========
                if node is None:
                    print(f"⚠️ 第 {iteration} 次迭代：expand 返回 None，跳过")
                    continue

                # 3. 模拟
                winner = self._simulate(node.state, player_to_start=node.player_to_move)

                # 4. 回传
                self._backpropagate(node, winner)

            except Exception as e:
                print(f"⚠️ 第 {iteration} 次迭代出错: {e}")
                continue

        # ========== 选择最佳走法 ==========
        return self._get_best_move()

    def _select(self, node):
        """
        选择阶段：从根节点开始，选择 UCT 最高的子节点

        Returns:
            MCTSNode: 选中的节点，如果没有则返回 None
        """
        # ========== 防御1：检查输入 ==========
        if node is None:
            return None

        # ========== 防御2：如果是终局，返回当前节点 ==========
        if node.is_terminal():
            return node

        # ========== 防御3：如果节点未完全展开，返回当前节点 ==========
        if not node.is_fully_expanded():
            return node

        # ========== 防御4：选择最佳子节点 ==========
        best_child, score = node.best_child(self.exploration_constant)

        if best_child is None:
            # 如果没有子节点，返回当前节点
            return node

        # 递归选择
        return self._select(best_child)

    def _expand(self, node):
        if node is None:
            print("⚠️ _expand: node 为 None")
            return None

        # ========== 防御2：检查 node.state ==========
        if node.state is None:
            print("⚠️ _expand: node.state 为 None")
            return node

        # ========== 防御3：检查是否终局 ==========
        if node.is_terminal():
            return node

        # ========== 防御4：检查是否有未尝试的走法 ==========
        if not node.untried_moves:
            return node

        # ========== 防御5：获取合法走法 ==========
        try:
            valid_moves = node.state.get_valid_moves()
        except Exception as e:
            print(f"❌ _expand: 获取合法走法失败: {e}")
            return node

        if not valid_moves:
            return node

        # ========== 选择走法 ==========
        # 从 untried_moves 中选一个（确保是合法的）
        move = None
        for m in node.untried_moves:
            if m in valid_moves:
                move = m
                break

        if move is None:
            # 如果没有合法走法，更新 untried_moves
            node.untried_moves = valid_moves.copy()
            if not node.untried_moves:
                return node
            move = node.untried_moves[0]

        # 从 untried_moves 中移除
        try:
            node.untried_moves.remove(move)
        except ValueError:
            # 如果 move 不在列表中，跳过
            return node

        # ========== 创建新状态 ==========
        try:
            new_state = self._copy_state(node.state)
            if new_state is None:
                print("❌ _expand: 复制状态失败")
                return node

            # 计算当前玩家 - 使用 node.player_to_move 而不是 self.current_player
            current_player = node.player_to_move
            success = new_state.make_move(move, current_player)
            if not success:
                print(f"❌ _expand: 走法 {move} 执行失败")
                return node

        except Exception as e:
            print(f"❌ _expand: 创建新状态失败: {e}")
            return node

        try:
            child_node = MCTSNode(new_state, parent=node, move=move)
            child_node.player_to_move = -current_player
            node.children.append(child_node)
        except Exception as e:
            print(f"❌ _expand: 创建子节点失败: {e}")
            return node

        return child_node

    def _simulate(self, state, player_to_start) -> int:
        """
        模拟阶段：从当前状态开始随机下到终局

        Returns:
            int: 获胜玩家 (1: A赢, -1: B赢, 0: 平局)
        """
        # ========== 防御1：检查输入 ==========
        if state is None:
            print("⚠️ _simulate: state 为 None")
            return 0

        # ========== 防御2：快速拷贝 ==========
        try:
            sim_state = self._copy_state(state)
            if sim_state is None:
                print("⚠️ _simulate: 复制状态失败")
                return 0
        except Exception as e:
            print(f"⚠️ _simulate: 复制状态异常: {e}")
            return 0

        # ========== 防御3：检查 sim_state 是否有效 ==========
        if sim_state is None:
            return 0

        player = player_to_start

        # ========== 防御4：限制模拟步数 ==========
        try:
            max_steps = 26 - sim_state.move_count
        except AttributeError:
            print("⚠️ _simulate: sim_state 缺少 move_count 属性")
            return 0

        if max_steps <= 0:
            # 已经结束，直接判断胜负
            return self._get_winner(sim_state)

        # ========== 随机模拟 ==========
        steps = 0
        max_sim_steps = min(max_steps, 30)  # 最多模拟30步，防止死循环

        while sim_state.move_count < 26 and steps < max_sim_steps:
            try:
                valid_moves = sim_state.get_valid_moves()
            except Exception as e:
                print(f"⚠️ _simulate: 获取合法走法失败: {e}")
                break

            if not valid_moves:
                break

            # 随机走一步
            move = random.choice(valid_moves)

            try:
                sim_state.make_move(move, player)
            except Exception as e:
                print(f"⚠️ _simulate: 执行走法失败: {e}")
                break

            player = -player
            steps += 1

        # ========== 判断胜负 ==========
        return self._get_winner(sim_state)

    def _backpropagate(self, node, winner):
        current = node
        while current is not None:
            current.visits += 1
            if winner == current.player_to_move:
                current.wins += 1
            current = current.parent

    def _get_best_move(self):
        """
        从根节点的子节点中选择访问次数最多的走法

        Returns:
            int: 最佳走法的索引，如果没有则返回 None
        """
        if self.root is None:
            return None

        if not self.root.children:
            # 如果没有子节点，从根节点获取合法走法
            valid_moves = self.root.state.get_valid_moves()
            return valid_moves[0] if valid_moves else None

        best_child = max(
            self.root.children, key=lambda c: c.wins / c.visits if c.visits > 0 else 0
        )

        if best_child is None:
            valid_moves = self.root.state.get_valid_moves()
            return valid_moves[0] if valid_moves else None

        return best_child.move

    def _copy_state(self, state):
        """
        拷贝 GameState

        Args:
            state: 原始 GameState

        Returns:
            GameState: 拷贝的新状态
        """
        # ========== 防御 ==========
        if state is None:
            return None

        # ========== 使用深拷贝确保完全独立 ==========
        try:
            new_state = copy.deepcopy(state)
            return new_state
        except Exception as e:
            print(f"⚠️ _copy_state: 深拷贝失败: {e}")
            # 如果深拷贝失败，尝试手动拷贝
            new_state = State()
            if hasattr(state, "board"):
                new_state.board = state.board.copy()
            if hasattr(state, "score_A"):
                new_state.score_A = state.score_A
            if hasattr(state, "score_B"):
                new_state.score_B = state.score_B
            if hasattr(state, "move_count"):
                new_state.move_count = state.move_count
            return new_state

    def _get_winner(self, state):
        if state is None:
            return 0

        if hasattr(state, "is_terminal") and not state.is_terminal():
            return 0

        # 根据分数判断
        if hasattr(state, "score_A") and hasattr(state, "score_B"):
            if state.score_A > state.score_B:
                return 1
            elif state.score_B > state.score_A:
                return -1

        return 0


def get_move_mcts(state, player, iterations=500):
    """
    MCTS AI 主函数

    Args:
        state: GameState 对象
        player: 当前玩家 (1 或 -1)
        iterations: MCTS 迭代次数

    Returns:
        int: 最佳走法索引，如果没有则返回 None
    """
    if state is None:
        print("❌ 错误：state 为 None")
        return None

    valid_moves = state.get_valid_moves()
    if not valid_moves:
        print("ℹ️ 没有合法走法")
        return None

    if len(valid_moves) == 1:
        return valid_moves[0]

    try:
        mcts = MCTS(state, iterations=iterations)
        mcts.current_player = player
        best_move = mcts.search()

        if best_move is None:
            return valid_moves[0]

        return best_move

    except Exception as e:
        print(f"❌ MCTS 搜索失败: {e}")
        return valid_moves[0] if valid_moves else None
