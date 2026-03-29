# 1. 棋盘用 10 行 9 列，board[r][c]
# 2. r 从 0 到 9，c 从 0 到 8
# 3. 上方一方、下方一方固定好（比如红在下黑在上）
# 4. 楚河汉界只影响象和兵，不是障碍物

RED = "r"
BLACK = "b"
EMPTY = "."

BOARD_ROWS = 10
BOARD_COLS = 9

PIECE_TYPES = {"K", "A", "B", "N", "R", "C", "P"} # K将、A士、B象、N马、R车、C炮、P兵


def in_board(r, c):
    return 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS

def init_board():
    board = [[EMPTY for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    # 黑方
    board[0] = ["bR", "bN", "bB", "bA", "bK", "bA", "bB", "bN", "bR"]
    board[2][1] = "bC"
    board[2][7] = "bC"
    for c in range(0, BOARD_COLS, 2):
        board[3][c] = "bP"
    # 红方
    board[9] = ["rR", "rN", "rB", "rA", "rK", "rA", "rB", "rN", "rR"]
    board[7][1] = "rC"
    board[7][7] = "rC"
    for c in range(0, BOARD_COLS, 2):
        board[6][c] = "rP"
    return board

def print_board(board):
    for r in range(BOARD_ROWS):
        print(" ".join(board[r]))
        if r == 4:
            print("楚 河 汉 界") #楚河汉界居中

def side_of_piece(piece):
    if piece == EMPTY:
        return None
    return piece[0] # 'r' 或 'b'

def type_of_piece(piece):
    if piece == EMPTY:
        return None
    return piece[1] # 'K', 'A', 'B', 'N', 'R', 'C', 'P'

def is_friend_piece(board, r, c, side):
    piece = board[r][c]
    return piece != EMPTY and side_of_piece(piece) == side

def is_enemy_piece(board, r, c, side):
    piece = board[r][c]
    return piece != EMPTY and side_of_piece(piece) != side

def is_empty_piece(board, r, c):
    return board[r][c] == EMPTY


if __name__ == "__main__":
    pass