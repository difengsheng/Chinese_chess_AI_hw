import moves
import chessboard

'''将死相关的函数。'''
def not_checkmate(board, side):
    """判断指定一方当前是否没有被将死。"""
    if not moves.is_in_check(board, side):
        return True

    legal_moves = moves.generate_legal_moves(board, side)
    return len(legal_moves) > 0


def winner(board):
    """判断当前棋盘状态的赢家。"""
    if not not_checkmate(board, chessboard.RED):
        return chessboard.BLACK
    if not not_checkmate(board, chessboard.BLACK):
        return chessboard.RED
    return None


if __name__ == "__main__":
    pass
