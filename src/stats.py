import time
from dataclasses import dataclass


from tqdm import tqdm

from src.game_state import GameState
from src.utils import idx_to_xyz


@dataclass(slots=True)
class Stats:
    total_games: int
    wins_A: int = 0
    wins_B: int = 0
    draws: int = 0
    score_A_list = []
    score_B_list = []
    avg_score_A: float = 0.0
    avg_score_B: float = 0.0
    avg_time: float = 0.0
    win_rate_A: float = 0.0
    win_rate_B: float = 0.0
    draw_rate: float = 0.0
    game_times = []

    def update(self, state, game_time):
        self.score_A_list.append(state.score_A)
        self.score_B_list.append(state.score_B)
        self.game_times.append(game_time)

        if state.score_A > state.score_B:
            self.wins_A += 1
        elif state.score_B > state.score_A:
            self.wins_B += 1
        else:
            self.draws += 1

    def result_update(self):
        self.avg_score_A = (
            sum(self.score_A_list) / self.total_games if self.total_games > 0 else 0.0
        )
        self.avg_score_B = (
            sum(self.score_B_list) / self.total_games if self.total_games > 0 else 0.0
        )
        self.avg_time = (
            sum(self.game_times) / self.total_games if self.total_games > 0 else 0.0
        )
        self.win_rate_A = (
            self.wins_A / self.total_games if self.total_games > 0 else 0.0
        )
        self.win_rate_B = (
            self.wins_B / self.total_games if self.total_games > 0 else 0.0
        )
        self.draw_rate = self.draws / self.total_games if self.total_games > 0 else 0.0


def get_A_vs_B_stats(A, B, total_games=100, verbose=False, max_moves=26) -> Stats:
    stats = Stats(total_games)

    print(f"AI1: {A.__name__} vs AI2: {B.__name__}, 对局数: {total_games}")

    for i in tqdm(range(total_games)):
        if verbose:
            print(f"第 {i + 1}/{total_games} 局")

        state = GameState()
        current_player = 1
        move_count = 0

        start_time = time.time()

        while move_count < max_moves:
            if current_player == 1:
                move = A(state, current_player)
            else:
                move = B(state, current_player)

            if move is None:
                break

            state.make_move(move, current_player)
            move_count += 1
            current_player = -current_player

            if verbose:
                print(f"第 {move_count} 步: {idx_to_xyz(move)}")

        end_time = time.time()
        game_time = end_time - start_time

        stats.update(state, game_time)

        if verbose:
            state.print_board()

    stats.result_update()

    return stats
