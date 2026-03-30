from basic import chessboard
from basic import moves
from basic import rules
from visualize import show
from visualize.controller import ChessController


def evaluate_board(board, side):
    """评估函数：简单计算双方棋子数量差作为评估值。"""

    # 这里我们给每种棋子赋分
    piece_values = {
        "K": 1000, "A": 2, "B": 3, "N": 4, "R": 6, "C": 5, "P": 1,
    }

    red_score = 0
    black_score = 0

    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece != chessboard.EMPTY:
                value = piece_values[chessboard.type_of_piece(piece)]
                if chessboard.side_of_piece(piece) == chessboard.RED:
                    red_score += value
                else:
                    black_score += value

    return (red_score - black_score) if side == chessboard.RED else (black_score - red_score)


