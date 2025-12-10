import pygame
import sys
import random

# --- 초기화 ---
pygame.init()

# --- 화면 설정 ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("점프킹")

# --- 시계 설정 ---
clock = pygame.time.Clock()
FPS = 60

# --- 색상 및 폰트 정의 ---
BACKGROUND_COLOR = (44, 62, 80)
PLAYER_COLOR = (241, 196, 15)
PLAYER_JUMP_COLOR = (243, 156, 18) # 점프 시 색상
PLATFORM_COLOR = (46, 204, 113)
TEXT_COLOR = (236, 240, 241)
TITLE_FONT = pygame.font.SysFont("Malgun Gothic", 64)
font = pygame.font.SysFont("Malgun Gothic", 48)
small_font = pygame.font.SysFont("Malgun Gothic", 36)

# --- 게임 설정 ---
GRAVITY = 0.6
JUMP_STRENGTH = -15
PLAYER_HORIZONTAL_SPEED = 6
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20

# --- 게임 변수 ---
game_state = 'start'
score = 0
player_x, player_y, player_vy = 0, 0, 0
jump_effect_timer = 0
platforms = []

def reset_game():
    """게임을 초기 상태로 리셋합니다."""
    global player_x, player_y, player_vy, platforms, score
    
    platforms.clear()
    for i in range(10):
        x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
        y = SCREEN_HEIGHT - 100 - i * 85
        new_platform = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        platforms.append(new_platform)

    player_x = platforms[-1].centerx
    player_y = platforms[-1].top - 15
    player_vy = 0
    score = 0

# --- 초기 설정 ---
reset_game()

# --- 게임 루프 ---
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == 'start':
            if event.type == pygame.MOUSEBUTTONDOWN:
                reset_game()
                game_state = 'playing'
        elif game_state == 'playing':
            if event.type == pygame.MOUSEBUTTONDOWN:
                player_vy = JUMP_STRENGTH
                jump_effect_timer = 10 # 점프 효과 타이머
        elif game_state == 'game_over':
            if event.type == pygame.MOUSEBUTTONDOWN:
                reset_game()
                game_state = 'playing'
        
    screen.fill(BACKGROUND_COLOR)

    if game_state == 'start':
        title_text = TITLE_FONT.render("점프킹", True, TEXT_COLOR)
        start_text = small_font.render("마우스 버튼을 눌러 시작", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))

    elif game_state == 'playing':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player_x -= PLAYER_HORIZONTAL_SPEED
        if keys[pygame.K_RIGHT]: player_x += PLAYER_HORIZONTAL_SPEED

        if player_x < 15: player_x = 15
        if player_x > SCREEN_WIDTH - 15: player_x = SCREEN_WIDTH - 15

        scroll_speed = 0
        if player_y < SCREEN_HEIGHT / 2 and player_vy < 0:
            scroll_speed = -player_vy
            player_y += scroll_speed
            score += int(scroll_speed)

        player_vy += GRAVITY
        player_y += player_vy

        if scroll_speed > 0:
            for plat in platforms: plat.y += scroll_speed

        player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)

        if player_vy > 0:
            for plat in platforms:
                if player_rect.colliderect(plat) and abs(player_rect.bottom - plat.top) < player_vy + 1:
                    player_vy = JUMP_STRENGTH
                    player_y = plat.top - 15
                    jump_effect_timer = 10
        
        platforms[:] = [p for p in platforms if p.top <= SCREEN_HEIGHT]
        while len(platforms) < 10:
            last_plat_y = min(p.top for p in platforms)
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = last_plat_y - random.randint(80, 120)
            platforms.append(pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

        if player_y > SCREEN_HEIGHT:
            game_state = 'game_over'

        for plat in platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, plat, border_radius=10)
        
        current_player_color = PLAYER_COLOR
        if jump_effect_timer > 0:
            current_player_color = PLAYER_JUMP_COLOR
            jump_effect_timer -= 1
        pygame.draw.circle(screen, current_player_color, (int(player_x), int(player_y)), 15)
        
        score_text = small_font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

    elif game_state == 'game_over':
        over_text = font.render("게임 오버", True, TEXT_COLOR)
        score_text = small_font.render(f"최종 점수: {score}", True, TEXT_COLOR)
        restart_text = small_font.render("마우스 버튼을 눌러 재시작", True, TEXT_COLOR)

        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
