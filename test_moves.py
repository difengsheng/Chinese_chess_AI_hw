# testmove.py
import chessboard
import moves

def test_initial_board_no_move():
    """初始状态下，任何棋子未移动时，一些明显非法的移动应被拒绝。"""
    board = chessboard.init_board()
    side = chessboard.RED  # 红方先走（假设）

    # 1. 空起点
    assert not moves.is_valid_move(board, 5, 5, 5, 6, side)

    # 2. 起点不是本方棋子
    assert not moves.is_valid_move(board, 0, 0, 0, 1, side)  # 黑车

    # 3. 终点是己方棋子
    assert not moves.is_valid_move(board, 9, 0, 9, 1, side)  # 红车吃红马

    # 4. 移动到棋盘外
    assert not moves.is_valid_move(board, 9, 0, 10, 0, side)

    print("✅ 初始棋盘基础检查通过")


def test_king_moves():
    """测试将/帅的移动"""
    board = chessboard.init_board()
    side = chessboard.RED

    # 红帅初始位置 (9,4)
    # 合法移动：向前一步 (8,4)
    assert moves.is_valid_move(board, 9, 4, 8, 4, side)
    # 非法移动：斜走
    assert not moves.is_valid_move(board, 9, 4, 8, 5, side)
    # 非法移动：走出九宫
    assert not moves.is_valid_move(board, 9, 4, 9, 6, side)

    # 黑将初始位置 (0,4)
    side = chessboard.BLACK
    assert moves.is_valid_move(board, 0, 4, 1, 4, side)
    assert not moves.is_valid_move(board, 0, 4, 1, 5, side)

    print("✅ 将/帅移动测试通过")


def test_advisor_moves():
    """测试士的移动"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 红士初始位置 (9,3) 和 (9,5)
    # (9,3) 斜走到 (8,4) 合法
    assert moves.is_valid_move(board, 9, 3, 8, 4, side)
    # 直走非法
    assert not moves.is_valid_move(board, 9, 3, 8, 3, side)
    # 走出九宫非法
    assert not moves.is_valid_move(board, 9, 3, 8, 2, side)

    print("✅ 士移动测试通过")


def test_elephant_moves():
    """测试象的移动"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 红象初始 (9,2) 和 (9,6)
    # 田字移动 (9,2) -> (7,0) 中间 (8,1) 为空，且未过河（目标行7 >=5）合法
    assert moves.is_valid_move(board, 9, 2, 7, 0, side)
    # 田字但中心有子（象眼阻塞）——初始时 (8,1) 无子，但我们可手动添加
    board[8][1] = "rP"  # 放一个红兵堵象眼
    assert not moves.is_valid_move(board, 9, 2, 7, 0, side)
    board[8][1] = chessboard.EMPTY  # 恢复

    # 过河非法
    assert not moves.is_valid_move(board, 9, 2, 5, 0, side)

    print("✅ 象移动测试通过")


def test_knight_moves():
    """测试马的移动（蹩腿）"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 红马初始 (9,1) 和 (9,7)
    # (9,1) -> (7,2) 日字，无蹩腿
    assert moves.is_valid_move(board, 9, 1, 7, 2, side)
    # 蹩腿测试：在 (8,1) 放一个棋子，马腿被堵
    board[8][1] = "rP"
    assert not moves.is_valid_move(board, 9, 1, 7, 2, side)
    board[8][1] = chessboard.EMPTY

    # (9,1) -> (7,0) 也合法
    assert moves.is_valid_move(board, 9, 1, 7, 0, side)

    print("✅ 马移动测试通过")


def test_rook_moves():
    """测试车的移动（直线无阻挡）"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 红车初始 (9,0) 和 (9,8)
    # 向前走一步 (8,0) 合法
    assert moves.is_valid_move(board, 9, 0, 8, 0, side)
    # 横向移动 (9,0) -> (9,2) 中间有红马 (9,1) 阻挡，非法
    assert not moves.is_valid_move(board, 9, 0, 9, 2, side)
    # 吃掉敌方棋子：黑车 (0,0) 不能直接吃，中间有阻挡
    assert not moves.is_valid_move(board, 9, 0, 0, 0, side)

    # 清除阻挡后可以吃
    board[8][0] = chessboard.EMPTY
    board[7][0] = chessboard.EMPTY
    board[6][0] = chessboard.EMPTY
    board[5][0] = chessboard.EMPTY
    board[4][0] = chessboard.EMPTY
    board[3][0] = chessboard.EMPTY
    board[2][0] = chessboard.EMPTY
    board[1][0] = chessboard.EMPTY
    assert moves.is_valid_move(board, 9, 0, 0, 0, side)

    print("✅ 车移动测试通过")


def test_cannon_moves():
    """测试炮的移动（炮架规则）"""
    board = chessboard.init_board()
    side = chessboard.RED
    
    # 炮平移无阻挡
    assert moves.is_valid_move(board, 7, 1, 7, 2, side)
    # 炮不能吃己方
    assert not moves.is_valid_move(board, 7, 1, 7, 7, side)

    # 清空路径，放一个敌子作为"架"和一个敌子作为"目标"
    for r in range(6, 0, -1):
        board[r][1] = chessboard.EMPTY
    board[5][1] = "bP"  # 炮架在 (5,1)
    board[1][1] = "bR"  # 敌子在 (1,1)
    
    # 炮隔一个架吃敌子：(7,1) -> (1,1) 中间恰好一个子 (5,1)
    assert moves.is_valid_move(board, 7, 1, 1, 1, side)
    # 炮平移中间不能有架：(7,1) -> (3,1) 中间有 (5,1)
    assert not moves.is_valid_move(board, 7, 1, 3, 1, side)
    # 炮平移无架合法：(7,1) -> (6,1) 中间无子
    assert moves.is_valid_move(board, 7, 1, 6, 1, side)
    
    print("✅ 炮移动测试通过")


def test_pawn_moves():
    """测试兵卒的移动（过河前后）"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 红兵初始 (6,0) (6,2) (6,4) (6,6) (6,8)
    # 未过河只能前进
    assert moves.is_valid_move(board, 6, 0, 5, 0, side)
    assert not moves.is_valid_move(board, 6, 0, 6, 1, side)  # 不能横移
    assert not moves.is_valid_move(board, 6, 0, 7, 0, side)  # 不能后退

    # 过河后可以左右前，不能后退
    # 移动兵到河对岸 (r=4)
    board[4][0] = "rP"
    board[6][0] = chessboard.EMPTY
    assert moves.is_valid_move(board, 4, 0, 3, 0, side)   # 前进吃子
    assert moves.is_valid_move(board, 4, 0, 4, 1, side)   # 右移
    assert not moves.is_valid_move(board, 4, 0, 4, -1, side)  # 左移（边界内？c=-1非法会被in_board过滤）
    # 但实际左移出界，先检查 in_board 会返回 False，所以安全
    assert not moves.is_valid_move(board, 4, 0, 5, 0, side)  # 后退非法

    print("✅ 兵移动测试通过")


def test_king_face_to_face():
    """测试将帅对面规则"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 初始状态将帅不在同列
    assert not moves.kings_face_to_face(board)

    # 移动红帅到 (8,4)，黑将不动，现在同列 (4) 但中间有棋子
    board = moves.make_move_copy(board, 9, 4, 8, 4)
    assert not moves.kings_face_to_face(board)

    # 清除中间所有棋子
    for r in range(1, 8):
        board[r][4] = chessboard.EMPTY
    assert moves.kings_face_to_face(board)

    # 测试移动合法性：红方不能走成将帅对面
    board = chessboard.init_board()
    # 先清空中间所有棋子（包括黑方和红方之间的）
    for r in range(1, 9):
        for c in range(9):
            board[r][c] = chessboard.EMPTY
    board[0][4] = "bK"
    board[9][4] = "rK"
    # 此时已经将帅对面，但初始状态就不合法，不过我们的 is_valid_move 会拒绝任何导致对面的走法
    # 尝试移动红帅到 (8,4) 仍然对面且中间无子，应非法
    assert not moves.is_valid_move(board, 9, 4, 8, 4, chessboard.RED)

    print("✅ 将帅对面测试通过")


def test_self_check():
    """测试移动后不能使自己被将军"""
    board = chessboard.init_board()
    side = chessboard.RED
    # 移动红马到可以送吃的位置？比如红马 (9,1) 移动到 (7,2)，那里安全，不会被将
    assert moves.is_valid_move(board, 9, 1, 7, 2, side)

    # 构造一个送吃的局面：红帅前移，暴露给黑车
    board = chessboard.init_board()
    # 把黑车移到可以直对红帅的位置
    board[0][0] = chessboard.EMPTY
    board[7][4] = "bR"  # 黑车放在红帅正前方两格
    # 红帅 (9,4) 向前一步到 (8,4) 会被黑车吃掉吗？会，因为黑车直线无阻挡
    # 但移动后自己的将处于被吃状态，应该非法
    assert not moves.is_valid_move(board, 9, 4, 8, 4, chessboard.RED)

    print("✅ 自将检查测试通过")


def test_generate_legal_moves():
    """测试生成所有合法走法函数（只检查数量非零且包含一些已知走法）"""
    board = chessboard.init_board()
    red_moves = moves.generate_legal_moves(board, chessboard.RED)
    black_moves = moves.generate_legal_moves(board, chessboard.BLACK)
    # 初始红方有 44 种合法走法（标准中国象棋初始红方合法走法数量，此处不严格，但应 > 0）
    assert len(red_moves) > 0
    assert len(black_moves) > 0
    # 检查已知的合法走法是否在列表中
    assert (9, 4, 8, 4) in red_moves  # 红帅前移
    assert (9, 1, 7, 2) in red_moves  # 红马跳出
    assert (7, 1, 7, 2) in red_moves  # 红炮平移
    print(f"✅ 生成合法走法测试通过：红方 {len(red_moves)} 步，黑方 {len(black_moves)} 步")


def run_all_tests():
    test_initial_board_no_move()
    test_king_moves()
    test_advisor_moves()
    test_elephant_moves()
    test_knight_moves()
    test_rook_moves()
    test_cannon_moves()
    test_pawn_moves()
    test_king_face_to_face()
    test_self_check()
    test_generate_legal_moves()
    print("\n🎉 所有测试通过！你的走法函数工作正常。")


if __name__ == "__main__":
    run_all_tests()