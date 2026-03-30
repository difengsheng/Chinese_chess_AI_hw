'''
这个代码负责象棋界面的流程交互层
包括选择棋子、移动棋子、判断胜负等功能
'''


from . import show
import chessboard
import moves
import rules
import random

# 假设你的可视化函数都在这个文件里，或者你可以根据实际文件名导入
# from visualize import build_layout, render_all, pixel_to_board, show_message

class ChessController:
    def __init__(self, ui_components):
        self.ui = ui_components
        self.reset_game()

    def create_initial_state(self):
        """职责：初始化棋盘、当前走方、选中点、可走点集合、游戏结束标记。"""
        self.board = chessboard.init_board()
        self.current_side = chessboard.RED
        self.selected_pos = None  # (r, c)
        self.legal_targets = []   # 当前选中棋子的可达目的坐标列表 [(r, c), ...]
        self.game_over = False
        self.all_legal_moves = moves.generate_legal_moves(self.board, self.current_side)

    def start_game(self):
        """职责：启动程序，绑定点击事件，触发首次渲染。"""
        self.ui["canvas"].bind("<Button-1>", self.on_canvas_click)
        self.ui["restart_btn"].config(command=self.reset_game)
        self.refresh_ui()
        self.ui["root"].mainloop()

    def on_canvas_click(self, event):
        """职责：统一处理点击逻辑，分派到选子或落子流程。"""
        if self.game_over:
            return

        pos = show.pixel_to_board(event.x, event.y) # 调用之前定义的坐标转换
        if not pos:
            return

        r, c = pos
        # 如果点击的是己方棋子 -> 进入选子流程
        if chessboard.is_friend_piece(self.board, r, c, self.current_side):
            self.try_select_piece(r, c)
        # 如果已经选中了棋子，且点击的是其他地方 -> 进入落子流程
        elif self.selected_pos:
            self.try_make_human_move(r, c)

    def try_select_piece(self, r, c):
        """职责：只允许当前方选子；成功后更新 selected 和 legal_targets。"""
        self.selected_pos = (r, c)
        self.legal_targets = self.collect_piece_legal_targets(r, c)
        self.ui["status_var"].set(f"已选中 {self.board[r][c]}，请选择落子点")
        self.refresh_ui()

    def collect_piece_legal_targets(self, from_r, from_c):
        """职责：从全局合法着法中过滤某一源点的终点集合。"""
        return [(m.to_r, m.to_c) for m in self.all_legal_moves 
                if m.from_r == from_r and m.from_c == from_c]

    def try_make_human_move(self, to_r, to_c):
        """职责：校验目标是否在 legal_targets，合法则执行走子并切换状态。"""
        if (to_r, to_c) in self.legal_targets:
            move = moves.Move(self.selected_pos[0], self.selected_pos[1], to_r, to_c)
            self.apply_move_and_refresh(move)
            
            if not self.game_over and self.current_side == chessboard.BLACK:
                # 轮到黑方（假设黑方是AI）
                self.ui["root"].after(500, self.run_ai_turn) 
        else:
            # 点击了非法位置，取消选中
            self.selected_pos = None
            self.legal_targets = []
            self.refresh_ui()

    def apply_move_and_refresh(self, move):
        """职责：落子后更新 board、清空选中、重绘界面。"""
        self.board = moves.make_move_copy(self.board, move)
        self.selected_pos = None
        self.legal_targets = []
        self.refresh_ui()
        
        if self.check_game_over():
            return

        self.switch_side()
        self.refresh_ui()

    def check_game_over(self):
        """职责：调用 winner 判定是否终局；终局则锁定输入。"""
        check_side = chessboard.BLACK if self.current_side == chessboard.RED else chessboard.RED
        win_side = rules.winner(self.board, check_side)
        if win_side:
            self.game_over = True
            msg = "红方胜！" if win_side == chessboard.RED else "黑方胜！"
            self.ui["status_var"].set(f"游戏结束: {msg}")
            show.show_message("终局", msg) # 调用之前定义的提示函数
            return True
        return False

    def run_ai_turn(self):
        """职责：调用随机AI拿一步，执行后刷新，并再次判终局。"""
        if self.game_over: return
        
        legal_moves = moves.generate_legal_moves(self.board, self.current_side)
        if legal_moves:
            ai_move = random.choice(legal_moves)
            self.apply_move_and_refresh(ai_move)

    def reset_game(self):
        """职责：恢复初始状态并重绘。"""
        self.create_initial_state()
        self.ui["status_var"].set("红方先行")
        self.refresh_ui()

    def switch_side(self):
        """职责：红黑方切换的单一出口函数。"""
        self.current_side = chessboard.BLACK if self.current_side == chessboard.RED else chessboard.RED
        self.all_legal_moves = moves.generate_legal_moves(self.board, self.current_side)

    def refresh_ui(self):
        """辅助函数：调用 render_all 刷新界面。"""
        show.render_all(self.ui, self.board, self.selected_pos, self.legal_targets)



def main():
    # 1. 创建 UI 引用
    ui = show.build_layout()
    
    # 2. 创建控制器并注入 UI
    # 控制器初始化时会自动调用 create_initial_state
    game_ctr = ChessController(ui)
    
    # 3. 启动游戏
    print("象棋程序已启动...")
    game_ctr.start_game()

if __name__ == "__main__":
    main()