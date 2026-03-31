from basic import chessboard
from basic import moves
from basic import rules




PIECE_VALUES_BASE = {
    'K': 10000, 'R': 900, 'C': 450, 'N': 400, 
    'A': 200,   'B': 200, 'P': 100
}

# 全局历史启发表：记录过去搜索中表现好的着法
# 键：(from_r, from_c, to_r, to_c)
# 值：该着法的累积启发值（越高越好）
history_heuristic = {}


def _count_pieces(board, side):
    """统计某一方各类棋子数量。"""
    counts = {'K': 0, 'R': 0, 'C': 0, 'N': 0, 'A': 0, 'B': 0, 'P': 0}
    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece != chessboard.EMPTY and chessboard.side_of_piece(piece) == side:
                ptype = chessboard.type_of_piece(piece)
                counts[ptype] += 1
    return counts


def _get_dynamic_piece_values(board):
    """根据残局阶段动态调整棋子价值。"""
    red_counts = _count_pieces(board, chessboard.RED)
    black_counts = _count_pieces(board, chessboard.BLACK)
    
    total_pieces = sum(red_counts.values()) + sum(black_counts.values())
    
    # 权重调整因子（残局时兵和马更值钱）
    if total_pieces < 10:  # 很少的棋子，深残局
        factor_pawn = 1.5
        factor_knight = 1.2
    elif total_pieces < 20:  # 中残局
        factor_pawn = 1.3
        factor_knight = 1.1
    else:  # 开局和中盘
        factor_pawn = 1.0
        factor_knight = 1.0
    
    values = PIECE_VALUES_BASE.copy()
    values['P'] = int(values['P'] * factor_pawn)
    values['N'] = int(values['N'] * factor_knight)
    return values


def _evaluate_pawn_position(board, r, c, side):
    """评估兵的位置价值。"""
    bonus = 0
    
    if moves.has_crossed_river(side, r):
        bonus += 50  # 过河兵加分
        
        # 兵更接近敌方阵地加分
        if side == chessboard.RED:
            bonus += (4 - r) * 20  # 红方在上加分
        else:
            bonus += (r - 5) * 20  # 黑方在下加分
    
    return bonus


def _evaluate_knight_position(board, r, c, side):
    """评估马的中心活跃度。"""
    # 马在中心（3-5列）活跃度高
    center_dist = abs(c - 4)
    bonus = (5 - center_dist) * 15
    return bonus


def _mvv_lva_score(board, move):
    """MVV-LVA (Most Valuable Victim - Least Valuable Attacker)评分。
    
    返回值越高，着法优先级越高。
    公式: 被吃棋子价值 * 1000 - 攻击者价值
    这样优先搜索"小子吃大子"的着法。
    """
    target_piece = board[move.to_r][move.to_c]
    
    # 不是吃子着法，返回-1000（最低优先级）
    if target_piece == chessboard.EMPTY:
        return -1000
    
    # 获取被吃棋子的价值
    victim_type = chessboard.type_of_piece(target_piece)
    victim_value = PIECE_VALUES_BASE.get(victim_type, 0)
    
    # 获取攻击者的价值（更低更优先）
    attacker_piece = board[move.from_r][move.from_c]
    attacker_type = chessboard.type_of_piece(attacker_piece)
    attacker_value = PIECE_VALUES_BASE.get(attacker_type, 0)
    
    # MVV-LVA评分：被吃价值 * 1000 - 攻击者价值
    # 这样同一个被吃棋子下，用低价值的攻击者优先
    return victim_value * 1000 - attacker_value


def _sort_moves_with_heuristics(board, moves_list):
    """使用多层启发式排序着法。
    
    优先级从高到低：
    1. 历史启发：过去表现好的着法
    2. MVV-LVA：小子吃大子的着法
    3. 吃子优先：有任何吃子
    """
    def move_sort_key(move):
        move_tuple = (move.from_r, move.from_c, move.to_r, move.to_c)
        
        # 历史启发值（有记录则取值，无则为0）
        history_value = history_heuristic.get(move_tuple, 0)
        
        # MVV-LVA评分
        mvv_lva = _mvv_lva_score(board, move)
        
        # 是否是吃子着法
        is_capture = board[move.to_r][move.to_c] != chessboard.EMPTY
        
        # 返回排序键（元组：按优先级从高到低）
        # Python会从左到右比较元组元素，倒序排列（reverse=True）
        return (history_value, mvv_lva, is_capture)
    
    return sorted(moves_list, key=move_sort_key, reverse=True)


def _update_history_heuristic(move, depth, is_cutoff=False):
    """更新历史启发表。
    
    Args:
        move: 着法
        depth: 当前搜索深度
        is_cutoff: 是否产生了剪枝（Beta剪枝）
    """
    if is_cutoff:
        move_tuple = (move.from_r, move.from_c, move.to_r, move.to_c)
        # 深度越大（接近根节点）剪枝，启发值越高
        history_heuristic[move_tuple] = history_heuristic.get(move_tuple, 0) + depth * depth


def reset_history_heuristic():
    """重置历史启发表（用于多局游戏）。"""
    global history_heuristic
    history_heuristic = {}


if __name__ == "__main__":
    pass