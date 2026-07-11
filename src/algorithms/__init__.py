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
