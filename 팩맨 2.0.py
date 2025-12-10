import pygame
import sys
import math
import random

# --- 초기화 ---
pygame.init()

# --- 상수 ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 520
FPS = 60
MAZE_TOP_OFFSET = 50
GRID_SIZE = 30
PLAYER_SPEED = 2.5
GHOST_SPEED = 2
GHOST_FRIGHTENED_SPEED = 1.5
FRIGHTENED_DURATION = 7 * FPS # 7 seconds

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (25, 25, 166)
PELLET_COLOR = (255, 204, 153)
RED = (255, 0, 0)
PINK = (255, 184, 222)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
FRIGHTENED_COLOR = (50, 50, 255)
FRIGHTENED_FLASH_COLOR = (200, 200, 255)

# --- 화면 설정 ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("팩맨")
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgun gothic", 28)
big_font = pygame.font.SysFont("malgun gothic", 56)

# --- 미로 데이터 ---
original_maze = [
    "WWWWWWWWWWWWWWWWWWWW",
    "WP........W........PW",
    "W.WW.WWW.WW.WWW.WW.W",
    "W.WW.WWW.WW.WWW.WW.W",
    "W..................W",
    "W.WW.W.WWWWWW.W.WW.W",
    "W....W...WW...W....W",
    "WWWW.WWWW..WWWW.WWWW",
    "   W.W G G  W.W   ",
    "WWWW.W.WWWWWW.W.WWWW",
    "W......W....W......W",
    "W.WWWW.W.WW.W.WWWW.W",
    "WP.................PW",
    "WWWWWWWWWWWWWWWWWWWW",
]
maze = original_maze.copy()

# --- 공통 유틸리티 함수 ---
def get_grid_pos(pos):
    return int(pos.x / GRID_SIZE), int((pos.y - MAZE_TOP_OFFSET) / GRID_SIZE)

def is_wall(grid_pos):
    x, y = grid_pos
    if 0 <= y < len(maze) and 0 <= x < len(maze[0]):
        return maze[y][x] == 'W'
    return True

# --- 플레이어 클래스 ---
class Player:
    def __init__(self, x, y):
        self.start_pos = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        self.radius = GRID_SIZE // 2 - 2
        self.speed = PLAYER_SPEED
        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius*2)
        self.mouth_angle = 0
        self.mouth_open = True

    def reset(self):
        self.pos = pygame.Vector2(self.start_pos.x, self.start_pos.y)
        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)

    def draw(self, screen):
        self.rect.center = self.pos
        
        # Animate mouth
        self.mouth_angle = (math.sin(pygame.time.get_ticks() * 0.02) + 1) / 2 * 45 
        
        # Rotate Pac-Man to face direction
        angle = self.direction.angle_to(pygame.Vector2(1, 0))
        
        start_angle = math.radians(angle + self.mouth_angle)
        end_angle = math.radians(angle - self.mouth_angle + 360)

        if self.direction == (0,0): # Not moving, close mouth
            pygame.draw.circle(screen, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)
        else:
            pygame.draw.arc(screen, YELLOW, self.rect, start_angle, end_angle, self.radius)


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.next_direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]: self.next_direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP]: self.next_direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN]: self.next_direction = pygame.Vector2(0, 1)

    def can_move(self, pos, direction):
        check_pos = pos + direction * GRID_SIZE
        grid_x, grid_y = get_grid_pos(check_pos)
        return not is_wall((grid_x, grid_y))

    def move(self):
        is_on_grid_x = abs(self.pos.x % GRID_SIZE - (GRID_SIZE / 2)) < self.speed
        is_on_grid_y = abs((self.pos.y - MAZE_TOP_OFFSET) % GRID_SIZE - (GRID_SIZE / 2)) < self.speed

        if is_on_grid_x and is_on_grid_y:
            current_grid_pos_pixels = pygame.Vector2(
                (int(self.pos.x / GRID_SIZE) * GRID_SIZE) + GRID_SIZE / 2,
                (int((self.pos.y - MAZE_TOP_OFFSET)/ GRID_SIZE) * GRID_SIZE) + GRID_SIZE / 2 + MAZE_TOP_OFFSET)
            if self.next_direction != (0,0) and self.can_move(current_grid_pos_pixels, self.next_direction):
                self.pos = current_grid_pos_pixels
                self.direction = self.next_direction
                self.next_direction = pygame.Vector2(0,0)
            elif not self.can_move(current_grid_pos_pixels, self.direction):
                self.pos = current_grid_pos_pixels
                self.direction = pygame.Vector2(0,0) # Stop
        
        if self.direction != (0,0):
             self.pos += self.direction * self.speed

# --- 고스트 클래스 ---
class Ghost:
    def __init__(self, x, y, color):
        self.start_pos = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        self.radius = GRID_SIZE // 2 - 2
        self.color = color
        self.direction = random.choice([pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)])
        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius*2)
        self.state = "CHASE" # CHASE, FRIGHTENED
        self.speed = GHOST_SPEED

    def reset(self):
        self.pos = pygame.Vector2(self.start_pos.x, self.start_pos.y)
        self.direction = random.choice([pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)])
        self.state = "CHASE"
        self.speed = GHOST_SPEED

    def draw(self, screen):
        self.rect.center = self.pos
        body_rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius/2, self.radius*2, self.radius*2)
        
        current_color = self.color
        if self.state == "FRIGHTENED":
            if frightened_mode_timer < 2 * FPS: # Flash for last 2 seconds
                current_color = FRIGHTENED_FLASH_COLOR if (pygame.time.get_ticks() // 200) % 2 == 0 else FRIGHTENED_COLOR
            else:
                current_color = FRIGHTENED_COLOR

        pygame.draw.circle(screen, current_color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.rect(screen, current_color, body_rect)
        
        # Eyes
        eye_y = self.pos.y - self.radius / 4
        eye_l_x = self.pos.x - self.radius / 2.5
        eye_r_x = self.pos.x + self.radius / 2.5
        eye_radius = self.radius / 4
        pygame.draw.circle(screen, WHITE, (int(eye_l_x), int(eye_y)), int(eye_radius))
        pygame.draw.circle(screen, WHITE, (int(eye_r_x), int(eye_y)), int(eye_radius))

        # Pupils
        pupil_offset = self.direction * eye_radius * 0.6
        pupil_radius = eye_radius / 2
        pygame.draw.circle(screen, BLACK, (int(eye_l_x + pupil_offset.x), int(eye_y + pupil_offset.y)), int(pupil_radius))
        pygame.draw.circle(screen, BLACK, (int(eye_r_x + pupil_offset.x), int(eye_y + pupil_offset.y)), int(pupil_radius))


    def can_move(self, pos, direction):
        check_pos = pos + direction * GRID_SIZE
        grid_x, grid_y = get_grid_pos(check_pos)
        return not is_wall((grid_x, grid_y))

    def move(self):
        if self.state == "FRIGHTENED": self.speed = GHOST_FRIGHTENED_SPEED
        else: self.speed = GHOST_SPEED

        is_on_grid_x = abs(self.pos.x % GRID_SIZE - (GRID_SIZE / 2)) < self.speed
        is_on_grid_y = abs((self.pos.y - MAZE_TOP_OFFSET) % GRID_SIZE - (GRID_SIZE / 2)) < self.speed

        if is_on_grid_x and is_on_grid_y:
            current_grid_pos_pixels = pygame.Vector2(
                (int(self.pos.x / GRID_SIZE) * GRID_SIZE) + GRID_SIZE / 2,
                (int((self.pos.y - MAZE_TOP_OFFSET)/ GRID_SIZE) * GRID_SIZE) + GRID_SIZE / 2 + MAZE_TOP_OFFSET )
            
            possible_directions = [d for d in [pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)] if self.can_move(current_grid_pos_pixels, d)]
            
            if len(possible_directions) > 1 and self.direction * -1 in possible_directions:
                possible_directions.remove(self.direction * -1)

            if not self.can_move(current_grid_pos_pixels, self.direction) or (len(possible_directions) > 1 and random.random() < 0.2):
                self.pos = current_grid_pos_pixels
                if possible_directions: self.direction = random.choice(possible_directions)
        
        self.pos += self.direction * self.speed

# --- 펠렛 클래스 ---
class Pellet:
    def __init__(self, x, y, is_power=False):
        self.pos = pygame.Vector2(x, y)
        self.is_power = is_power
        self.radius = 6 if is_power else 3
        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        pygame.draw.circle(screen, PELLET_COLOR, (int(self.pos.x), int(self.pos.y)), self.radius)

# --- 그리기 함수 ---
def draw_game_elements():
    draw_maze()
    for pellet in pellets: pellet.draw(screen)
    player.draw(screen)
    for ghost in ghosts: ghost.draw(screen)
    draw_ui()

def draw_maze():
    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            if char == 'W':
                pygame.draw.rect(screen, BLUE, (x * GRID_SIZE, y * GRID_SIZE + MAZE_TOP_OFFSET, GRID_SIZE, GRID_SIZE))

def draw_ui():
    score_text = font.render(f"점수: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_start_screen():
    screen.fill(BLACK)
    title = big_font.render("팩맨", True, YELLOW)
    prompt = font.render("시작하려면 아무 키나 누르세요.", True, WHITE)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
    screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)))

def draw_end_screen(message):
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH/4, SCREEN_HEIGHT/2 - (SCREEN_HEIGHT/6), SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
    end_text = big_font.render(message, True, RED if message == "GAME OVER" else YELLOW)
    score_text = font.render(f"총점: {score}", True, WHITE)
    restart_text = font.render("다시 시작하려면 아무 키나 누르세요.", True, WHITE)
    screen.blit(end_text, end_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
    screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20)))
    screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 70)))

# --- 게임 상태 관리 ---
game_state = "START"
score = 0
pellets = []
ghosts = []
frightened_mode_timer = 0
player = Player(GRID_SIZE * 1.5, MAZE_TOP_OFFSET + GRID_SIZE * 1.5)

def reset_game():
    global score, maze, pellets, ghosts, frightened_mode_timer
    score = 0
    frightened_mode_timer = 0
    maze = original_maze.copy()
    pellets.clear()
    ghosts.clear()
    player.reset()

    ghost_colors = [RED, PINK, CYAN, ORANGE]
    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            pos_x, pos_y = x * GRID_SIZE + GRID_SIZE / 2, y * GRID_SIZE + MAZE_TOP_OFFSET + GRID_SIZE / 2
            if char == '.': pellets.append(Pellet(pos_x, pos_y))
            elif char == 'P': pellets.append(Pellet(pos_x, pos_y, is_power=True))
            elif char == 'G' and len(ghosts) < 4:
                ghosts.append(Ghost(pos_x, pos_y, ghost_colors.pop(0)))
    for ghost in ghosts: ghost.reset()

# --- 게임 루프 ---
running = True
reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "START": game_state = "PLAYING"
            elif game_state in ["GAME_OVER", "WIN"]:
                reset_game()
                game_state = "START"

    screen.fill(BLACK)

    if game_state == "START":
        draw_start_screen()
    elif game_state == "PLAYING":
        if frightened_mode_timer > 0:
            frightened_mode_timer -= 1
            if frightened_mode_timer == 0:
                for ghost in ghosts: ghost.state = "CHASE"

        player.update()
        player.move()
        for ghost in ghosts: ghost.move()

        for pellet in pellets[:]:
            if player.rect.colliderect(pellet.rect):
                pellets.remove(pellet)
                if pellet.is_power:
                    score += 50
                    frightened_mode_timer = FRIGHTENED_DURATION
                    for ghost in ghosts: ghost.state = "FRIGHTENED"
                else: score += 10
        
        for ghost in ghosts:
            if player.rect.colliderect(ghost.rect):
                if ghost.state == "FRIGHTENED":
                    score += 200
                    ghost.reset()
                else:
                    game_state = "GAME_OVER"
                    break
        
        if not pellets: game_state = "WIN"
        draw_game_elements()

    elif game_state in ["GAME_OVER", "WIN"]:
        draw_game_elements() # Draw the final game state behind the message
        draw_end_screen("GAME OVER" if game_state == "GAME_OVER" else "승리하셨습니다!")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
