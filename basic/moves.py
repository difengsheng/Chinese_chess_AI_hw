import copy
from dataclasses import dataclass
from . import chessboard


@dataclass(frozen=True)
class Move:
	"""表示一步走法：起点(from)到终点(to)。"""
	from_r: int
	from_c: int
	to_r: int
	to_c: int


def in_palace(side, r, c):
	"""判断位置是否在该方九宫内。"""
	if c < 3 or c > 5:
		return False
	if side == chessboard.BLACK:
		return 0 <= r <= 2
	return 7 <= r <= 9


def has_crossed_river(side, r):
	"""判断兵卒当前位置是否已过河。"""
	if side == chessboard.RED:
		return r <= 4
	return r >= 5


def blockers_between(board, from_r, from_c, to_r, to_c):
	"""统计同一直线上起终点之间的阻挡棋子数量。"""
	if from_r != to_r and from_c != to_c:
		return -1

	count = 0
	if from_r == to_r:
		step = 1 if to_c > from_c else -1
		c = from_c + step
		while c != to_c:
			if board[from_r][c] != chessboard.EMPTY:
				count += 1
			c += step
	else:
		step = 1 if to_r > from_r else -1
		r = from_r + step
		while r != to_r:
			if board[r][from_c] != chessboard.EMPTY:
				count += 1
			r += step
	return count


def _validate_king_move(board, move, side):
	"""校验将/帅走法：九宫内直走一步。"""
	if abs(move.to_r - move.from_r) + abs(move.to_c - move.from_c) != 1:
		return False
	return in_palace(side, move.to_r, move.to_c)


def _validate_advisor_move(board, move, side):
	"""校验士走法：九宫内斜走一步。"""
	if abs(move.to_r - move.from_r) != 1 or abs(move.to_c - move.from_c) != 1:
		return False
	return in_palace(side, move.to_r, move.to_c)


def _validate_elephant_move(board, move, side):
	"""校验象走法：田字两格、象眼不堵、不可过河。"""
	if abs(move.to_r - move.from_r) != 2 or abs(move.to_c - move.from_c) != 2:
		return False

	eye_r = (move.from_r + move.to_r) // 2
	eye_c = (move.from_c + move.to_c) // 2
	if board[eye_r][eye_c] != chessboard.EMPTY:
		return False

	if side == chessboard.RED and move.to_r < 5:
		return False
	if side == chessboard.BLACK and move.to_r > 4:
		return False
	return True


def _validate_knight_move(board, move, side):
	"""校验马走法：日字且马脚不被堵。"""
	dr = move.to_r - move.from_r
	dc = move.to_c - move.from_c
	adr = abs(dr)
	adc = abs(dc)

	if not ((adr == 2 and adc == 1) or (adr == 1 and adc == 2)):
		return False

	if adr == 2:
		leg_r = move.from_r + (1 if dr > 0 else -1)
		leg_c = move.from_c
	else:
		leg_r = move.from_r
		leg_c = move.from_c + (1 if dc > 0 else -1)

	return board[leg_r][leg_c] == chessboard.EMPTY


def _validate_rook_move(board, move, side):
	"""校验车走法：同列或同行且中间无阻挡。"""
	if move.from_r != move.to_r and move.from_c != move.to_c:
		return False
	return blockers_between(board, move.from_r, move.from_c, move.to_r, move.to_c) == 0


def _validate_cannon_move(board, move, side):
	"""校验炮走法：平移不隔子，吃子需隔一子。"""
	if move.from_r != move.to_r and move.from_c != move.to_c:
		return False

	block_count = blockers_between(board, move.from_r, move.from_c, move.to_r, move.to_c)
	if block_count < 0:
		return False

	target = board[move.to_r][move.to_c]
	if target == chessboard.EMPTY:
		return block_count == 0

	return block_count == 1 and chessboard.is_enemy_piece(board, move.to_r, move.to_c, side)


def _validate_pawn_move(board, move, side):
	"""校验兵卒走法：不过河直进，过河后可平移。"""
	dr = move.to_r - move.from_r
	dc = move.to_c - move.from_c
	forward = -1 if side == chessboard.RED else 1

	if not has_crossed_river(side, move.from_r):
		return dr == forward and dc == 0

	if dr == forward and dc == 0:
		return True
	if dr == 0 and abs(dc) == 1:
		return True
	return False


def _validate_piece_rule(board, move, side):
	"""按棋子类型分发到对应走法校验函数。"""
	piece_type = chessboard.type_of_piece(board[move.from_r][move.from_c])

	if piece_type == "K":
		return _validate_king_move(board, move, side)
	if piece_type == "A":
		return _validate_advisor_move(board, move, side)
	if piece_type == "B":
		return _validate_elephant_move(board, move, side)
	if piece_type == "N":
		return _validate_knight_move(board, move, side)
	if piece_type == "R":
		return _validate_rook_move(board, move, side)
	if piece_type == "C":
		return _validate_cannon_move(board, move, side)
	if piece_type == "P":
		return _validate_pawn_move(board, move, side)
	return False


def find_king(board, side):
	"""查找指定阵营将/帅的位置。"""
	target = side + "K"
	for r in range(chessboard.BOARD_ROWS):
		for c in range(chessboard.BOARD_COLS):
			if board[r][c] == target:
				return r, c
	return None


def kings_face_to_face(board):
	"""判断两将是否在同列且中间无遮挡。"""
	red_king = find_king(board, chessboard.RED)
	black_king = find_king(board, chessboard.BLACK)

	if red_king is None or black_king is None:
		return False

	rr, rc = red_king
	br, bc = black_king
	if rc != bc:
		return False

	return blockers_between(board, rr, rc, br, bc) == 0


def make_move_copy(board, move):
	"""复制棋盘并执行一步走子。"""
	new_board = copy.deepcopy(board)
	new_board[move.to_r][move.to_c] = new_board[move.from_r][move.from_c]
	new_board[move.from_r][move.from_c] = chessboard.EMPTY
	return new_board


def is_square_attacked(board, target_r, target_c, by_side):
	"""判断目标格是否被指定一方攻击。"""
	for r in range(chessboard.BOARD_ROWS):
		for c in range(chessboard.BOARD_COLS):
			piece = board[r][c]
			if piece == chessboard.EMPTY:
				continue
			if chessboard.side_of_piece(piece) != by_side:
				continue
			attack_move = Move(r, c, target_r, target_c)
			if _validate_piece_rule(board, attack_move, by_side):
				return True
	return False


def is_in_check(board, side):
	"""判断指定一方当前是否被将军。"""
	king_pos = find_king(board, side)
	if king_pos is None:
		return True

	enemy_side = chessboard.BLACK if side == chessboard.RED else chessboard.RED
	return is_square_attacked(board, king_pos[0], king_pos[1], enemy_side)


def is_valid_move(board, move, side):
	"""综合校验一步棋是否完全合法。"""
	# 1) Basic legality checks
	if not chessboard.in_board(move.from_r, move.from_c) or not chessboard.in_board(move.to_r, move.to_c):
		return False
	if move.from_r == move.to_r and move.from_c == move.to_c:
		return False

	piece = board[move.from_r][move.from_c]
	if piece == chessboard.EMPTY:
		return False
	if chessboard.side_of_piece(piece) != side:
		return False
	if chessboard.is_friend_piece(board, move.to_r, move.to_c, side):
		return False

	# 2) Piece-specific movement
	if not _validate_piece_rule(board, move, side):
		return False

	# 3) Common checks after move: kings facing and self-check
	next_board = make_move_copy(board, move)
	if kings_face_to_face(next_board):
		return False
	if is_in_check(next_board, side):
		return False

	return True


def generate_legal_moves(board, side):
	"""生成指定一方当前所有合法走法。"""
	legal = []
	for from_r in range(chessboard.BOARD_ROWS):
		for from_c in range(chessboard.BOARD_COLS):
			piece = board[from_r][from_c]
			if piece == chessboard.EMPTY:
				continue
			if chessboard.side_of_piece(piece) != side:
				continue

			for to_r in range(chessboard.BOARD_ROWS):
				for to_c in range(chessboard.BOARD_COLS):
					candidate = Move(from_r, from_c, to_r, to_c)
					if is_valid_move(board, candidate, side):
						legal.append(candidate)
	return legal

if __name__ == "__main__":
    pass