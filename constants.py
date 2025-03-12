'''constants.py - Constants for the game.'''
# Game & Screen Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = 200 + GRID_WIDTH * BLOCK_SIZE + 200
SCREEN_HEIGHT = 600
GRID_START_X = 200

# Colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
TRANSPARENT = (128, 128, 128, 80)
BACKGROUND_COLOR = (10, 10, 25)
BUTTON_COLOR = (60, 159, 40)
BUTTON_HOVER_COLOR = (80, 200, 60)
LEVEL_BUTTON_COLOR = (100, 100, 100)
LEVEL_BUTTON_HOVER_COLOR = (130, 130, 130)
TABLE_COLOR = (0, 0, 0)

# Colors & Shapes for Tetrominos
# I, L, J, O, S, Z, T
COLORS = [
    (0, 255, 255),   # I - Cyan
    (255, 165, 0),   # L - Orange
    (0, 0, 255),     # J - Blue
    (255, 255, 0),   # O - Yellow
    (0, 255, 0),     # S - Green
    (255, 0, 0),     # Z - Red
    (255, 0, 255)    # T - Purple
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

# Game logic constants
DAS_DELAY = 380
ARR_DELAY = 70
MOVE_REPEAT_DELAY = 15
LOCK_DELAY = 500
MAX_LOCK_RESETS = 15
BASE_FALL_SPEED = 1000
SOFT_DROP_SPEED = 50
LINES_PER_LEVEL = 10

# Scoring constants
SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
COMBO_BONUS = [0, 150, 200, 300, 400, 400]
BACK_TO_BACK_BONUS = 1.5
ALL_CLEAR_BONUS = 2000

# Highscore files
HIGH_SCORE_FILE = "highscores.json"
MAX_SCORES = 5

# Level options
LEVEL_OPTIONS = [1, 5, 10, 15, 20, 25]