'''
这个代码负责象棋界面的显示层，使用Tkinter库来创建一个图形界面，显示棋盘和棋子的位置。
它还处理用户的点击事件，以便玩家可以通过点击棋盘来移动棋子。
这个界面会根据游戏状态更新显示，提供一个直观的方式来进行游戏。
'''


import tkinter as tk
from tkinter import ttk
from basic import chessboard
from basic import moves


# 基础 UI 配置
CELL_SIZE = 55      # 格子大小
OFFSET_X = 40       # 左边距
OFFSET_Y = 40       # 上边距
PIECE_RADIUS = 22   # 棋子半径


def build_layout():
    """
    职责：创建窗口、画布、状态栏、重开按钮
    返回：包含界面对象引用的字典
    """
    root = tk.Tk()
    root.title("中国象棋 AI - 可视化界面")
    root.geometry("600x700")
    root.resizable(False, False)

    # --- 1. 顶部控制栏 ---
    control_frame = ttk.Frame(root, padding="10")
    control_frame.pack(side=tk.TOP, fill=tk.X)

    restart_btn = ttk.Button(control_frame, text="重新开始")
    restart_btn.pack(side=tk.LEFT)

    # --- 2. 棋盘画布 ---
    # 象棋棋盘比例约为 9:10，这里设置一个稍大的画布
    canvas = tk.Canvas(root, width=520, height=580, bg="#F4D39B", highlightthickness=0)
    canvas.pack(pady=10)

    # --- 3. 底部状态栏 ---
    status_var = tk.StringVar(value="准备就绪")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # 将所有需要交互的对象封装返回
    gui_components = {
        "root": root,
        "canvas": canvas,
        "restart_btn": restart_btn,
        "status_var": status_var,
        "status_bar": status_bar
    }
    
    return gui_components


def board_to_pixel(r, c):
    """
    职责：棋盘行列坐标 (0-9, 0-8) 转画布像素坐标 (x, y)。
    注意：象棋坐标 r 对应 y 方向，c 对应 x 方向。
    """
    x = OFFSET_X + c * CELL_SIZE
    y = OFFSET_Y + r * CELL_SIZE
    return x, y

def pixel_to_board(x, y):
    """
    鼠标像素坐标映射回最近棋盘点，并做边界过滤。
    return: (r, c) 或 None（如果点击位置超出有效范围）
    """
    # 逆向计算并取最近整数
    c = round((x - OFFSET_X) / CELL_SIZE)
    r = round((y - OFFSET_Y) / CELL_SIZE)

    # 边界过滤与感应范围检查 (点击位置距离交叉点不能太远，例如半个格子的 0.4 倍)
    if 0 <= r < 10 and 0 <= c < 9:
        target_x, target_y = board_to_pixel(r, c)
        distance = ((x - target_x)**2 + (y - target_y)**2)**0.5
        if distance < CELL_SIZE * 0.4:
            return r, c
    return None


def draw_board_background(canvas):
    """
    职责：画棋盘网格、九宫、楚河汉界。
    """
    canvas.delete("bg") # 清除旧背景
    
    # 1. 画横线
    for r in range(10):
        x0, y0 = board_to_pixel(r, 0)
        x1, y1 = board_to_pixel(r, 8)
        canvas.create_line(x0, y0, x1, y1, tags="bg")

    # 2. 画竖线
    for c in range(9):
        x0, y0 = board_to_pixel(0, c)
        x1, y1 = board_to_pixel(9, c)
        if c == 0 or c == 8:
            # 边线不断开
            canvas.create_line(x0, y0, x1, y1, tags="bg")
        else:
            # 中间纵线在河界处断开
            xm, ym_top = board_to_pixel(4, c)
            xm, ym_btm = board_to_pixel(5, c)
            canvas.create_line(x0, y0, xm, ym_top, tags="bg")
            canvas.create_line(xm, ym_btm, x1, y1, tags="bg")

    # 3. 画九宫斜线 (斜交叉)
    def draw_palace_x(top_r, c_center):
        # 左上到右下
        p1 = board_to_pixel(top_r, c_center-1)
        p2 = board_to_pixel(top_r+2, c_center+1)
        # 右上到左下
        p3 = board_to_pixel(top_r, c_center+1)
        p4 = board_to_pixel(top_r+2, c_center-1)
        canvas.create_line(p1, p2, tags="bg")
        canvas.create_line(p3, p4, tags="bg")

    draw_palace_x(0, 4) # 黑方九宫
    draw_palace_x(7, 4) # 红方九宫

    # 4. 楚河汉界文字
    tx, ty = board_to_pixel(4.5, 4) # 位于第4.5行中间
    canvas.create_text(tx - 100, ty, text="楚 河", font=("华文行楷", 24), tags="bg")
    canvas.create_text(tx + 100, ty, text="汉 界", font=("华文行楷", 24), tags="bg")


def draw_pieces(canvas, board):
    """
    职责：按 board 数据画棋子；区分红黑样式。
    """
    canvas.delete("piece") # 清除旧棋子
    
    # 棋子名称映射
    name_map = {
        'K': '帅', 'A': '仕', 'B': '相', 'N': '马', 'R': '车', 'C': '炮', 'P': '兵', # 红
        'k': '将', 'a': '士', 'b': '象', 'n': '馬', 'r': '車', 'c': '砲', 'p': '卒'  # 黑
    }

    for r in range(10):
        for c in range(9):
            piece = board[r][c]
            if piece == ".":
                continue
            
            side = piece[0]  # 'r' 或 'b'
            ptype = piece[1] # 'K', 'A' ...
            
            x, y = board_to_pixel(r, c)
            
            # 颜色区分
            color = "red" if side == 'r' else "black"
            text_char = name_map.get(ptype if side == 'r' else ptype.lower(), ptype)
            
            # 画棋子底盘
            canvas.create_oval(
                x - PIECE_RADIUS, y - PIECE_RADIUS,
                x + PIECE_RADIUS, y + PIECE_RADIUS,
                fill="#F0E68C", outline=color, width=2, tags="piece"
            )
            
            # 画棋子文字
            canvas.create_text(
                x, y, text=text_char, fill=color, 
                font=("微软雅黑", 16, "bold"), tags="piece"
            )



def ask_user_side():
    """
    弹窗询问玩家选择红方还是黑方
    返回: chessboard.RED (1) 或 chessboard.BLACK (-1)
    """
    # askyesno 返回 True(是) 或 False(否)
    from tkinter import messagebox
    ans = messagebox.askyesno("选择阵营", "你想作为红方（先行）吗？\n点击'是'选红方，'否'选黑方。")
    if ans:
        return chessboard.RED
    else:
        return chessboard.BLACK



def draw_selection(canvas, r, c):
    """
    职责：高亮当前选中的棋子。
    使用一个稍大的外框表示选中。
    """
    canvas.delete("selection")
    if r is None or c is None:
        return
    
    x, y = board_to_pixel(r, c)
    # 画一个比棋子稍大的虚线框
    padding = PIECE_RADIUS + 5
    canvas.create_rectangle(
        x - padding, y - padding,
        x + padding, y + padding,
        outline="gold", width=3, dash=(4, 4), tags="selection"
    )



def draw_legal_targets(canvas, legal_moves):
    """
    职责：高亮可落子点。
    legal_moves: 列表，元素为 Move 对象或 (r, c) 元组。
    """
    canvas.delete("targets")
    for move in legal_moves:
        # 兼容 Move 对象和元组
        tr = move.to_r if hasattr(move, 'to_r') else move[0]
        tc = move.to_c if hasattr(move, 'to_c') else move[1]
        
        x, y = board_to_pixel(tr, tc)
        # 画一个小实心圆点作为提示
        canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5,
            fill="#228B22", stipple="gray50", tags="targets"
        )



def render_all(ui, board, selected_pos=None, legal_moves=None):
    """
    职责：统一重绘入口。
    按图层顺序：背景 -> 棋子 -> 提示点 -> 选中框。
    """
    canvas = ui["canvas"]
    
    # 1. 背景层 (如果背景是静态的，可以只在初始化画一次，这里为了保险重绘)
    if not canvas.find_withtag("bg"):
        draw_board_background(canvas)

    # 2. 棋子层 (顶层)
    draw_pieces(canvas, board)
    
    # 3. 提示层
    if legal_moves:
        draw_legal_targets(canvas, legal_moves)
    else:
        canvas.delete("targets")
        
    # 4. 选中层
    if selected_pos:
        draw_selection(canvas, *selected_pos)
    else:
        canvas.delete("selection")
        
    

def show_message(title, message):
    """
    职责：弹出轻提示或终局提示。
    """
    from tkinter import messagebox
    messagebox.showinfo(title, message)



if __name__ == "__main__":
    pass