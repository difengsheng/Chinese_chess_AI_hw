import moves
import chessboard

'''将死相关的函数。'''


def has_king(board, side):
    """判断指定一方将/帅是否仍在棋盘上。"""
    return moves.find_king(board, side) is not None


def has_legal_moves(board, side):
    """判断指定一方是否还有合法着法。"""
    return len(moves.generate_legal_moves(board, side)) > 0



def winner(board, side_to_move=None):
    """判断当前棋盘状态的赢家。

    规则：
    1) 一方将/帅被吃，立即判负。
    2) 若给定 side_to_move，且其无合法着法，则该方判负。
    """
    if not has_king(board, chessboard.RED):
        return chessboard.BLACK
    if not has_king(board, chessboard.BLACK):
        return chessboard.RED

    if side_to_move is not None:
        if not has_legal_moves(board, side_to_move):
            return chessboard.BLACK if side_to_move == chessboard.RED else chessboard.RED
        return None


if __name__ == "__main__":
    pass
