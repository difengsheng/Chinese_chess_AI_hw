from basic import chessboard
from basic import moves
from basic import rules
import time



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


def _evaluate_king_safety(board, side):
    """【新增加】评估将帅的安全性。将周围如果有对方棋子则扣分，被本方保护则加分。"""
    king_pos = moves.find_king(board, side)
    if not king_pos:
        return -10000
    kr, kc = king_pos
    safety_score = 0
    
    enemy_side = chessboard.BLACK if side == chessboard.RED else chessboard.RED
    # 距离将帅很近的地方如果有敌方棋子，严重扣分
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = kr + dr, kc + dc
            if chessboard.in_board(nr, nc):
                piece = board[nr][nc]
                if piece != chessboard.EMPTY and chessboard.side_of_piece(piece) == enemy_side:
                    safety_score -= 80
                elif piece != chessboard.EMPTY and chessboard.side_of_piece(piece) == side:
                    safety_score += 15 # 有己方棋子挨着，稍加安全性
    return safety_score

def _evaluate_mobility(board, side):
    """【新增加】机动性评估：合法着法的数量。由于走法越多的情况越灵活，予以适当加分。"""
    # 每多一个合法走步，奖励2分
    legal_moves_count = len(moves.generate_legal_moves(board, side))
    return legal_moves_count * 2

def _evaluate_defense_structure(board, side):
    """【新增加】防御结构评估：士象如果连在一起有保卫关系，给与加分"""
    defense_score = 0
    # 具体的士象双全判定较为繁琐，简易实现为存活数量的非线性加成
    counts = _count_pieces(board, side)
    if counts['A'] == 2: defense_score += 30 # 双士全
    if counts['B'] == 2: defense_score += 30 # 双象全
    return defense_score


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


def evaluate_board(board,
                   king_safety_eval = True,
                   defense_eval = True,
                   moves_eval = True):
    """扩展评估函数：包含多个维度的综合评估。"""

    piece_values = _get_dynamic_piece_values(board)

    red_material = 0
    black_material = 0
    red_position = 0
    black_position = 0

    total_score = 0

    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece == chessboard.EMPTY:
                continue

            ptype = chessboard.type_of_piece(piece)
            side = chessboard.side_of_piece(piece)
            base_value = piece_values[ptype]
            position_bonus = 0

            if ptype == "P":  
                position_bonus = _evaluate_pawn_position(board, r, c, side)
            elif ptype == "N":  
                position_bonus = _evaluate_knight_position(board, r, c, side)

            if side == chessboard.RED:
                red_material += base_value
                red_position += position_bonus
            else:
                black_material += base_value
                black_position += position_bonus

    if king_safety_eval:
        red_king_safety = _evaluate_king_safety(board, chessboard.RED)   
        black_king_safety = _evaluate_king_safety(board, chessboard.BLACK)
        total_score += (red_king_safety - black_king_safety)

    if defense_eval:
        red_defense = _evaluate_defense_structure(board, chessboard.RED) 
        black_defense = _evaluate_defense_structure(board, chessboard.BLACK)
        total_score += (red_defense - black_defense)

    if moves_eval:
        red_moves = _evaluate_mobility(board, chessboard.RED)    
        black_moves = _evaluate_mobility(board, chessboard.BLACK)
        total_score += (red_moves - black_moves)

    total_score += ((red_material - black_material) + (red_position - black_position))

    return total_score


def _quiescence_search(board, side, alpha, beta, q_depth, start_time, time_limit):
    if start_time is not None and time_limit is not None:
        if time.time() - start_time > time_limit:
            return evaluate_board(board)

    stand_pat = evaluate_board(board)

    if side == chessboard.RED:
        if stand_pat > alpha:
            alpha = stand_pat
        if stand_pat >= beta:
            return stand_pat
    else:
        if stand_pat < beta:
            beta = stand_pat
        if stand_pat <= alpha:
            return stand_pat

    if q_depth <= 0:
        return stand_pat

    legal_moves = moves.generate_legal_moves(board, side)
    capture_moves = [m for m in legal_moves if board[m.to_r][m.to_c] != chessboard.EMPTY]

    if not capture_moves:
        return stand_pat

    capture_moves = _sort_moves_with_heuristics(board, capture_moves)
    opponent_side = chessboard.BLACK if side == chessboard.RED else chessboard.RED

    if side == chessboard.RED:
        for move in capture_moves:
            new_board = moves.make_move_copy(board, move)
            score = _quiescence_search(new_board, opponent_side, alpha, beta, q_depth - 1, start_time, time_limit)
            if score >= beta:
                return score
            if score > alpha:
                alpha = score
        return alpha
    else:
        for move in capture_moves:
            new_board = moves.make_move_copy(board, move)
            score = _quiescence_search(new_board, opponent_side, alpha, beta, q_depth - 1, start_time, time_limit)
            if score <= alpha:
                return score
            if score < beta:
                beta = score
        return beta


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