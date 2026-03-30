# test_moves.py
import chessboard
import moves
import rules


def test_initial_board_no_move():
    """Basic invalid move checks from initial position."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert not moves.is_valid_move(board, moves.Move(5, 5, 5, 6), side)
    assert not moves.is_valid_move(board, moves.Move(0, 0, 0, 1), side)
    assert not moves.is_valid_move(board, moves.Move(9, 0, 9, 1), side)
    assert not moves.is_valid_move(board, moves.Move(9, 0, 10, 0), side)

    print("PASS: initial board basic checks")


def test_king_moves():
    """Test king movement rules."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(9, 4, 8, 4), side)
    assert not moves.is_valid_move(board, moves.Move(9, 4, 8, 5), side)
    assert not moves.is_valid_move(board, moves.Move(9, 4, 9, 6), side)

    side = chessboard.BLACK
    assert moves.is_valid_move(board, moves.Move(0, 4, 1, 4), side)
    assert not moves.is_valid_move(board, moves.Move(0, 4, 1, 5), side)

    print("PASS: king moves")


def test_advisor_moves():
    """Test advisor movement rules."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(9, 3, 8, 4), side)
    assert not moves.is_valid_move(board, moves.Move(9, 3, 8, 3), side)
    assert not moves.is_valid_move(board, moves.Move(9, 3, 8, 2), side)

    print("PASS: advisor moves")


def test_elephant_moves():
    """Test elephant movement rules."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(9, 2, 7, 0), side)
    board[8][1] = "rP"
    assert not moves.is_valid_move(board, moves.Move(9, 2, 7, 0), side)
    board[8][1] = chessboard.EMPTY

    assert not moves.is_valid_move(board, moves.Move(9, 2, 5, 0), side)

    print("PASS: elephant moves")


def test_knight_moves():
    """Test knight movement including leg-block rule."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(9, 1, 7, 2), side)
    board[8][1] = "rP"
    assert not moves.is_valid_move(board, moves.Move(9, 1, 7, 2), side)
    board[8][1] = chessboard.EMPTY

    assert moves.is_valid_move(board, moves.Move(9, 1, 7, 0), side)

    print("PASS: knight moves")


def test_rook_moves():
    """Test rook movement with blockers."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(9, 0, 8, 0), side)
    assert not moves.is_valid_move(board, moves.Move(9, 0, 9, 2), side)
    assert not moves.is_valid_move(board, moves.Move(9, 0, 0, 0), side)

    board[8][0] = chessboard.EMPTY
    board[7][0] = chessboard.EMPTY
    board[6][0] = chessboard.EMPTY
    board[5][0] = chessboard.EMPTY
    board[4][0] = chessboard.EMPTY
    board[3][0] = chessboard.EMPTY
    board[2][0] = chessboard.EMPTY
    board[1][0] = chessboard.EMPTY
    assert moves.is_valid_move(board, moves.Move(9, 0, 0, 0), side)

    print("PASS: rook moves")


def test_cannon_moves():
    """Test cannon movement and capture rules."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(7, 1, 7, 2), side)
    assert not moves.is_valid_move(board, moves.Move(7, 1, 7, 7), side)

    for r in range(6, 0, -1):
        board[r][1] = chessboard.EMPTY
    board[5][1] = "bP"
    board[1][1] = "bR"

    assert moves.is_valid_move(board, moves.Move(7, 1, 1, 1), side)
    assert not moves.is_valid_move(board, moves.Move(7, 1, 3, 1), side)
    assert moves.is_valid_move(board, moves.Move(7, 1, 6, 1), side)

    print("PASS: cannon moves")


def test_pawn_moves():
    """Test pawn movement before/after crossing river."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(6, 0, 5, 0), side)
    assert not moves.is_valid_move(board, moves.Move(6, 0, 6, 1), side)
    assert not moves.is_valid_move(board, moves.Move(6, 0, 7, 0), side)

    board[4][0] = "rP"
    board[6][0] = chessboard.EMPTY
    assert moves.is_valid_move(board, moves.Move(4, 0, 3, 0), side)
    assert moves.is_valid_move(board, moves.Move(4, 0, 4, 1), side)
    assert not moves.is_valid_move(board, moves.Move(4, 0, 4, -1), side)
    assert not moves.is_valid_move(board, moves.Move(4, 0, 5, 0), side)

    print("PASS: pawn moves")


def test_king_face_to_face():
    """Test kings-face-to-face rule."""
    board = chessboard.init_board()

    assert not moves.kings_face_to_face(board)

    board = moves.make_move_copy(board, moves.Move(9, 4, 8, 4))
    assert not moves.kings_face_to_face(board)

    for r in range(1, 8):
        board[r][4] = chessboard.EMPTY
    assert moves.kings_face_to_face(board)

    board = chessboard.init_board()
    for r in range(1, 9):
        for c in range(9):
            board[r][c] = chessboard.EMPTY
    board[0][4] = "bK"
    board[9][4] = "rK"
    assert not moves.is_valid_move(board, moves.Move(9, 4, 8, 4), chessboard.RED)

    print("PASS: kings face to face")


def test_self_check():
    """Test that self-check moves are rejected."""
    board = chessboard.init_board()
    side = chessboard.RED

    assert moves.is_valid_move(board, moves.Move(9, 1, 7, 2), side)

    board = chessboard.init_board()
    board[0][0] = chessboard.EMPTY
    board[7][4] = "bR"
    assert not moves.is_valid_move(board, moves.Move(9, 4, 8, 4), chessboard.RED)

    print("PASS: self-check filtering")


def test_generate_legal_moves():
    """Test legal move generation and known moves."""
    board = chessboard.init_board()
    red_moves = moves.generate_legal_moves(board, chessboard.RED)
    black_moves = moves.generate_legal_moves(board, chessboard.BLACK)

    assert len(red_moves) > 0
    assert len(black_moves) > 0
    assert moves.Move(9, 4, 8, 4) in red_moves
    assert moves.Move(9, 1, 7, 2) in red_moves
    assert moves.Move(7, 1, 7, 2) in red_moves
    print(f"PASS: generate legal moves red={len(red_moves)} black={len(black_moves)}")


def test_winner_when_king_missing():
    """If a king is captured, that side loses immediately."""
    board = chessboard.init_board()
    board[0][4] = chessboard.EMPTY
    assert rules.winner(board) == chessboard.RED

    board = chessboard.init_board()
    board[9][4] = chessboard.EMPTY
    assert rules.winner(board) == chessboard.BLACK

    print("PASS: winner by missing king")


def test_winner_when_no_legal_moves_for_side_to_move():
    """If side to move has no legal moves, that side loses."""
    board = [[chessboard.EMPTY for _ in range(chessboard.BOARD_COLS)] for _ in range(chessboard.BOARD_ROWS)]
    board[0][0] = "bK"
    board[9][4] = "rK"
    board[8][4] = "bR"
    board[8][0] = "bR"
    board[0][3] = "bR"
    board[0][5] = "bR"

    assert len(moves.generate_legal_moves(board, chessboard.RED)) == 0
    assert rules.winner(board, chessboard.RED) == chessboard.BLACK

    print("PASS: winner by no legal moves for side to move")


def run_all_tests():
    test_initial_board_no_move()
    test_king_moves()
    test_advisor_moves()
    test_elephant_moves()
    test_knight_moves()
    test_rook_moves()
    test_cannon_moves()
    test_pawn_moves()
    test_king_face_to_face()
    test_self_check()
    test_generate_legal_moves()
    test_winner_when_king_missing()
    test_winner_when_no_legal_moves_for_side_to_move()
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    run_all_tests()
