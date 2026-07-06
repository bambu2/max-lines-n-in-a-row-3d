import random
import math

from game_state import GameState
from utils import idx_to_xyz


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


def get_ai_move_minimax(state, player, depth=4):
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
    def __init__(self, state, parent=None, move=None):
        self.state = state  # GameState 对象
        self.parent = parent  # 父节点
        self.move = move  # 走到这个节点的落子位置 (idx)
        self.children = []  # 子节点列表
        self.wins = 0  # 胜利次数（从当前玩家视角）
        self.visits = 0  # 访问次数
        self.untried_moves = state.get_valid_moves()  # 还没试过的走法

    def is_fully_expanded(self):
        """检查是否所有可能的走法都已尝试过"""
        return len(self.untried_moves) == 0

    def is_terminal(self):
        """检查游戏是否结束（所有格子下满）"""
        return self.state.move_count >= 26

    def best_child(self, exploration_constant=1.41):
        """
        使用 UCT 公式选择最佳子节点
        UCT = 胜率 + C * sqrt(ln(父访问次数) / 子访问次数)
        """
        best_score = -float("inf")
        best_child = None

        for child in self.children:
            # 胜率
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            # 探索奖励
            exploration = exploration_constant * math.sqrt(
                math.log(self.visits) / child.visits
            )
            score = win_rate + exploration

            if score > best_score:
                best_score = score
                best_child = child


class MCTS:
    def __init__(self, state, iterations=1000):
        self.root = MCTSNode(state)
        self.iterations = iterations
        self.current_player = 1  # 假设 MCTS 总是为当前玩家服务

    def search(self):
        """执行 MCTS 搜索"""
        # 如果根节点已经是终局，直接返回
        if self.root.is_terminal():
            return None

        for _ in range(self.iterations):
            # 1. 选择
            node = self.select(self.root)

            # 如果 node 是 None，跳过这轮
            if node is None:
                continue

            # 2. 扩展
            if not node.is_terminal():
                node = self.expand(node)

            # 3. 模拟
            winner = self.simulate(node.state)

            # 4. 回传
            self.backpropagate(node, winner)

        # 返回访问次数最多的子节点
        if not self.root.children:
            return None

        best_move_node = max(self.root.children, key=lambda c: c.visits)
        return best_move_node.move

    def select(self, node):
        """
        选择：从根节点开始，一直选 UCT 最高的子节点
        """
        while not node.is_terminal() and node.is_fully_expanded():
            child = node.best_child()
            if child is None:  # 如果没有子节点，跳出循环
                break
            node = child
        return node

    def expand(self, node):
        """扩展：从未尝试的走法中随机选一个，创建子节点"""
        # 随机选一个未尝试的走法
        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)

        # 创建新状态
        new_state = copy_state(node.state)  # 需要深拷贝
        new_state.make_move(move, self.current_player)

        # 创建子节点
        child_node = MCTSNode(new_state, parent=node, move=move)
        node.children.append(child_node)

        return child_node

    def simulate(self, state):
        """
        模拟：从当前状态开始，双方随机走棋直到终局
        返回胜利玩家 (1 或 -1)
        """
        sim_state = copy_state(state)
        player = self.current_player

        # 随机下到终局
        while sim_state.move_count < 26:
            valid_moves = sim_state.get_valid_moves()
            if not valid_moves:
                break

            # 随机走一步
            move = random.choice(valid_moves)
            sim_state.make_move(move, player)
            player = -player  # 切换玩家

        # 判断胜负（从当前玩家视角）
        if sim_state.score_A > sim_state.score_B:
            return 1  # 玩家A赢
        elif sim_state.score_B > sim_state.score_A:
            return -1  # 玩家B赢
        else:
            return 0  # 平局（极少发生）

    def backpropagate(self, node, winner):
        """回传：从节点一直更新到根节点"""
        while node is not None:
            node.visits += 1
            # 只有当前玩家赢了才加分
            if winner == self.current_player:
                node.wins += 1
            node = node.parent


def copy_state(state):
    """快速拷贝 GameState（只拷贝必要数据）"""
    new_state = GameState()
    new_state.board = state.board.copy()  # 列表拷贝
    new_state.score_A = state.score_A
    new_state.score_B = state.score_B
    new_state.move_count = state.move_count
    # lines 和 center_idx 是只读的，可以共享
    return new_state


def get_ai_move_mcts(state, player, iterations=500):
    """
    MCTS AI 主函数
    iterations: 模拟次数，越大棋力越强（推荐 500-2000）
    """
    # MCTS 内部用 player 作为当前玩家
    mcts = MCTS(state, iterations=iterations)
    mcts.current_player = player

    best_move = mcts.search()
    return best_move
