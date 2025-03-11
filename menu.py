import pygame
import gameplay

# Game Constants
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 200 + GRID_WIDTH * BLOCK_SIZE + 200
GRID_START_X = 200

# Colors
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
BACKGROUND_COLOR = (10, 10, 25)
BUTTON_COLOR, BUTTON_HOVER_COLOR = (60, 159, 40), (80, 200, 60)
LEVEL_BUTTON_COLOR, LEVEL_BUTTON_HOVER_COLOR = (100, 100, 100), (130, 130, 130)
TABLE_COLOR = (0, 0, 0)

# Initialize fonts
font = small_font = large_font = screen = None

# Game level settings
LEVEL_OPTIONS = [1, 5, 10, 15, 20, 25]
current_level_index = 0

def create_screen():
    """Create and return the game window"""
    global screen, font, small_font, large_font
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    font = pygame.font.SysFont("couriernew", 24)
    small_font = pygame.font.SysFont("couriernew", 24, bold=True)
    large_font = pygame.font.SysFont("couriernew", 48)
    return screen

def get_rainbow_color(time):
    """Generate rainbow color based on time"""
    colors = [
        (255, 0, 0),    # Red
        (255, 165, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 100, 255),  # Blue
        (138, 43, 226)  # Purple
    ]
    index = int((time % 1200) / 200) % len(colors)
    return colors[index]

def draw_start_menu(screen):
    """Draw start menu and high scores with names"""
    global current_level_index
    screen.fill(BACKGROUND_COLOR)

    # Tetris title
    title_font = pygame.font.SysFont(None, 72, bold=True)
    
    # Tetris title letters and colors
    letters = "TETRIS"
    colors = [
        (255, 0, 0),    # T - Red
        (255, 165, 0),  # E - Orange
        (255, 255, 0),  # T - Yellow
        (0, 255, 0),    # R - Green
        (0, 100, 255),  # I - Blue
        (138, 43, 226)  # S - Purple
    ]
    
    # 计算总宽度以便居中显示
    total_width = 0
    letter_surfaces = []
    
    for letter in letters:
        letter_surface = title_font.render(letter, True, WHITE)
        letter_surfaces.append(letter_surface)
        total_width += letter_surface.get_width()
    
    # 起始X坐标（居中）
    current_x = SCREEN_WIDTH // 2 - total_width // 2
    title_y = 100
    
    # 渲染每个彩色字母
    for i, letter_surface in enumerate(letter_surfaces):
        color_letter = title_font.render(letters[i], True, colors[i])
        shadow_letter = title_font.render(letters[i], True, (50, 50, 50))
        screen.blit(shadow_letter, (current_x + 3, title_y + 3))
        screen.blit(color_letter, (current_x, title_y))
        current_x += letter_surface.get_width()

    # 获取鼠标位置
    mouse_pos = pygame.mouse.get_pos()

    # Play 按钮
    button_width, button_height = 200, 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = 250
    play_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_color = BUTTON_HOVER_COLOR if play_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, play_rect)
    pygame.draw.rect(screen, WHITE, play_rect, 2)
    play_text = font.render("PLAY", True, WHITE)
    screen.blit(play_text, (button_x + button_width // 2 - play_text.get_width() // 2, 
                            button_y + button_height // 2 - play_text.get_height() // 2))

    # Level 按钮
    level_button_width, level_button_height = 200, 40
    level_button_x = SCREEN_WIDTH // 2 - level_button_width // 2
    level_button_y = button_y + button_height + 15
    level_rect = pygame.Rect(level_button_x, level_button_y, level_button_width, level_button_height)
    level_button_color = LEVEL_BUTTON_HOVER_COLOR if level_rect.collidepoint(mouse_pos) else LEVEL_BUTTON_COLOR
    pygame.draw.rect(screen, level_button_color, level_rect)
    pygame.draw.rect(screen, WHITE, level_rect, 2)
    current_level = LEVEL_OPTIONS[current_level_index]
    level_text = font.render(f"LEVEL: {current_level}", True, WHITE)
    screen.blit(level_text, (level_button_x + level_button_width // 2 - level_text.get_width() // 2, 
                            level_button_y + level_button_height // 2 - level_text.get_height() // 2))

    # 高分榜标题
    high_score_text = small_font.render("HIGH SCORES", True, WHITE)
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, level_button_y + level_button_height + 30))

    # 加载高分榜
    high_scores = gameplay.load_high_scores()
    
    # 确定最大宽度以动态调整列
    max_rank_width = max([small_font.render(f"{i + 1}.", True, WHITE).get_width() for i in range(len(high_scores))] or [small_font.render("5.", True, WHITE).get_width()])
    max_name_width = max([small_font.render(entry["name"], True, WHITE).get_width() for entry in high_scores] or [small_font.render("AAA", True, WHITE).get_width()])
    max_score_width = max([small_font.render(f"{entry['score']:,}", True, WHITE).get_width() for entry in high_scores] or [small_font.render("0,000", True, WHITE).get_width()])
    
    RANK_WIDTH = max(60, max_rank_width + 15)
    NAME_WIDTH = max(120, max_name_width + 20)
    SCORE_WIDTH = max(100, max_score_width + 20)
    table_width = RANK_WIDTH + NAME_WIDTH + SCORE_WIDTH
    table_x = SCREEN_WIDTH // 2 - table_width // 2
    name_x = table_x + RANK_WIDTH
    score_x = table_x + RANK_WIDTH + NAME_WIDTH
    
    table_height = 30
    table_y = level_button_y + level_button_height + 60
    
    # 表头
    header_rect = pygame.Rect(table_x, table_y, table_width, table_height)
    pygame.draw.rect(screen, TABLE_COLOR, header_rect)
    pygame.draw.rect(screen, WHITE, header_rect, 1)
    screen.blit(small_font.render("RANK", True, WHITE), (table_x + (RANK_WIDTH - small_font.render("RANK", True, WHITE).get_width()) // 2, table_y + table_height//2 - small_font.get_height()//2))
    screen.blit(small_font.render("NAME", True, WHITE), (name_x + (NAME_WIDTH - small_font.render("NAME", True, WHITE).get_width()) // 2, table_y + table_height//2 - small_font.get_height()//2))
    screen.blit(small_font.render("SCORE", True, WHITE), (score_x + (SCORE_WIDTH - small_font.render("SCORE", True, WHITE).get_width()) // 2, table_y + table_height//2 - small_font.get_height()//2))
    
    # 表格行
    for i, entry in enumerate(high_scores[:gameplay.MAX_SCORES]):
        row_y = table_y + (i + 1) * table_height
        row_rect = pygame.Rect(table_x, row_y, table_width, table_height)
        row_color = (30, 30, 50) if i % 2 == 0 else (20, 20, 40)
        pygame.draw.rect(screen, row_color, row_rect)
        pygame.draw.rect(screen, WHITE, row_rect, 1)
        rank_num = small_font.render(f"{i + 1}.", True, WHITE)
        name_num = small_font.render(entry["name"], True, WHITE)
        score_num = small_font.render(f"{entry['score']:,}", True, WHITE)
        screen.blit(rank_num, (table_x + (RANK_WIDTH - rank_num.get_width()) // 2, row_y + table_height//2 - rank_num.get_height()//2))
        screen.blit(name_num, (name_x + (NAME_WIDTH - name_num.get_width()) // 2, row_y + table_height//2 - name_num.get_height()//2))
        screen.blit(score_num, (score_x + (SCORE_WIDTH - score_num.get_width()) // 2, row_y + table_height//2 - score_num.get_height()//2))

    return play_rect, level_rect

def handle_level_button_click():
    """Handle level button click by cycling through level options"""
    global current_level_index
    current_level_index = (current_level_index + 1) % len(LEVEL_OPTIONS)
    return LEVEL_OPTIONS[current_level_index]

def draw_game_over(screen, score, new_high_score, input_active, input_text, flash_start_time):
    """Draw the game over screen with high scores, input box, and rainbow flashing"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    game_over_text = large_font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3 - 50))
    
    final_score_text = font.render(f"Final Score: {score:,}", True, WHITE)
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 3 + 10))

    high_scores = gameplay.load_high_scores()
    high_score_title = small_font.render("HIGH SCORES", True, WHITE)
    screen.blit(high_score_title, (SCREEN_WIDTH // 2 - high_score_title.get_width() // 2, SCREEN_HEIGHT // 3 + 50))

    max_rank_width = max([small_font.render(f"{i + 1}.", True, WHITE).get_width() for i in range(len(high_scores))] or [small_font.render("5.", True, WHITE).get_width()])
    max_name_width = max([small_font.render(entry["name"], True, WHITE).get_width() for entry in high_scores] or [small_font.render("AAA", True, WHITE).get_width()])
    max_score_width = max([small_font.render(f"{entry['score']:,}", True, WHITE).get_width() for entry in high_scores] or [small_font.render("0,000", True, WHITE).get_width()])
    
    RANK_WIDTH = max(60, max_rank_width + 15)
    NAME_WIDTH = max(120, max_name_width + 20)
    SCORE_WIDTH = max(100, max_score_width + 20)
    table_width = RANK_WIDTH + NAME_WIDTH + SCORE_WIDTH
    table_x = SCREEN_WIDTH // 2 - table_width // 2
    name_x = table_x + RANK_WIDTH
    score_x = table_x + RANK_WIDTH + NAME_WIDTH
    
    table_y = SCREEN_HEIGHT // 3 + 80
    table_height = 30

    header_rect = pygame.Rect(table_x, table_y, table_width, table_height)
    pygame.draw.rect(screen, TABLE_COLOR, header_rect)
    pygame.draw.rect(screen, WHITE, header_rect, 1)
    screen.blit(small_font.render("RANK", True, WHITE), (table_x + (RANK_WIDTH - small_font.render("RANK", True, WHITE).get_width()) // 2, table_y + table_height//2 - small_font.get_height()//2))
    screen.blit(small_font.render("NAME", True, WHITE), (name_x + (NAME_WIDTH - small_font.render("NAME", True, WHITE).get_width()) // 2, table_y + table_height//2 - small_font.get_height()//2))
    screen.blit(small_font.render("SCORE", True, WHITE), (score_x + (SCORE_WIDTH - small_font.render("SCORE", True, WHITE).get_width()) // 2, table_y + table_height//2 - small_font.get_height()//2))

    current_time = pygame.time.get_ticks()
    for i, entry in enumerate(high_scores[:gameplay.MAX_SCORES]):
        row_y = table_y + (i + 1) * table_height
        row_rect = pygame.Rect(table_x, row_y, table_width, table_height)
        row_color = (30, 30, 50) if i % 2 == 0 else (20, 20, 40)
        pygame.draw.rect(screen, row_color, row_rect)
        pygame.draw.rect(screen, WHITE, row_rect, 1)
        
        rank_text = small_font.render(f"{i + 1}.", True, WHITE)
        text_color = get_rainbow_color(current_time) if (new_high_score and entry["score"] == score and not input_active and current_time - flash_start_time < 5000) else WHITE
        name_text = small_font.render(entry["name"], True, text_color)
        score_text = small_font.render(f"{entry['score']:,}", True, text_color)
        
        screen.blit(rank_text, (table_x + (RANK_WIDTH - rank_text.get_width()) // 2, row_y + table_height//2 - rank_text.get_height()//2))
        screen.blit(name_text, (name_x + (NAME_WIDTH - name_text.get_width()) // 2, row_y + table_height//2 - name_text.get_height()//2))
        screen.blit(score_text, (score_x + (SCORE_WIDTH - score_text.get_width()) // 2, row_y + table_height//2 - score_text.get_height()//2))

    if input_active:
        input_box_width = 300
        input_box_y = table_y + (min(len(high_scores), gameplay.MAX_SCORES) + 1) * table_height + 30
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - input_box_width // 2, input_box_y, input_box_width, 40)
        input_box_color = (100, 150, 200) if len(input_text) > 0 else BUTTON_COLOR
        pygame.draw.rect(screen, input_box_color, input_box)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        
        prompt_text = small_font.render("Enter your name (max 5 chars)", True, WHITE)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, input_box_y - 30))
        
        input_display = small_font.render(input_text, True, WHITE)
        screen.blit(input_display, (input_box.x + 10, input_box.y + input_box.h // 2 - input_display.get_height() // 2))
        
        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
        if cursor_visible:
            cursor_x = input_box.x + 10 + input_display.get_width()
            cursor_y = input_box.y + input_box.h // 2 - input_display.get_height() // 2
            pygame.draw.line(screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + input_display.get_height()), 2)

    button_width, button_height = 200, 50
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = SCREEN_HEIGHT - 60
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    button_text = font.render("RESTART", True, WHITE)
    screen.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2, 
                            button_y + button_height // 2 - button_text.get_height() // 2))

    return button_rect

def draw_countdown(screen, font, count):
    """绘制倒计时数字"""
    screen.fill(BACKGROUND_COLOR)  # 清除整个屏幕以避免重叠
    text = font.render(str(count), True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

def handle_game_over_input(events, input_text, score):
    """处理游戏结束时的输入，支持大小写字母，返回更新后的 input_text 和 input_active"""
    input_active = True
    for event in events:
        if event.type == pygame.QUIT:
            return False, input_text
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()  # 在事件内部获取最新按键状态
            shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            print(f"Key pressed: {event.key}, Shift: {shift_pressed}, Current input_text: '{input_text}'")
            if event.key in (pygame.K_LALT, pygame.K_RALT):
                continue
            if event.key == pygame.K_RETURN and input_text.strip():
                gameplay.end_game(score, input_text)
                input_active = False
            elif event.key == pygame.K_BACKSPACE and len(input_text) > 0:
                input_text = input_text[:-1]
            elif event.key in range(pygame.K_a, pygame.K_z + 1) and len(input_text) < 5:
                if shift_pressed:
                    input_text += chr(event.key - pygame.K_a + ord('A'))  # 大写
                else:
                    input_text += chr(event.key - pygame.K_a + ord('a'))  # 小写
            elif event.key in range(pygame.K_0, pygame.K_9 + 1) and len(input_text) < 5:
                input_text += chr(event.key - pygame.K_0 + ord('0'))
            elif event.key == pygame.K_SPACE and keys[pygame.K_SPACE] and len(input_text) < 5:
                input_text += " "
            elif event.key == pygame.K_MINUS and len(input_text) < 5:
                input_text += "-"
            elif len(input_text) >= 5:
                print("Input limit reached (5 characters max)")
    return input_active, input_text