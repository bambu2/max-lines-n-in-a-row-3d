import random
import math

from src.utils import GameState


class MCTSNode:
    """MCTS 节点（修复逻辑）"""

    def __init__(self, state: GameState, parent=None, move=None, player_to_move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0

        if parent is not None:
            self.player_to_move = -parent.player_to_move
        else:
            # 根节点，由外部设置（MCTS 初始化时赋值）
            self.player_to_move = player_to_move

        # 初始化未尝试走法
        self.untried_moves = state.get_valid_moves() if state else []

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        if self.state is None:
            return True
        return self.state.is_terminal()

    def best_child(self, exploration_constant=1.414):
        if not self.children:
            return None, -float("inf")

        # 优先选择未访问过的节点
        for child in self.children:
            if child.visits == 0:
                return child, float("inf")

        # 计算 UCT
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
    def __init__(self, state, iterations=500, exploration_constant=1.41):
        if state is None:
            raise ValueError("state 不能为 None")

        # ✅ 根节点先创建，player_to_move 初始为 None，后续由外部设置
        self.root = MCTSNode(state, player_to_move=None)
        self.iterations = max(1, iterations)
        self.exploration_constant = exploration_constant
        self.current_player = 1  # 占位，后续会由 get_move_mcts 赋值

    def search(self):
        if self.root is None:
            print("❌ 错误：根节点为 None")
            return None

        if self.root.is_terminal():
            print("ℹ️ 游戏已结束，没有走法")
            return None

        valid_moves = self.root.state.get_valid_moves()
        if not valid_moves:
            return None

        if len(valid_moves) == 1:
            return valid_moves[0]

        for iteration in range(self.iterations):
            try:
                # 1. 选择
                node = self._select(self.root)
                if node is None:
                    continue

                # 2. 扩展
                if not node.is_terminal():
                    node = self._expand(node)
                    if node is None:
                        continue

                # 3. 模拟（从 node 状态的玩家开始）
                winner = self._simulate(node.state, player_to_start=node.player_to_move)

                # 4. 回传
                self._backpropagate(node, winner)

            except Exception as e:
                print(f"⚠️ 第 {iteration} 次迭代出错: {e}")
                continue

        return self._get_best_move()

    def _select(self, node):
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

    def _expand(self, node):
        if node is None or node.state is None:
            return node

        if node.is_terminal():
            return node

        # ✅ 确保有未尝试的走法
        if not node.untried_moves:
            # 若意外为空则重新同步合法走法（防御性编程）
            node.untried_moves = node.state.get_valid_moves()
            if not node.untried_moves:
                return node

        # 选择一个未尝试的走法
        move = node.untried_moves.pop(0)  # 用 pop 保证移除
        # 确认走法仍合法（避免状态被外部修改）
        if move not in node.state.get_valid_moves():
            return node  # 该走法已非法，返回节点下次再尝试其他

        # ✅ 创建子状态，使用当前节点的玩家来执行走法
        new_state = self._copy_state(node.state)
        if new_state is None:
            return node

        # ✅ 核心修正：使用 node.player_to_move 执行走法
        current_player = node.player_to_move
        success = new_state.make_move(move, current_player)
        if not success:
            print(f"❌ 走法 {move} 执行失败")
            return node

        # ✅ 创建子节点，子节点的 player_to_move 会在构造函数中自动设为 -current_player
        child_node = MCTSNode(new_state, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def _simulate(self, state, player_to_start) -> int:
        if state is None:
            return 0

        sim_state = self._copy_state(state)
        if sim_state is None:
            return 0

        player = player_to_start
        max_steps = 26 - sim_state.move_count  # 最多总步数 26
        if max_steps <= 0:
            return self._get_winner(sim_state)

        steps = 0
        max_sim_steps = min(max_steps, 30)  # 防死循环
        while sim_state.move_count < 26 and steps < max_sim_steps:
            valid_moves = sim_state.get_valid_moves()
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            sim_state.make_move(move, player)
            player = -player
            steps += 1

        return self._get_winner(sim_state)

    def _backpropagate(self, node, winner):
        current = node
        while current is not None:
            current.visits += 1
            # ✅ 修正：节点视角是“轮到 player_to_move 行动”，若胜者正是该玩家则加胜场
            if winner == current.player_to_move:
                current.wins += 1
            current = current.parent

    def _get_best_move(self):
        if self.root is None or not self.root.children:
            # 无子节点时，随便返回一个合法走法
            valid_moves = self.root.state.get_valid_moves()
            return valid_moves[0] if valid_moves else None

        # 选胜率最高的孩子（若访问量为 0，胜率视为 0）
        best_child = max(
            self.root.children, key=lambda c: c.wins / c.visits if c.visits > 0 else 0
        )
        return best_child.move

    def _copy_state(self, state):
        """浅拷贝 + 深拷贝列表"""
        if state is None:
            return None
        new_state = GameState()
        new_state.board = state.board.copy()
        new_state.score_A = state.score_A
        new_state.score_B = state.score_B
        new_state.move_count = state.move_count
        # lines 和 center_idx 为只读，共享即可
        return new_state

    def _get_winner(self, state):
        if (
            state is None
            or not hasattr(state, "is_terminal")
            or not state.is_terminal()
        ):
            return 0
        if state.score_A > state.score_B:
            return 1
        elif state.score_B > state.score_A:
            return -1
        return 0


def get_move_mcts(state, player, iterations=500):
    """
    MCTS AI 主函数
    Args:
        state: 当前局面
        player: 当前行棋玩家 (1 或 -1)
        iterations: 搜索迭代次数
    Returns:
        最佳走法索引，若无则返回 None
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
        # ✅ 将 AI 当前玩家设置到根节点
        mcts.current_player = player
        mcts.root.player_to_move = player  # 根节点轮到 AI 行棋
        best_move = mcts.search()

        if best_move is None:
            return valid_moves[0]
        return best_move
    except Exception as e:
        print(f"❌ MCTS 搜索失败: {e}")
        return valid_moves[0] if valid_moves else None
