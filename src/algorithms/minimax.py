def get_move_minimax(state, player, depth=4) -> int | None:
    """Get best move using minimax with alpha-beta pruning."""

    if not state.valid_moves:
        return None
    if len(state.valid_moves) == 1:
        return state.valid_moves[0]

    best_score = -float("inf")
    best_move = state.valid_moves[0]
    is_maximizing = player == 1

    for idx in state.valid_moves:
        # ✅ Make move
        state.make_move(idx, player)

        # After making the move, it's the OPPONENT's turn
        score = minimax(
            state, depth - 1, -float("inf"), float("inf"), not is_maximizing
        )

        # ✅ Undo move
        state.undo_move()

        if score > best_score:
            best_score = score
            best_move = idx

    return best_move


def minimax(state, depth, alpha, beta, is_maximizing) -> float:
    """Minimax with alpha-beta pruning using undo."""
    current_player = 1 if is_maximizing else -1

    if state.is_terminal() or depth == 0:
        return evaluate_board(state, current_player)

    valid_moves = [idx for idx in range(27) if state.is_valid_move(idx)]
    if not valid_moves:
        return evaluate_board(state, current_player)

    if is_maximizing:
        max_eval = -float("inf")
        for idx in valid_moves:
            # ✅ Make move
            state.make_move(idx, 1)

            # Recursively evaluate
            eval = minimax(state, depth - 1, alpha, beta, False)

            # ✅ Undo move (NO COPYING!)
            state.undo_move()

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval

    else:
        min_eval = float("inf")
        for idx in valid_moves:
            # ✅ Make move
            state.make_move(idx, -1)

            # Recursively evaluate
            eval = minimax(state, depth - 1, alpha, beta, True)

            # ✅ Undo move (NO COPYING!)
            state.undo_move()

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def evaluate_board(state, current_player):
    if state.is_terminal():
        # Who actually has more points?
        if state.score_A > state.score_B:
            # Player 1 wins
            return 10000 if current_player == 1 else -10000
        elif state.score_B > state.score_A:
            # Player -1 wins
            return 10000 if current_player == -1 else -10000
        else:
            return 0

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
    # Count moves for current player
    my_moves = 0
    opponent_moves = 0

    # Save current state
    board_backup = state.board.copy()
    score_backup = (state.score_A, state.score_B)
    move_count_backup = state.move_count

    # Count current player's moves
    for pos in range(27):
        if state.board[pos] == 0:
            # Try the move
            temp_state = state  # In real code, copy state properly
            temp_state.board[pos] = player
            if temp_state.is_valid_move(pos):  # Need actual validation
                my_moves += 1
            temp_state.board[pos] = 0

    # Count opponent's moves
    for pos in range(27):
        if state.board[pos] == 0:
            temp_state = state
            temp_state.board[pos] = -player
            if temp_state.is_valid_move(pos):
                opponent_moves += 1
            temp_state.board[pos] = 0

    # Restore state
    state.board = board_backup
    state.score_A, state.score_B = score_backup
    state.move_count = move_count_backup

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
        if pos == state.banned_idx:  # Skip banned center
            continue
        if state.board[pos] == player:
            bonus += get_position_importance(pos)
        elif state.board[pos] == -player:
            bonus -= get_position_importance(pos)
    return bonus
