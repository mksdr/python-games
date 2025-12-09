import tkinter as tk
import random

# --- 상수 정의 ---
TILE_SIZE = 24
GAME_SPEED_MS = 150

# 맵 정의: 1 = 벽, 0 = 길 (점), 2 = 팩맨, 4 = 유령, 5 = 유령 문
GAME_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 5, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 5, 4, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

DIRECTIONS = ["Up", "Left", "Down", "Right"]  # 우선순위 (팩맨 규칙)
DIR_OFFSET = {"Left": (0, -1), "Right": (0, 1), "Up": (-1, 0), "Down": (1, 0)}

class PacManGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Pac-Man")

        self.score = 0
        self.dots_remaining = 0
        self.game_over = False

        self.map_height = len(GAME_MAP)
        self.map_width = len(GAME_MAP[0])
        self.canvas_width = self.map_width * TILE_SIZE
        self.canvas_height = self.map_height * TILE_SIZE

        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 16))
        self.score_label.pack()

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

        self.start_button = tk.Button(root, text="START", font=("Arial", 16), command=self.start_game)
        self.start_button.pack(pady=10)

        self.game_running = False
        self.game_over_text_id = None

        self.map = [row[:] for row in GAME_MAP]
        self.dots = {}
        self.player_pos = None
        self.ghost_pos = None
        self.player_direction = "Right"
        self.player_next_direction = "Right"
        self.player_id = None
        self.ghost_id = None
        self.ghost_direction = "Up"

        self.draw_map()

        self.root.bind("<KeyPress-Left>", self.key_pressed)
        self.root.bind("<KeyPress-Right>", self.key_pressed)
        self.root.bind("<KeyPress-Up>", self.key_pressed)
        self.root.bind("<KeyPress-Down>", self.key_pressed)

    # --- 유틸리티 ---
    def _cell_bbox(self, r, c, pad=2):
        x1 = c * TILE_SIZE + pad
        y1 = r * TILE_SIZE + pad
        x2 = (c + 1) * TILE_SIZE - pad
        y2 = (r + 1) * TILE_SIZE - pad
        return x1, y1, x2, y2

    def _move_canvas_item(self, item_id, r, c):
        self.canvas.coords(item_id, *self._cell_bbox(r, c))

    def _create_entity(self, r, c, kind):
        bbox = self._cell_bbox(r, c)
        if kind == "player":
            return self.canvas.create_oval(*bbox, fill="yellow", outline="")
        if kind == "ghost":
            return self.canvas.create_rectangle(*bbox, fill="red", outline="")
        return None

    # --- 맵/렌더링 ---
    def draw_map(self):
        for r in range(self.map_height):
            for c in range(self.map_width):
                x1, y1, x2, y2 = c * TILE_SIZE, r * TILE_SIZE, (c + 1) * TILE_SIZE, (r + 1) * TILE_SIZE
                cell = self.map[r][c]

                if cell == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="")
                elif cell == 0:
                    dot_bbox = (x1 + TILE_SIZE // 2 - 2, y1 + TILE_SIZE // 2 - 2,
                                x1 + TILE_SIZE // 2 + 2, y1 + TILE_SIZE // 2 + 2)
                    dot_id = self.canvas.create_oval(*dot_bbox, fill="white", outline="")
                    self.dots[(r, c)] = dot_id
                    self.dots_remaining += 1
                elif cell == 2:
                    self.player_pos = [r, c]
                    self.player_id = self._create_entity(r, c, "player")
                elif cell == 4:
                    self.ghost_pos = [r, c]
                    self.ghost_id = self._create_entity(r, c, "ghost")
                # cell == 5 : invisible gate, do nothing

    # --- 입력 ---
    def key_pressed(self, event):
        if self.game_running:
            self.player_next_direction = event.keysym

    # --- 게임 루프 ---
    def game_loop(self):
        if self.game_over or not self.game_running:
            return

        self.move_player()
        self.move_ghost()
        self.check_collisions()
        self.update_score()
        self.check_win_loss()

        self.root.after(GAME_SPEED_MS, self.game_loop)

    # --- 이동/충돌 ---
    def get_next_pos(self, r, c, direction):
        dr, dc = DIR_OFFSET.get(direction, (0, 0))
        r += dr
        c += dc

        # 터널
        if r == 9 and c == -1:
            c = self.map_width - 1
        elif r == 9 and c == self.map_width:
            c = 0
        return r, c

    def is_wall(self, r, c):
        if 0 <= r < self.map_height and 0 <= c < self.map_width:
            if self.map[r][c] == 5:
                return True  # 팩맨에게는 벽
            return self.map[r][c] == 1
        return True

    def move_player(self):
        r, c = self.player_pos
        next_r_try, next_c_try = self.get_next_pos(r, c, self.player_next_direction)
        if not self.is_wall(next_r_try, next_c_try):
            self.player_direction = self.player_next_direction

        next_r, next_c = self.get_next_pos(r, c, self.player_direction)
        if not self.is_wall(next_r, next_c):
            self.player_pos = [next_r, next_c]
            self._move_canvas_item(self.player_id, next_r, next_c)

    def get_reverse_direction(self, direction):
        return {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}.get(direction)

    def move_ghost(self):
        pr, pc = self.player_pos
        gr, gc = self.ghost_pos

        reverse_dir = self.get_reverse_direction(self.ghost_direction)
        candidates = []

        for direction in DIRECTIONS:
            if direction == reverse_dir:
                continue
            nr, nc = self.get_next_pos(gr, gc, direction)
            if 0 <= nr < self.map_height and 0 <= nc < self.map_width and self.map[nr][nc] != 1:
                candidates.append((direction, nr, nc))

        if not candidates:
            nr, nc = self.get_next_pos(gr, gc, reverse_dir)
            if 0 <= nr < self.map_height and 0 <= nc < self.map_width and self.map[nr][nc] != 1:
                candidates.append((reverse_dir, nr, nc))
            if not candidates:
                return

        best = candidates[0]
        min_dist = (best[1] - pr) ** 2 + (best[2] - pc) ** 2

        for cand in candidates[1:]:
            dist = (cand[1] - pr) ** 2 + (cand[2] - pc) ** 2
            if dist < min_dist or (dist == min_dist and DIRECTIONS.index(cand[0]) < DIRECTIONS.index(best[0])):
                best, min_dist = cand, dist

        self.ghost_direction = best[0]
        self.ghost_pos = [best[1], best[2]]
        self._move_canvas_item(self.ghost_id, best[1], best[2])

    def check_collisions(self):
        pos = tuple(self.player_pos)
        if pos in self.dots:
            self.canvas.delete(self.dots.pop(pos))
            self.score += 10
            self.dots_remaining -= 1

    # --- UI/상태 ---
    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def start_game(self):
        if self.game_running:
            return
        if self.game_over:
            self.reset_game()

        self.game_running = True
        self.start_button.config(state=tk.DISABLED)

        if self.game_over_text_id:
            self.canvas.delete(self.game_over_text_id)
            self.game_over_text_id = None

        self.game_loop()

    def reset_game(self):
        self.canvas.delete("all")
        self.score = 0
        self.dots_remaining = 0
        self.game_over = False
        self.game_running = False

        self.dots.clear()
        self.player_pos = None
        self.ghost_pos = None
        self.player_direction = "Right"
        self.player_next_direction = "Right"
        self.ghost_direction = "Up"
        self.game_over_text_id = None
        self.map = [row[:] for row in GAME_MAP]

        self.draw_map()
        self.update_score()
        self.start_button.config(text="START")

    def check_win_loss(self):
        if self.player_pos == self.ghost_pos:
            message, color = "GAME OVER", "red"
            self.game_over = True
        elif self.dots_remaining == 0:
            message, color = "YOU WIN!", "green"
            self.game_over = True
        else:
            return

        self.game_running = False
        self.game_over_text_id = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text=message, fill=color, font=("Arial", 40, "bold"),
        )
        self.start_button.config(text="RESTART", state=tk.NORMAL)

# --- 메인 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    game = PacManGame(root)
    root.mainloop()