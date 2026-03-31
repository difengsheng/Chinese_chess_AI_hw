
from basic import chessboard
from basic import moves
from basic import rules
from visualize import show
from visualize.controller import ChessController
from ulti import minmax_ulti as mmtl
import random
import time

def evaluate_board(board,
                   king_safety_eval = True,
                   protection_eval = False,
                   defense_eval = True,
                   moves_eval = True):
    """扩展评估函数：包含多个维度的综合评估。"""

    piece_values = mmtl._get_dynamic_piece_values(board)

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
                position_bonus = mmtl._evaluate_pawn_position(board, r, c, side)
            elif ptype == "N":  
                position_bonus = mmtl._evaluate_knight_position(board, r, c, side)

            if side == chessboard.RED:
                red_material += base_value
                red_position += position_bonus
            else:
                black_material += base_value
                black_position += position_bonus

    if king_safety_eval:
        red_king_safety = mmtl._evaluate_king_safety(board, chessboard.RED)   
        black_king_safety = mmtl._evaluate_king_safety(board, chessboard.BLACK)
        total_score += (red_king_safety - black_king_safety)

    if defense_eval:
        red_defense = mmtl._evaluate_defense_structure(board, chessboard.RED) 
        black_defense = mmtl._evaluate_defense_structure(board, chessboard.BLACK)
        total_score += (red_defense - black_defense)

    if moves_eval:
        red_moves = mmtl._evaluate_mobility(board, chessboard.RED)    
        black_moves = mmtl._evaluate_mobility(board, chessboard.BLACK)
        total_score += (red_moves - black_moves)

    total_score += ((red_material - black_material) + (red_position - black_position))

    return total_score

def _is_terminal(board, side):
    winner = rules.winner(board, side)
    if winner is not None:
        score = float("inf") if winner == chessboard.RED else float("-inf")     
        return True, winner, score
    return False, None, None

def _alphabeta_search(board, side = chessboard.RED, depth = 0, alpha = float("-inf"), beta = float("inf"), start_time = None, time_limit = None):
    if start_time is not None and time_limit is not None:
        if time.time() - start_time > time_limit:
            return None, evaluate_board(board)

    is_terminal, winner, score = _is_terminal(board, side)
    if is_terminal:
        return None, score

    if depth == 0:
        return None, evaluate_board(board)

    legal_moves = moves.generate_legal_moves(board, side)
    legal_moves = mmtl._sort_moves_with_heuristics(board, legal_moves)

    if not legal_moves:
        return None, float("-inf") if side == chessboard.RED else float("inf")  

    best_move = random.choice(legal_moves)
    opponent_side = chessboard.BLACK if side == chessboard.RED else chessboard.RED

    if side == chessboard.RED:
        max_value = float("-inf")
        for move in legal_moves:
            new_board = moves.make_move_copy(board, move)
            _, value = _alphabeta_search(new_board, opponent_side, depth - 1, alpha, beta, start_time, time_limit)

            if value > max_value:
                max_value = value
                best_move = move

            alpha = max(alpha, max_value)
            if beta <= alpha:
                mmtl._update_history_heuristic(move, depth, is_cutoff=True)     
                break

        return best_move, max_value
    else:
        min_value = float("inf")
        for move in legal_moves:
            new_board = moves.make_move_copy(board, move)
            _, value = _alphabeta_search(new_board, opponent_side, depth - 1, alpha, beta, start_time, time_limit)

            if value < min_value:
                min_value = value
                best_move = move

            beta = min(beta, min_value)
            if beta <= alpha:
                mmtl._update_history_heuristic(move, depth, is_cutoff=True)     
                break

        return best_move, min_value

def minmax_search(board, side, depth, time_limit=None):
    start_time = time.time() if time_limit else None
    return _alphabeta_search(board, side, depth, float("-inf"), float("inf"), start_time, time_limit)

def reset_search_heuristics():
    mmtl.reset_history_heuristic()

if __name__ == "__main__":
    board = chessboard.init_board()
    start_time = time.time()
    best_move, score = minmax_search(board, chessboard.RED, depth=3)
    end_time = time.time()
    print(f"Best Move: {best_move}, Score: {score}, completed in {end_time - start_time:.2f} seconds")


