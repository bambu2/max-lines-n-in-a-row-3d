import random
import math

from src.utils import idx_to_xyz, GameState


def get_ai_move_random(state, player):
    """随机选择一个合法位置"""
    valid_moves = []
    for idx in range(27):
        if state.is_valid_move(idx):
            valid_moves.append(idx)

    if valid_moves:
        return random.choice(valid_moves)
    return None


def get_ai_move_greedy(state, player):
    """选择能立即形成最多线的位置"""
    best_score = -1
    best_move = None

    for idx in range(27):
        if not state.is_valid_move(idx):
            continue

        # 模拟落子
        board_copy = state.board.copy()
        board_copy[idx] = player

        # 计算如果下这里，能完成几条线
        score = 0
        for line in state.lines:
            if idx not in line:
                continue
            vals = [board_copy[i] for i in line]
            if all(v == player for v in vals):
                score += 1

        # 防守：如果对手下一步能完成线，优先堵
        defense_score = 0
        for line in state.lines:
            if idx not in line:
                continue
            vals = [state.board[i] for i in line]
            # 如果对手已经有两个子，且第三个是空位
            if vals.count(-player) == 2 and vals.count(0) == 1:
                defense_score += 5  # 高优先级防守

        total_score = score * 10 + defense_score

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move


def get_ai_move_advanced(state, player):
    """使用评估函数，选择潜力最高的位置"""
    best_score = -999
    best_move = None
    center_idx = 13

    for idx in range(27):
        if not state.is_valid_move(idx):
            continue

        # 进攻得分
        offense_score = 0
        for line in state.lines:
            if idx not in line:
                continue

            vals = [state.board[i] for i in line]

            # 如果线中有对手棋子，这条线被堵
            if any(v == -player for v in vals):
                continue

            your_count = sum(1 for v in vals if v == player)
            empty_count = sum(1 for v in vals if v == 0)

            if empty_count > 0:
                if your_count == 2:  # 差一步完成
                    offense_score += 100
                elif your_count == 1:
                    offense_score += 10
                else:
                    offense_score += 1

        # 防守得分（阻止对手）
        defense_score = 0
        for line in state.lines:
            if idx not in line:
                continue

            vals = [state.board[i] for i in line]

            # 检查对手的威胁
            if any(v == player for v in vals):
                continue

            opponent_count = sum(1 for v in vals if v == -player)
            empty_count = sum(1 for v in vals if v == 0)

            if empty_count > 0:
                if opponent_count == 2:  # 对手差一步
                    defense_score += 80
                elif opponent_count == 1:
                    defense_score += 5

        # 位置加成
        position_bonus = 0
        l, r, c = idx_to_xyz(idx)
        if idx == 13:  # 中心（虽然不能用，但还是留着）
            position_bonus = 0
        elif l in (0, 2) and r in (0, 2) and c in (0, 2):
            position_bonus = 3  # 角格
        elif (
            (l == 1 and r in (0, 2) and c in (0, 2))
            or (r == 1 and l in (0, 2) and c in (0, 2))
            or (c == 1 and l in (0, 2) and r in (0, 2))
        ):
            position_bonus = 2  # 边心格

        total_score = offense_score + defense_score + position_bonus

        if total_score > best_score:
            best_score = total_score
            best_move = idx

    return best_move


def minimax(state, depth, alpha, beta, is_maximizing, player):
    """Minimax搜索 + Alpha-Beta剪枝"""
    # 如果到达终局或深度限制
    if state.move_count >= 26 or depth == 0:
        # 评估当前局面
        return evaluate_board(state, player)

    if is_maximizing:
        max_eval = -float("inf")
        for idx in range(27):
            if state.is_valid_move(idx):
                # 模拟落子
                board_backup = state.board.copy()
                score_backup = (state.score_A, state.score_B)
                state.make_move(idx, player)

                eval = minimax(state, depth - 1, alpha, beta, False, -player)

                # 恢复状态
                state.board = board_backup
                state.score_A, state.score_B = score_backup
                state.move_count -= 1

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float("inf")
        for idx in range(27):
            if state.is_valid_move(idx):
                board_backup = state.board.copy()
                score_backup = (state.score_A, state.score_B)
                state.make_move(idx, -player)

                eval = minimax(state, depth - 1, alpha, beta, True, player)

                state.board = board_backup
                state.score_A, state.score_B = score_backup
                state.move_count -= 1

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval


def get_ai_move_minimax(state, player, depth=6):
    """Minimax AI主函数"""
    best_score = -float("inf")
    best_move = None

    for idx in range(27):
        if state.is_valid_move(idx):
            board_backup = state.board.copy()
            score_backup = (state.score_A, state.score_B)
            state.make_move(idx, player)

            score = minimax(
                state, depth - 1, -float("inf"), float("inf"), False, -player
            )

            state.board = board_backup
            state.score_A, state.score_B = score_backup
            state.move_count -= 1

            if score > best_score:
                best_score = score
                best_move = idx

    return best_move


def evaluate_board(state, player):
    """评估当前局面的得分"""
    # 终局评估
    if state.move_count >= 26:
        if state.score_A > state.score_B:
            return 1000 if player == 1 else -1000
        elif state.score_B > state.score_A:
            return 1000 if player == -1 else -1000
        else:
            return 0

    # 中间局面评估
    score_diff = state.score_A - state.score_B
    return score_diff * 10  # 转换回玩家视角


class MCTSNode:
    """MCTS 节点"""

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_valid_moves() if state else []

    def is_fully_expanded(self):
        """检查是否所有合法走法都已尝试"""
        return len(self.untried_moves) == 0

    def is_terminal(self):
        """检查游戏是否结束"""
        if self.state is None:
            return True
        return self.state.move_count >= 26

    def best_child(self, exploration_constant=1.41):
        """
        使用 UCT 公式选择最佳子节点
        返回 (best_child, score) 元组，如果没有子节点返回 (None, -inf)
        """
        if not self.children:
            return None, -float("inf")

        best_child = None
        best_score = -float("inf")

        for child in self.children:
            # 防止除零错误
            if child.visits == 0:
                # 未访问的节点给予最高优先级（无限探索）
                return child, float("inf")

            # UCT 公式
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
            state: GameState 对象
            iterations: 模拟次数
            exploration_constant: 探索常数（越大越倾向于探索）
        """
        if state is None:
            raise ValueError("state 不能为 None")

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
                winner = self._simulate(node.state)

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
        """
        扩展阶段：从未尝试的走法中选一个，创建子节点

        Returns:
            MCTSNode: 新创建的子节点，如果没有可扩展的则返回原节点
        """
        # ========== 防御1：检查输入 ==========
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
            node.untried_moves = valid_moves.copy()  # 使用 copy 避免引用问题
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

            # 执行走法
            success = new_state.make_move(move, self.current_player)
            if not success:
                print(f"❌ _expand: 走法 {move} 执行失败")
                return node

        except Exception as e:
            print(f"❌ _expand: 创建新状态失败: {e}")
            return node

        # ========== 创建子节点 ==========
        try:
            child_node = MCTSNode(new_state, parent=node, move=move)
            node.children.append(child_node)
        except Exception as e:
            print(f"❌ _expand: 创建子节点失败: {e}")
            return node

        return child_node

    def _simulate(self, state):
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

        player = self.current_player

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
        """
        回传阶段：从节点一直更新到根节点

        Args:
            node: 起始节点
            winner: 获胜玩家 (1: A赢, -1: B赢, 0: 平局)
        """
        # ========== 防御1：检查输入 ==========
        if node is None:
            return

        current = node
        while current is not None:
            current.visits += 1

            # 只有当前玩家赢了才加分
            if winner == self.current_player:
                current.wins += 1

            current = current.parent

    def _get_best_move(self):
        """
        从根节点的子节点中选择访问次数最多的走法

        Returns:
            int: 最佳走法的索引，如果没有则返回 None
        """
        # ========== 防御1：检查根节点 ==========
        if self.root is None:
            return None

        # ========== 防御2：检查是否有子节点 ==========
        if not self.root.children:
            # 如果没有子节点，从根节点获取合法走法
            valid_moves = self.root.state.get_valid_moves()
            return valid_moves[0] if valid_moves else None

        # ========== 选择访问次数最多的子节点 ==========
        best_child = max(self.root.children, key=lambda c: c.visits)

        if best_child is None:
            valid_moves = self.root.state.get_valid_moves()
            return valid_moves[0] if valid_moves else None

        return best_child.move

    def _copy_state(self, state):
        """
        快速拷贝 GameState

        Args:
            state: 原始 GameState

        Returns:
            GameState: 拷贝的新状态
        """
        # ========== 防御 ==========
        if state is None:
            return None

        # ========== 浅拷贝 + 深拷贝列表 ==========
        new_state = GameState()
        new_state.board = state.board.copy()  # 列表拷贝
        new_state.score_A = state.score_A
        new_state.score_B = state.score_B
        new_state.move_count = state.move_count
        # lines 和 center_idx 是只读的，可以共享
        return new_state

    def _get_winner(self, state):
        """
        判断胜负

        Returns:
            int: 1 (A赢), -1 (B赢), 0 (平局)
        """
        if state is None:
            return 0

        if state.score_A > state.score_B:
            return 1
        elif state.score_B > state.score_A:
            return -1
        else:
            return 0


# ========== 封装的 AI 函数 ==========
def get_ai_move_mcts(state, player, iterations=500):
    """
    MCTS AI 主函数

    Args:
        state: GameState 对象
        player: 当前玩家 (1 或 -1)
        iterations: MCTS 迭代次数

    Returns:
        int: 最佳走法索引，如果没有则返回 None
    """
    # ========== 防御1：检查输入 ==========
    if state is None:
        print("❌ 错误：state 为 None")
        return None

    # ========== 防御2：检查是否有合法走法 ==========
    valid_moves = state.get_valid_moves()
    if not valid_moves:
        print("ℹ️ 没有合法走法")
        return None

    # ========== 防御3：如果只有一个走法，直接返回 ==========
    if len(valid_moves) == 1:
        return valid_moves[0]

    # ========== 执行 MCTS ==========
    try:
        mcts = MCTS(state, iterations=iterations)
        mcts.current_player = player
        best_move = mcts.search()

        # ========== 防御4：检查搜索结果 ==========
        if best_move is None:
            # 保底：返回第一个合法走法
            return valid_moves[0]

        return best_move

    except Exception as e:
        print(f"❌ MCTS 搜索失败: {e}")
        # 保底：返回第一个合法走法
        return valid_moves[0] if valid_moves else None
