from basic import chessboard
from basic import moves
from basic import rules
from visualize import show
from visualize.controller import ChessController
from ulti import minmax_ulti as mmtl
import time


# 基础子力价值（权重会动态调整）


def evaluate_board(board, 
                   king_safety_eval = False,
                   protection_eval = False, 
                   defense_eval = False,
                   moves_eval = False):
    """扩展评估函数：包含6个维度的综合评估。
    
    维度包括：
    1. 基础棋子价值
    2. 位置价值（兵过河、马中心、将安全）
    3. 机动性项（合法步数差）
    4. 防御结构（士象完整性）
    5. 动态子力价值（根据残局调整权重）
    6. 棋子保护关系
    """
    
    # 获取动态棋子价值
    piece_values = mmtl._get_dynamic_piece_values(board)
    
    red_material = 0
    black_material = 0
    red_position = 0
    black_position = 0

    total_score = 0
    
    # 计算基础棋子价值 + 位置价值
    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece == chessboard.EMPTY:
                continue
            
            ptype = chessboard.type_of_piece(piece)
            side = chessboard.side_of_piece(piece)
            base_value = piece_values[ptype]
            position_bonus = 0
            
            # 位置价值加分
            if ptype == 'P':  # 兵
                position_bonus = mmtl._evaluate_pawn_position(board, r, c, side)
            elif ptype == 'N':  # 马
                position_bonus = mmtl._evaluate_knight_position(board, r, c, side)
            
            if side == chessboard.RED:
                red_material += base_value
                red_position += position_bonus
            else:
                black_material += base_value
                black_position += position_bonus
    
    # 将安全性评估
    if king_safety_eval:
        red_king_safety = mmtl._evaluate_king_safety(board, chessboard.RED)
        black_king_safety = mmtl._evaluate_king_safety(board, chessboard.BLACK)
        total_score += (red_king_safety - black_king_safety)
    
    # 防御结构评估
    if defense_eval:
        red_defense = mmtl._evaluate_defense_structure(board, chessboard.RED)
        black_defense = mmtl._evaluate_defense_structure(board, chessboard.BLACK)
        total_score += (red_defense - black_defense)

    # 棋子保护关系评估
    if protection_eval:
        red_protection = mmtl._evaluate_piece_protection(board, chessboard.RED)
        black_protection = mmtl._evaluate_piece_protection(board, chessboard.BLACK)
        total_score += (red_protection - black_protection)
    
    # 机动性评估（合法步数差）
    if moves_eval:
        red_moves = len(moves.generate_legal_moves(board, chessboard.RED))
        black_moves = len(moves.generate_legal_moves(board, chessboard.BLACK))
        total_score += (red_moves - black_moves) * 5  # 每多一个合法着法加5分
    
    # 综合评分（红方视角）
    total_score += ((red_material - black_material) 
                    + (red_position - black_position) )
    
    return total_score



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