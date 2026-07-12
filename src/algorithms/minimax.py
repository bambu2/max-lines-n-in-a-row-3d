def get_move_minimax(state, player, depth=4) -> int | None:
    best_score = -float("inf")
    best_move = None

    valid_moves = [idx for idx in range(27) if state.is_valid_move(idx)]

    if not valid_moves:
        return None

    if len(valid_moves) == 1:
        return valid_moves[0]

    for idx in valid_moves:
        # Save state
        board_backup = state.board.copy()
        score_backup = (state.score_A, state.score_B)
        move_count_backup = state.move_count

        # Make move
        state.make_move(idx, player)

        # Evaluate - pass opponent as the "other" player for minimax
        # The current player has made their move, now it's opponent's turn
        score = minimax(state, depth - 1, -float("inf"), float("inf"), False, -player)

        # Restore state
        state.board = board_backup
        state.score_A, state.score_B = score_backup
        state.move_count = move_count_backup

        # Select best move
        if score > best_score:
            best_score = score
            best_move = idx

    return best_move


def minimax(state, depth, alpha, beta, is_maximizing, current_player) -> float:
    """Minimax with alpha-beta pruning.

    Args:
        current_player: The player whose turn it is to move (1 or -1)
    """
    # If terminal or depth limit reached
    if state.is_terminal() or depth == 0:
        return evaluate_board(state, current_player)

    # Get valid moves for current player
    valid_moves = [idx for idx in range(27) if state.is_valid_move(idx)]

    # If no valid moves, evaluate immediately
    if not valid_moves:
        return evaluate_board(state, current_player)

    if is_maximizing:
        max_eval = -float("inf")
        for idx in valid_moves:
            # Save state
            board_backup = state.board.copy()
            score_backup = (state.score_A, state.score_B)
            move_count_backup = state.move_count

            # Make move for maximizing player (current_player)
            state.make_move(idx, current_player)

            # Recursively evaluate - switch to minimizing, opponent's turn
            eval = minimax(state, depth - 1, alpha, beta, False, -current_player)

            # Restore state
            state.board = board_backup
            state.score_A, state.score_B = score_backup
            state.move_count = move_count_backup

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for idx in valid_moves:
            # Save state
            board_backup = state.board.copy()
            score_backup = (state.score_A, state.score_B)
            move_count_backup = state.move_count

            # Make move for minimizing player (current_player - the opponent)
            state.make_move(idx, current_player)

            # Recursively evaluate - switch to maximizing, other player's turn
            eval = minimax(state, depth - 1, alpha, beta, True, -current_player)

            # Restore state
            state.board = board_backup
            state.score_A, state.score_B = score_backup
            state.move_count = move_count_backup

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def evaluate_board(state, current_player):
    """Evaluate board from current_player's perspective"""
    # Terminal evaluation
    if state.is_terminal():
        # Get scores from current_player's perspective
        if current_player == 1:
            my_score, opp_score = state.score_A, state.score_B
        else:
            my_score, opp_score = state.score_B, state.score_A

        # Return win/loss/draw
        if my_score > opp_score:
            return 10000  # Win
        elif opp_score > my_score:
            return -10000  # Loss
        else:
            return 0  # Draw

    # Mid-game evaluation from current_player's perspective
    if current_player == 1:
        score_diff = state.score_A - state.score_B
    else:
        score_diff = state.score_B - state.score_A

    # Add positional bonuses for strategic play
    positional_bonus = calculate_sophisticated_bonus(state, current_player)

    # Consider mobility (number of available moves)
    mobility_bonus = calculate_mobility_bonus(state, current_player)

    # Combine score difference with positional bonus
    return score_diff * 10 + positional_bonus + mobility_bonus


def calculate_mobility_bonus(state, player):
    """Bonus for having more available moves than opponent"""
    my_moves = sum(
        1 for i in range(27) if state.is_valid_move(i) and state.board[i] == 0
    )

    # Temporarily swap player to count opponent's moves
    opponent_moves = sum(
        1 for i in range(27) if state.is_valid_move(i) and state.board[i] == 0
    )

    # This is a simplification - in a real game, you'd need to simulate opponent's moves
    # Return a small mobility advantage
    return (my_moves - opponent_moves) * 0.5


def get_position_importance(pos):
    """Return the strategic importance of a position (0-10)"""
    # Corners - most important
    corners = [0, 2, 6, 8, 18, 20, 24, 26]
    if pos in corners:
        return 8

    # Edges - medium importance
    edges = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    if pos in edges:
        return 5

    # Face centers - lower importance
    face_centers = [4, 10, 12, 14, 16, 22]
    if pos in face_centers:
        return 3

    # Center (13) - banned, should never be here
    return 0


def calculate_sophisticated_bonus(state, player):
    """Calculate positional bonus using weighted importance"""
    bonus = 0
    for pos in range(27):
        if pos == 13:  # Skip banned center
            continue
        if state.board[pos] == player:
            bonus += get_position_importance(pos)
        elif state.board[pos] == -player:
            bonus -= get_position_importance(pos)
    return bonus
