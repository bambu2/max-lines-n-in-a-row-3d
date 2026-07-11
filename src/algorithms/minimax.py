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

        # Evaluate - note: we pass the current player for evaluation
        score = minimax(
            state, depth - 1, -float("inf"), float("inf"), False, player, valid_moves
        )

        # Restore state
        state.board = board_backup
        state.score_A, state.score_B = score_backup
        state.move_count = move_count_backup

        # Select best move
        if score > best_score:
            best_score = score
            best_move = idx

    return best_move


def minimax(
    state, depth, alpha, beta, is_maximizing, player, valid_moves=None
) -> float:
    # If terminal or depth limit reached
    if state.is_terminal() or depth == 0:
        return evaluate_board(state, player)

    # Get valid moves (pass or compute)
    if valid_moves is None:
        valid_moves = [idx for idx in range(27) if state.is_valid_move(idx)]

    # If no valid moves, evaluate immediately
    if not valid_moves:
        return evaluate_board(state, player)

    if is_maximizing:
        max_eval = -float("inf")
        for idx in valid_moves:  # Only iterate through valid moves
            # Save state
            board_backup = state.board.copy()
            score_backup = (state.score_A, state.score_B)
            move_count_backup = state.move_count

            # Make move for maximizing player (current player)
            state.make_move(idx, player)

            # Get new valid moves for next recursion
            next_valid_moves = [i for i in range(27) if state.is_valid_move(i)]

            # Recursively evaluate
            eval = minimax(
                state, depth - 1, alpha, beta, False, player, next_valid_moves
            )

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
        for idx in valid_moves:  # Only iterate through valid moves
            # Save state
            board_backup = state.board.copy()
            score_backup = (state.score_A, state.score_B)
            move_count_backup = state.move_count

            # Make move for minimizing player (opponent)
            state.make_move(idx, -player)

            # Get new valid moves for next recursion
            next_valid_moves = [i for i in range(27) if state.is_valid_move(i)]

            # Recursively evaluate
            eval = minimax(
                state, depth - 1, alpha, beta, True, player, next_valid_moves
            )

            # Restore state
            state.board = board_backup
            state.score_A, state.score_B = score_backup
            state.move_count = move_count_backup

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def evaluate_board(state, player):
    """Evaluate board from player's perspective"""
    # Terminal evaluation
    if state.is_terminal():
        # Get scores from player's perspective
        if player == 1:
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

    # Mid-game evaluation from player's perspective
    if player == 1:
        score_diff = state.score_A - state.score_B
    else:
        score_diff = state.score_B - state.score_A

    # Add positional bonuses for strategic play
    positional_bonus = calculate_positional_bonus(state, player)

    # Combine score difference with positional bonus
    return score_diff * 10 + positional_bonus


def calculate_advanced_heuristic(state, player):
    """Advanced heuristic considering piece combinations"""
    bonus = 0

    # Base positional bonus
    bonus += calculate_sophisticated_bonus(state, player)

    # Bonus for pairs of corners on the same face
    face_corners = {
        "top": [0, 2, 6, 8],
        "bottom": [18, 20, 24, 26],
        "front": [0, 2, 18, 20],
        "back": [6, 8, 24, 26],
        "left": [0, 6, 18, 24],
        "right": [2, 8, 20, 26],
    }

    for face, corners in face_corners.items():
        player_corners = sum(1 for c in corners if state.board[c] == player)
        if player_corners >= 3:
            bonus += 10  # Strong control of a face
        elif player_corners == 2:
            bonus += 3  # Decent control

    # Bonus for connected corners (corner-corner diagonals)
    corner_pairs = [
        (0, 2),
        (0, 6),
        (0, 18),
        (0, 20),
        (2, 8),
        (2, 20),
        (2, 26),
        (6, 8),
        (6, 24),
        (6, 26),
        (8, 24),
        (8, 26),
        (18, 20),
        (18, 24),
        (20, 26),
        (24, 26),
    ]

    for c1, c2 in corner_pairs:
        if state.board[c1] == player and state.board[c2] == player:
            bonus += 2  # Bonus for controlling connected corners

    return bonus


def calculate_positional_bonus(state, player):
    """Calculate bonus for positional advantages"""
    bonus = 0

    # CORNERS - Most valuable since center is banned
    corners = [0, 2, 6, 8, 18, 20, 24, 26]
    corner_bonus = 4  # Highest value for corners

    for pos in corners:
        if state.board[pos] == player:
            bonus += corner_bonus
        elif state.board[pos] == -player:
            bonus -= corner_bonus

    # EDGES - Second most valuable
    edges = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    edge_bonus = 2

    for pos in edges:
        if state.board[pos] == player:
            bonus += edge_bonus
        elif state.board[pos] == -player:
            bonus -= edge_bonus

    # FACE CENTERS - Least valuable (but still important)
    face_centers = [4, 10, 12, 14, 16, 22]
    face_bonus = 1

    for pos in face_centers:
        if state.board[pos] == player:
            bonus += face_bonus
        elif state.board[pos] == -player:
            bonus -= face_bonus

    return bonus


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


def get_neighbors(pos):
    """Get neighboring positions on the 3x3x3 cube"""
    # This is simplified - you need to implement actual 3D neighbors
    # Based on your game's board structure
    neighbors = []
    # Add your neighbor logic here
    return neighbors
