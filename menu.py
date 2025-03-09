import pygame
import json
import os

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
LEVEL_BUTTON_COLOR, LEVEL_BUTTON_HOVER_COLOR = (100, 100, 100), (130, 130, 130)  # Gray colors for level button
TABLE_COLOR = (0, 0, 0)

# Initialize fonts
font = small_font = large_font = screen = None

# High Score File
HIGH_SCORE_FILE = "highscores.json"

# Game level settings
LEVEL_OPTIONS = [1, 5, 10, 15, 20, 25]  # Start at level 1
current_level_index = 0  # Start with the first level option (level 1)

def load_high_scores():
    """Load score from json file"""
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            return json.load(file)
    return [0] * 5  # If file doesn't exist, return 5 zeros

def create_screen():
    """Create and return the game window"""
    global screen, font, small_font, large_font
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    font = pygame.font.SysFont("couriernew", 24)
    small_font = pygame.font.SysFont("couriernew", 28)  # 使用等宽字体，调整为 28 以避免过大
    large_font = pygame.font.SysFont("couriernew", 48)
    return screen

def draw_start_menu(screen):
    """Draw start menu and high scores"""
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
        # 创建彩色字母
        color_letter = title_font.render(letters[i], True, colors[i])
        
        # 添加简单的阴影效果增强可读性
        shadow_letter = title_font.render(letters[i], True, (50, 50, 50))
        screen.blit(shadow_letter, (current_x + 3, title_y + 3))
        
        # 绘制彩色字母
        screen.blit(color_letter, (current_x, title_y))
        current_x += letter_surface.get_width()

    # 获取鼠标位置
    mouse_pos = pygame.mouse.get_pos()

    # Play 按钮
    button_width, button_height = 200, 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = 250
    play_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # 根据鼠标位置改变按钮颜色
    button_color = BUTTON_HOVER_COLOR if play_rect.collidepoint(mouse_pos) else BUTTON_COLOR

    pygame.draw.rect(screen, button_color, play_rect)
    pygame.draw.rect(screen, WHITE, play_rect, 2)

    # 按钮文字
    play_text = font.render("PLAY", True, WHITE)
    screen.blit(play_text, (button_x + button_width // 2 - play_text.get_width() // 2, 
                            button_y + button_height // 2 - play_text.get_height() // 2))

    # Level 按钮 - 添加在Play按钮下方
    level_button_width, level_button_height = 200, 40
    level_button_x = SCREEN_WIDTH // 2 - level_button_width // 2
    level_button_y = button_y + button_height + 15  # 在Play按钮下方留一些间距
    level_rect = pygame.Rect(level_button_x, level_button_y, level_button_width, level_button_height)

    # 根据鼠标位置改变按钮颜色
    level_button_color = LEVEL_BUTTON_HOVER_COLOR if level_rect.collidepoint(mouse_pos) else LEVEL_BUTTON_COLOR

    pygame.draw.rect(screen, level_button_color, level_rect)
    pygame.draw.rect(screen, WHITE, level_rect, 2)

    # 当前级别显示
    current_level = LEVEL_OPTIONS[current_level_index]
    level_text = font.render(f"LEVEL: {current_level}", True, WHITE)
    screen.blit(level_text, (level_button_x + level_button_width // 2 - level_text.get_width() // 2, 
                            level_button_y + level_button_height // 2 - level_text.get_height() // 2))

    # 高分榜标题 - 位置调整以适应新按钮
    high_score_text = small_font.render("HIGH SCORES", True, WHITE)
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, level_button_y + level_button_height + 30))

    # 加载高分榜
    high_scores = load_high_scores()
    
    # 确定最大分数宽度以动态调整列
    max_score_width = max([small_font.render(str(score).zfill(4), True, WHITE).get_width() for score in high_scores] or [small_font.render("0000", True, WHITE).get_width()])
    table_width = 250  # 增加表格宽度以容纳分数
    rank_width = 50  # 固定 RANK 列宽度
    score_x = table_width - max_score_width - 30  # SCORE 列右对齐，增加边距到 30 像素
    
    # 创建高分榜表格 - 位置调整
    table_height = 30
    table_x = SCREEN_WIDTH // 2 - table_width // 2
    table_y = level_button_y + level_button_height + 60
    
    # 表头
    rank_text = small_font.render("RANK", True, WHITE)
    score_text = small_font.render("SCORE", True, WHITE)
    
    # 绘制表头背景
    header_rect = pygame.Rect(table_x, table_y, table_width, table_height)
    pygame.draw.rect(screen, TABLE_COLOR, header_rect)
    pygame.draw.rect(screen, WHITE, header_rect, 1)
    
    # 绘制表头文字
    screen.blit(rank_text, (table_x + 10, table_y + table_height//2 - rank_text.get_height()//2))  # 左对齐 RANK
    screen.blit(score_text, (table_x + score_x, table_y + table_height//2 - score_text.get_height()//2))  # 右对齐 SCORE
    
    # 绘制表格行
    for i, score in enumerate(high_scores):
        row_y = table_y + (i + 1) * table_height
        row_rect = pygame.Rect(table_x, row_y, table_width, table_height)
        
        # 交替行颜色
        row_color = (30, 30, 50) if i % 2 == 0 else (20, 20, 40)
        pygame.draw.rect(screen, row_color, row_rect)
        pygame.draw.rect(screen, WHITE, row_rect, 1)
        
        # 排名和分数
        rank_num = small_font.render(f"{i + 1}.", True, WHITE)
        score_num = small_font.render(str(score).zfill(4), True, WHITE)  # 格式化为 4 位数
        
        # 对齐 RANK 和 SCORE
        screen.blit(rank_num, (table_x + 10, row_y + table_height//2 - rank_num.get_height()//2))  # 左对齐 RANK
        screen.blit(score_num, (table_x + score_x, row_y + table_height//2 - score_num.get_height()//2))  # 右对齐 SCORE

    return play_rect, level_rect  # Return both button rectangles

def handle_level_button_click():
    """Handle level button click by cycling through level options"""
    global current_level_index
    current_level_index = (current_level_index + 1) % len(LEVEL_OPTIONS)
    return LEVEL_OPTIONS[current_level_index]

def draw_game_over(screen, score):
    """Draw the game over screen with restart button"""
    # Create overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Game over text and score
    game_over_text = large_font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 3 + 60))
    
    # Restart button
    button_width, button_height = 200, 50
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = SCREEN_HEIGHT // 2 + 50
    
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    
    button_text = font.render("RESTART", True, WHITE)
    screen.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2, 
                            button_y + button_height // 2 - button_text.get_height() // 2))
    
    return button_rect  # Return the button rectangle