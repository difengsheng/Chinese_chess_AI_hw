from basic import chessboard
from basic import moves
from basic import rules




PIECE_VALUES_BASE = {
    'K': 10000, 'R': 900, 'C': 450, 'N': 400, 
    'A': 200,   'B': 200, 'P': 100
}


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
    """评估将的安全性（周围士象防护）。"""
    king_pos = moves.find_king(board, side)
    if not king_pos:
        return 0
    
    kr, kc = king_pos
    safety_bonus = 0
    
    # 检查九宫内士象数量
    advisor_count = 0
    elephant_count = 0
    
    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece != chessboard.EMPTY and chessboard.side_of_piece(piece) == side:
                ptype = chessboard.type_of_piece(piece)
                if ptype == 'A':  # 士
                    advisor_count += 1
                    safety_bonus += 30
                elif ptype == 'B':  # 象
                    elephant_count += 1
                    safety_bonus += 25
    
    # 将周围有士象更安全
    if advisor_count >= 2 and elephant_count >= 2:
        safety_bonus += 50
    
    return safety_bonus


def _evaluate_defense_structure(board, side):
    """评估士象防御结构的完整性。"""
    bonus = 0
    advisor_count = 0
    elephant_count = 0
    
    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece != chessboard.EMPTY and chessboard.side_of_piece(piece) == side:
                ptype = chessboard.type_of_piece(piece)
                if ptype == 'A':
                    advisor_count += 1
                elif ptype == 'B':
                    elephant_count += 1
    
    # 完整的防御结构（2士2象）加分
    if advisor_count == 2:
        bonus += 40
    if elephant_count == 2:
        bonus += 40
    
    return bonus


def _evaluate_piece_protection(board, side):
    """评估棋子是否被保护（减少白送）。"""
    protection_bonus = 0
    opponent_side = chessboard.BLACK if side == chessboard.RED else chessboard.RED
    
    for r in range(chessboard.BOARD_ROWS):
        for c in range(chessboard.BOARD_COLS):
            piece = board[r][c]
            if piece == chessboard.EMPTY or chessboard.side_of_piece(piece) != side:
                continue
            
            # 检查该棋子是否被对方攻击
            is_attacked = False
            for opp_r in range(chessboard.BOARD_ROWS):
                for opp_c in range(chessboard.BOARD_COLS):
                    opp_piece = board[opp_r][opp_c]
                    if opp_piece != chessboard.EMPTY and chessboard.side_of_piece(opp_piece) == opponent_side:
                        attack_move = moves.Move(opp_r, opp_c, r, c)
                        if moves.is_valid_move(board, attack_move, opponent_side):
                            is_attacked = True
                            break
                if is_attacked:
                    break
            
            # 如果被攻击但被己方保护，减少惩罚
            if is_attacked:
                # 检查是否被己方保护
                is_protected = False
                for prot_r in range(chessboard.BOARD_ROWS):
                    for prot_c in range(chessboard.BOARD_COLS):
                        prot_piece = board[prot_r][prot_c]
                        if prot_piece != chessboard.EMPTY and chessboard.side_of_piece(prot_piece) == side:
                            protect_move = moves.Move(prot_r, prot_c, r, c)
                            if moves.is_valid_move(board, protect_move, side):
                                is_protected = True
                                break
                    if is_protected:
                        break
                
                if is_protected:
                    protection_bonus += 20  # 被保护的棋子加分
    
    return protection_bonus


if __name__ == "__main__":
    pass