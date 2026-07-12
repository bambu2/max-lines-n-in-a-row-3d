import math
import random


class Node:
    __slots__ = (
        "state",
        "parent",
        "action",
        "children",
        "visits",
        "value",
        "untried_actions",
    )

    def __init__(self, state, parent=None, action=None):
        self.state = state  # Your game state
        self.parent = parent  # Parent node
        self.action = action  # Action that led here
        self.children = []  # List of child nodes
        self.visits = 0  # Visit count
        self.value = 0.0  # Total reward (from perspective of current player)
        self.untried_actions = state.get_legal_actions()  # Actions not yet expanded

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def is_terminal(self) -> bool:
        return self.state.is_terminal()

    def best_child(self, exploration_constant: float = 1.41) -> "Node":
        """Select child with highest UCB1 score"""

        def ucb1(child):
            if child.visits == 0:
                return float("inf")
            return (child.value / child.visits) + exploration_constant * math.sqrt(
                math.log(self.visits) / child.visits
            )

        return max(self.children, key=ucb1)


class MCTS:
    def __init__(self, state, iterations=1000, exploration=1.41):
        self.root = Node(state)
        self.iterations = iterations
        self.exploration = exploration

    def search(self):
        for _ in range(self.iterations):
            node = self.root

            # 1. SELECTION - traverse tree
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child(self.exploration)

            # 2. EXPANSION - add one child
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expand(node)

            # 3. SIMULATION - play randomly
            reward = self._simulate(node)

            # 4. BACKPROPAGATION
            self._backpropagate(node, reward)

        # Return best action
        return max(self.root.children, key=lambda c: c.visits).action

    def _expand(self, node: Node) -> Node:
        """Expand one untried action"""
        action = node.untried_actions.pop()
        new_state = node.state.apply_action(action)
        child = Node(new_state, parent=node, action=action)
        node.children.append(child)
        return child

    def _simulate(self, node: Node) -> float:
        """Random rollout from this state"""
        state = node.state.copy()
        while not state.is_terminal():
            actions = state.get_legal_actions()
            action = random.choice(actions)
            state = state.apply_action(action)
        return (
            state.get_reward()
        )  # Must return from perspective of player who just moved

    def _backpropagate(self, node: Node | None, reward: float):
        """Propagate reward up the tree"""
        while node:
            node.visits += 1
            node.value += reward
            node = node.parent
            reward = -reward  # Flip reward for opponent


def get_move_mcts():
    pass
