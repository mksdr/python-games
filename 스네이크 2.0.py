import pygame
import sys
import random
import os

# --- 상수 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# --- 색상 (현대적인 느낌의 색상 팔레트) ---
COLOR_BACKGROUND = (20, 20, 20)
COLOR_SNAKE = (57, 255, 20) # 밝은 녹색
COLOR_SNAKE_HEAD = (124, 252, 0) # 더 밝은 녹색
COLOR_FOOD = (255, 7, 58) # 밝은 빨강/분홍
COLOR_TEXT = (230, 230, 230) # 밝은 회색
COLOR_GRID = (30, 30, 30) # 어두운 회색
COLOR_OVERLAY = (0, 0, 0, 170) # 반투명 검정

# --- 방향 ---
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- 게임 상태 ---
START = 0
PLAYING = 1
GAME_OVER = 2

# --- Pygame 초기화 ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("스네이크 게임")
clock = pygame.time.Clock()

# --- 폰트 로드 ---
# 한글을 지원하는 시스템 폰트를 찾습니다.
def get_korean_font():
    # Windows
    if sys.platform == "win32":
        for font in ["malgun.ttf", "gulim.ttc"]:
            path = os.path.join(os.environ.get("SystemRoot", "C:/Windows"), "Fonts", font)
            if os.path.exists(path):
                return path
    # macOS
    elif sys.platform == "darwin":
        for font in ["AppleGothic.dfont", "/System/Library/Fonts/Supplemental/AppleGothic.ttf"]:
             if os.path.exists(font):
                return font
    # Linux (나눔고딕이 설치되어 있다고 가정)
    for font in ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "NanumGothic.ttf"]:
        if os.path.exists(font):
            return font
    return None # 적절한 폰트를 찾지 못한 경우

korean_font_path = get_korean_font()

try:
    # 폰트를 찾았으면 해당 폰트를 사용, .ttc(글꼴 모음)의 경우 인덱스 지정
    if korean_font_path and korean_font_path.lower().endswith('.ttc'):
        font_small = pygame.font.Font(korean_font_path, 24, index=0)
        font_large = pygame.font.Font(korean_font_path, 72, index=0)
    else:
        font_small = pygame.font.Font(korean_font_path, 24)
        font_large = pygame.font.Font(korean_font_path, 72)

    # 폰트 로드 실패 시 pygame 기본 폰트 사용
    if font_small is None or font_large is None:
        raise FileNotFoundError

except (FileNotFoundError, pygame.error):
    print("경고: 한글 폰트를 찾을 수 없습니다. 기본 폰트로 대체합니다. (글자가 깨질 수 있습니다)")
    font_small = pygame.font.Font(None, 30)
    font_large = pygame.font.Font(None, 80)


# --- 클래스 정의 ---

class Snake:
    """뱀의 로직을 관리하는 클래스"""
    def __init__(self):
        self.reset()

    def reset(self):
        """뱀을 초기 상태로 리셋합니다."""
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False

    def move(self):
        """뱀을 현재 방향으로 한 칸 이동시킵니다."""
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # 화면 경계를 벗어났는지 확인
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return False # 게임 오버

        # 머리가 몸통의 다른 부분과 충돌했는지 확인합니다.
        if len(self.body) > 1 and new_head in self.body[1:]:
            return False # 게임 오버

        self.body.insert(0, new_head)

        if self.grow:
            self.grow = False
        else:
            self.body.pop()
        
        return True

    def change_direction(self, new_direction):
        """뱀의 이동 방향을 변경합니다. 단, 반대 방향으로는 즉시 변경할 수 없습니다."""
        if len(self.body) > 1 and (self.direction[0] * -1, self.direction[1] * -1) == new_direction:
            return
        self.direction = new_direction

    def grow_snake(self):
        """뱀의 몸을 한 칸 늘립니다."""
        self.grow = True

    def draw(self, surface):
        """뱀을 화면에 그립니다. 머리는 다른 색으로 표시합니다."""
        for i, segment in enumerate(self.body):
            x, y = segment
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, COLOR_BACKGROUND, rect, 1) # 세그먼트 테두리

class Food:
    """음식의 로직을 관리하는 클래스"""
    def __init__(self, snake_body):
        self.position = (0, 0)
        self.randomize_position(snake_body)

    def randomize_position(self, snake_body):
        """음식의 위치를 뱀의 몸과 겹치지 않는 무작위 위치로 변경합니다."""
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_body:
                break

    def draw(self, surface):
        """음식을 화면에 그립니다."""
        x, y = self.position
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, COLOR_FOOD, rect)
        pygame.draw.rect(surface, COLOR_BACKGROUND, rect, 1) # 테두리

# --- 그리기 함수 ---

def draw_grid(surface):
    """게임 배경에 그리드를 그립니다."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

def draw_score(surface, score):
    """화면 상단에 현재 점수를 표시합니다."""
    score_text = f"Score: {score}"
    text_surface = font_small.render(score_text, True, COLOR_TEXT)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, 25))
    surface.blit(text_surface, text_rect)

def draw_text_overlay(surface, title, subtitle):
    """화면 중앙에 반투명 오버레이와 함께 텍스트를 표시합니다."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(COLOR_OVERLAY)
    surface.blit(overlay, (0, 0))

    title_surf = font_large.render(title, True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
    surface.blit(title_surf, title_rect)

    subtitle_surf = font_small.render(subtitle, True, COLOR_TEXT)
    subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
    surface.blit(subtitle_surf, subtitle_rect)

# --- 메인 게임 로직 ---

def game_loop():
    """메인 게임 루프. 게임의 상태를 관리하고 화면을 업데이트합니다."""
    game_state = START
    snake = Snake()
    food = Food(snake.body)
    score = 0
    game_speed = 10

    while True:
        # --- 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 게임 상태에 따른 키 입력 처리
            if game_state == START:
                if event.type == pygame.KEYDOWN:
                    game_state = PLAYING
            elif game_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN: snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT: snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT: snake.change_direction(RIGHT)
            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_loop() # 게임 재시작
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

        # --- 화면 그리기 ---
        screen.fill(COLOR_BACKGROUND)
        
        if game_state == START:
            draw_text_overlay(screen, "스네이크 게임", "아무 키나 눌러 시작하세요")
        
        elif game_state == PLAYING:
            draw_grid(screen)
            
            if not snake.move():
                game_state = GAME_OVER

            if snake.body[0] == food.position:
                snake.grow_snake()
                food.randomize_position(snake.body)
                score += 1
                if game_speed < 30: game_speed += 0.5

            snake.draw(screen)
            food.draw(screen)
            draw_score(screen, score)

        elif game_state == GAME_OVER:
            # 게임 오버 시 마지막 게임 화면을 보여줍니다.
            draw_grid(screen)
            snake.draw(screen)
            food.draw(screen)
            draw_score(screen, score)
            draw_text_overlay(screen, "게임 종료", f"점수: {score} | 'R' 키를 눌러 재시작, 'Q' 키를 눌러 종료")

        # --- 화면 업데이트 ---
        pygame.display.flip()
        clock.tick(game_speed)

if __name__ == "__main__":
    game_loop()
