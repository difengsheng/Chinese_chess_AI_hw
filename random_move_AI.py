import random

import chessboard
import moves
import rules
from visualize import show


def random_move_ai(board, side):
	"""随机走法 AI：返回一步合法走法，若无路可走则返回 None。"""
	legal_moves = moves.generate_legal_moves(board, side)
	if not legal_moves:
		return None
	return random.choice(legal_moves)


def random_move(board, steps=200, side=chessboard.RED):
	"""命令行随机对弈（保留原始用途，便于无界面调试）。"""
	current_side = side
	for step in range(steps):
		move = random_move_ai(board, current_side)
		print(f"Step {step}: {current_side} moves {move}")
		if move is None:
			print(f"Game over at step {step}. Winner: {rules.winner(board, current_side)}")
			return
		board = moves.make_move_copy(board, move)
		current_side = chessboard.BLACK if current_side == chessboard.RED else chessboard.RED

	print(f"Game ended after {steps} steps. No winner.")


class RandomAIVsAIController:
	"""使用现有 show 层进行随机 AI 自对弈。"""

	def __init__(self, ui_components, delay_ms=450, max_steps=500, start_side=chessboard.RED):
		self.ui = ui_components
		self.delay_ms = delay_ms
		self.max_steps = max_steps
		self.start_side = start_side
		self.after_id = None
		self.reset_game()

	def reset_game(self):
		self.board = chessboard.init_board()
		self.current_side = self.start_side
		self.step_count = 0
		self.game_over = False
		self._cancel_pending_timer()
		self.refresh_ui()
		self._update_status()

	def start_game(self):
		self.ui["restart_btn"].config(command=self.restart)
		# 自对弈模式不需要点击落子，保留画布只用于展示。
		self.ui["canvas"].bind("<Button-1>", lambda _event: None)
		self._schedule_next_turn(initial=True)
		self.ui["root"].mainloop()

	def restart(self):
		self.reset_game()
		self._schedule_next_turn(initial=True)

	def _schedule_next_turn(self, initial=False):
		if self.game_over:
			return
		delay = 200 if initial else self.delay_ms
		self.after_id = self.ui["root"].after(delay, self.run_one_turn)

	def run_one_turn(self):
		if self.game_over:
			return

		if self.step_count >= self.max_steps:
			self._finish_game(None, reason="达到最大步数，和棋")
			return

		move = random_move_ai(self.board, self.current_side)
		if move is None:
			winner_side = rules.winner(self.board, self.current_side)
			self._finish_game(winner_side, reason=f"{self._side_name(self.current_side)}无合法着法")
			return

		self.board = moves.make_move_copy(self.board, move)
		self.step_count += 1

		next_side = chessboard.BLACK if self.current_side == chessboard.RED else chessboard.RED
		winner_side = rules.winner(self.board, next_side)
		if winner_side is not None:
			self.current_side = next_side
			self.refresh_ui()
			self._finish_game(winner_side, reason="终局判定")
			return

		self.current_side = next_side
		self.refresh_ui()
		self._update_status(last_move=move)
		self._schedule_next_turn()

	def refresh_ui(self):
		show.render_all(self.ui, self.board, selected_pos=None, legal_moves=None)

	def _update_status(self, last_move=None):
		side_text = self._side_name(self.current_side)
		if last_move is None:
			self.ui["status_var"].set(f"随机对弈中 | 第{self.step_count}步 | 轮到{side_text}")
			return

		move_text = f"({last_move.from_r},{last_move.from_c})->({last_move.to_r},{last_move.to_c})"
		self.ui["status_var"].set(
			f"随机对弈中 | 第{self.step_count}步 {move_text} | 轮到{side_text}"
		)

	def _finish_game(self, winner_side, reason=""):
		self.game_over = True
		self._cancel_pending_timer()

		if winner_side is None:
			msg = f"对弈结束：{reason}"
		else:
			msg = f"{self._side_name(winner_side)}胜！"
			if reason:
				msg = f"{msg}（{reason}）"

		self.ui["status_var"].set(f"游戏结束 | {msg}")
		show.show_message("随机 AI 对弈结束", msg)

	def _cancel_pending_timer(self):
		if self.after_id is not None:
			self.ui["root"].after_cancel(self.after_id)
			self.after_id = None

	@staticmethod
	def _side_name(side):
		return "红方" if side == chessboard.RED else "黑方"


def main():
	ui = show.build_layout()
	controller = RandomAIVsAIController(ui_components=ui, delay_ms=450, max_steps=500)
	controller.start_game()


if __name__ == "__main__":
	main()
