from basic import chessboard
from basic import moves
from basic import rules
from visualize import show
from visualize.controller import ChessController
import time



def evaluate_board(board):
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

    return (red_score - black_score)



def _is_terminal(board, side):
    """判断当前局面是否终局。返回 (is_terminal, winner, score)。"""
    # 检查是否已将死（无法逃脱）
    winner = rules.winner(board, side)
    if winner is not None:
        # 将死：获胜方返回正无穷，失败方返回负无穷
        score = float('inf') if winner == chessboard.RED else float('-inf')
        return True, winner, score
    return False, None, None



def _alphabeta_search(board, side = chessboard.RED, depth = 0, alpha = float('-inf'), beta = float('inf')):
    """Alpha-Beta 剪枝的 MinMax 搜索。递归内部函数。"""
    
    # 终局优先判定
    is_terminal, winner, score = _is_terminal(board, side)
    if is_terminal:
        return None, score
    
    # 深度限制
    if depth == 0:
        return None, evaluate_board(board)

    legal_moves = moves.generate_legal_moves(board, side)
    if not legal_moves:
        # 没有合法着法，当前方输
        return None, float('-inf') if side == chessboard.RED else float('inf')

    best_move = None
    opponent_side = chessboard.BLACK if side == chessboard.RED else chessboard.RED

    if side == chessboard.RED:
        # 红方（最大方）：尽量提高分数
        max_value = float('-inf')
        for move in legal_moves:
            new_board = moves.make_move_copy(board, move)
            _, value = _alphabeta_search(new_board, opponent_side, depth - 1, alpha, beta)
            
            if value > max_value:
                max_value = value
                best_move = move
            
            # Alpha-Beta 剪枝
            alpha = max(alpha, max_value)
            if beta <= alpha:
                break  # 剪枝：对手不会走到这个分支
        
        return best_move, max_value
    else:
        # 黑方（最小方）：尽量降低分数
        min_value = float('inf')
        for move in legal_moves:
            new_board = moves.make_move_copy(board, move)
            _, value = _alphabeta_search(new_board, opponent_side, depth - 1, alpha, beta)
            
            if value < min_value:
                min_value = value
                best_move = move
            
            # Alpha-Beta 剪枝
            beta = min(beta, min_value)
            if beta <= alpha:
                break  # 剪枝：当前玩家已不会走到更差方案
        
        return best_move, min_value


def minmax_search(board, side, depth):
    """MinMax 搜索入口函数：返回最佳着法和对应的评估值。"""
    return _alphabeta_search(board, side, depth, float('-inf'), float('inf'))


if __name__ == "__main__":
    # 这里可以测试 MinMax 搜索函数
    board = chessboard.init_board()
    start_time = time.time()
    best_move, score = minmax_search(board, chessboard.RED, depth=3)
    end_time = time.time()
    print(f"Best Move: {best_move}, Score: {score}, completed in {end_time - start_time:.2f} seconds")