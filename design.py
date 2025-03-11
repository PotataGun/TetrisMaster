# design.py - Optimized
import pygame
import gameplay

# Game Constants
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 200 + GRID_WIDTH * BLOCK_SIZE + 200
GRID_START_X = 200

# Colors
WHITE, GRAY, BLACK = (255, 255, 255), (128, 128, 128), (0, 0, 0)
TRANSPARENT = (128, 128, 128, 80)
BACKGROUND_COLOR = (10, 10, 25)
BUTTON_COLOR, BUTTON_HOVER_COLOR = (50, 100, 200), (70, 140, 255)

# Tetromino colors and shapes
COLORS = [
    (0, 255, 255), (255, 165, 0), (0, 0, 255), (255, 255, 0),
    (0, 255, 0), (255, 0, 0), (255, 0, 255)
]

SHAPES = [
    [[1, 1, 1, 1]],                    # I
    [[1, 0, 0], [1, 1, 1]],            # L
    [[0, 0, 1], [1, 1, 1]],            # J
    [[1, 1], [1, 1]],                  # O
    [[0, 1, 1], [1, 1, 0]],            # S
    [[1, 1, 0], [0, 1, 1]],            # Z
    [[0, 1, 0], [1, 1, 1]]             # T
]

# Initialize fonts
pygame.font.init()
font = pygame.font.SysFont("couriernew", 24)
small_font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont("couriernew", 36)

def draw_grid(screen, grid):
    """Draw the game grid"""
    grid_bg = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), pygame.SRCALPHA)
    grid_bg.fill((128, 128, 128, 100))
    screen.blit(grid_bg, (GRID_START_X, 0))
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != TRANSPARENT:
                pygame.draw.rect(screen, grid[y][x], 
                    (GRID_START_X + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pygame.draw.rect(screen, GRAY, 
                (GRID_START_X + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_block(screen, block):
    """Draw the current active block"""
    if not block: return
    shape = block.get_shape()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                rect = (GRID_START_X + (block.x + x) * BLOCK_SIZE, 
                       (block.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, block.color, rect, 0)
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_ghost_piece(screen, ghost_block):
    """Draw the ghost piece (landing preview)"""
    if not ghost_block: return
    shape = ghost_block.get_shape()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(GRID_START_X + (ghost_block.x + x) * BLOCK_SIZE, 
                                 (ghost_block.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, ghost_block.color, rect, 1)

def draw_preview(screen, blocks, title, x, y, width, height, block_size=BLOCK_SIZE//1.5):
    """Draw a preview area (used for next blocks and held piece)"""
    small_font = pygame.font.SysFont(None, 30)
    text = small_font.render(title, True, WHITE)
    screen.blit(text, (x, y - 30))
    
    bg = pygame.Surface((width, height), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 100))
    screen.blit(bg, (x - 10, y - 10))
    
    # Draw border
    pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(x - 10, y - 10, width, height), 2)
    
    # Draw blocks if provided
    if not blocks: return
    blocks = [blocks] if not isinstance(blocks, list) else blocks
    
    for i, block in enumerate(blocks):
        if not block: continue
        shape = block.get_shape()
        shape_width = len(shape[0]) * block_size
        shape_height = len(shape) * block_size
        offset_x = x + (4 * block_size - shape_width) // 2
        offset_y = y + i * 80 + (4 * block_size - shape_height) // 2
        
        for y_pos, row in enumerate(shape):
            for x_pos, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(offset_x + x_pos * block_size, offset_y + y_pos * block_size, 
                                      block_size, block_size)
                    pygame.draw.rect(screen, block.color, rect, 0)
                    pygame.draw.rect(screen, WHITE, rect, 1)

def draw_next_blocks(screen, next_blocks):
    """Draw the next blocks preview"""
    preview_x = GRID_START_X + GRID_WIDTH * BLOCK_SIZE + 30
    draw_preview(screen, next_blocks, "NEXT", preview_x, 50, 6 * BLOCK_SIZE, 260)

def draw_held_piece(screen, held_piece):
    """Draw the held piece"""
    hold_x = 30
    draw_preview(screen, held_piece, "HOLD", hold_x, 50, 5 * BLOCK_SIZE * 0.8, 5 * BLOCK_SIZE * 0.8, BLOCK_SIZE * 0.8)

def draw_score_animation(screen, font, x, y):
    """Draw score animation when lines are cleared"""
    font = pygame.font.SysFont("couriernew", 24)
    
    # Display animations
    animations = [
        (gameplay.score_animation, (255, 255, 0), (x + 50, y - 30)),
        (gameplay.clear_message, (255, 255, 255), (0, 0)),  # 临时占位，稍后计算
        (gameplay.combo_animation, (255, 50, 50), (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 3 + 40))
    ]
    
    for anim, color, pos in animations:
        if anim and (gameplay.score_timer > 0 or gameplay.combo_timer > 0):
            text = font.render(anim, True, color)
            if anim == gameplay.clear_message:  # 仅对 clear_message 动态居中
                pos = (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 3)  # 水平居中
            screen.blit(text, pos)
    
    # Update timers
    if gameplay.score_timer > 0:
        gameplay.score_timer -= 1
    else:
        gameplay.score_animation = gameplay.clear_message = None
        
    if gameplay.combo_timer > 0:
        gameplay.combo_timer -= 1
    else:
        gameplay.combo_animation = None

def draw_score(screen, score, combo_count):
    """Draw the score display"""
    score_x = GRID_START_X + GRID_WIDTH * BLOCK_SIZE + 30
    score_y = 350
    
    # Background
    score_bg = pygame.Surface((160, 80), pygame.SRCALPHA)
    score_bg.fill((0, 0, 0, 100))
    screen.blit(score_bg, (score_x - 5, score_y - 5))
    
    # Score text
    font = pygame.font.SysFont("couriernew", 24)
    score_label = font.render("SCORE:", True, WHITE)
    screen.blit(score_label, (score_x, score_y))
    score_text = font.render(str(score), True, WHITE)
    screen.blit(score_text, (score_x + score_label.get_width() + 10, score_y))
    
    # Combo display
    if combo_count > 0:
        combo_text = font.render(f"COMBO: {combo_count}x", True, (255, 165, 0))
        screen.blit(combo_text, (score_x, score_y + 40))

def draw_game_level(screen, current_level):
    """Draw the game level display"""
    level_x = GRID_START_X + GRID_WIDTH * BLOCK_SIZE + 30
    level_y = 480  # Position below the score display
    
    # Background
    level_bg = pygame.Surface((160, 40), pygame.SRCALPHA)
    level_bg.fill((0, 0, 0, 100))
    screen.blit(level_bg, (level_x - 5, level_y - 5))
    
    # Level text
    font = pygame.font.SysFont("couriernew", 24)
    level_text = font.render(f"LEVEL: {current_level}", True, WHITE)
    screen.blit(level_text, (level_x, level_y))

def draw_lines_cleared(screen, lines_cleared):
    """Draw the lines cleared display with consistent style"""
    level_x = GRID_START_X + GRID_WIDTH * BLOCK_SIZE + 30
    level_y = 480  # Match with draw_game_level's y position
    
    # Background
    lines_bg = pygame.Surface((160, 40), pygame.SRCALPHA)  # Same size as Level background
    lines_bg.fill((0, 0, 0, 100))
    screen.blit(lines_bg, (level_x - 5, level_y + 40 - 5))  # Position below Level
    
    # Lines cleared text
    font = pygame.font.SysFont("couriernew", 24)  # Use the same font as Score and Level
    lines_text = font.render(f"Lines: {lines_cleared}", True, WHITE)
    screen.blit(lines_text, (level_x, level_y + 40))  # Center text within the background