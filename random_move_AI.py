import chessboard
import moves
import rules
import random


def random_move_ai(board, side):
    """随机走法的AI。"""
    legal_moves = moves.generate_legal_moves(board, side)
    if not legal_moves:
        return None
    return random.choice(legal_moves)


def random_move(board, steps = 200, side = chessboard.RED):
    """随机走法的AI自对弈。"""
    current_side = side
    for step in range(steps):
        move = random_move_ai(board, current_side)
        print(f"Step {step}: {current_side} moves {move}")
        if move is None:
            print(f"Game over at step {step}. Winner: {rules.winner(board, current_side)}")
            return
        board = moves.make_move_copy(board, move)
        current_side = chessboard.BLACK if current_side == chessboard.RED else chessboard.RED

    print(f"Game ended after {steps} steps. No winner.")


if __name__ == "__main__":
    board = chessboard.init_board()
    random_move(board)