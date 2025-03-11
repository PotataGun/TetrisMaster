# gameplay.py
import random
import json
import os
import design

# Animation variables
score_animation = combo_animation = clear_message = None
score_timer = combo_timer = 0

# Game state tracking
back_to_back = all_clear = False
current_bag = []

# Scoring system
SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
COMBO_BONUS = [0, 150, 200, 300, 400, 400]
BACK_TO_BACK_BONUS = 1.5
ALL_CLEAR_BONUS = 2000

# High score system
HIGH_SCORE_FILE = "highscores.json"
MAX_SCORES = 5

class Block:
    """Tetris block class"""
    def __init__(self, shape_index):
        self.shape_index = shape_index
        self.shape = design.SHAPES[shape_index]
        self.color = design.COLORS[shape_index]
        self.x = design.GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self, grid):
        """Rotate the block with SRS wall kicks"""
        original_shape = self.shape
        new_shape = [list(row) for row in zip(*self.shape[::-1])]
        original_x, original_y = self.x, self.y

        # Determine if it's an I piece
        is_i_piece = self.shape_index == 0
        kick_tests = [(-1, 0), (-1, 1), (0, -2), (-1, -2)] if not is_i_piece else [(-2, 0), (1, 0), (-2, -1), (1, 2)]

        if is_valid_move(self, grid, new_shape=new_shape):
            self.shape = new_shape
            return True
        else:
            # Try wall kicks
            for dx, dy in kick_tests:
                self.x = original_x + dx
                self.y = original_y + dy
                if is_valid_move(self, grid, new_shape=new_shape):
                    self.shape = new_shape
                    return True
                self.x, self.y = original_x, original_y
            self.shape = original_shape
            return False

    def get_shape(self):
        """Return current block shape"""
        return self.shape

def create_blocks_bag():
    """Create a new shuffled bag of all 7 tetromino types"""
    bag = list(range(len(design.SHAPES)))
    random.shuffle(bag)
    return bag

def create_block():
    """Create a new block using the 7-bag randomizer system"""
    global current_bag
    if not current_bag:
        current_bag = create_blocks_bag()
    shape_index = current_bag.pop(0)
    return Block(shape_index)

def is_valid_move(block, grid, dx=0, dy=0, new_shape=None):
    """Check if a move is valid with debug info and top overflow detection"""
    shape = new_shape if new_shape else block.get_shape()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x, new_y = block.x + x + dx, block.y + y + dy
                if (new_x < 0 or new_x >= design.GRID_WIDTH or 
                    new_y < 0 or new_y >= design.GRID_HEIGHT or
                    (new_y >= 0 and grid[new_y][new_x] != design.TRANSPARENT)):
                    return False
    return True

def place_block(block, grid):
    """Place block in the grid"""
    shape = block.get_shape()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[block.y + y][block.x + x] = block.color

def calculate_soft_drop_score(drop_distance):
    """Calculate points for soft drop"""
    return drop_distance

def calculate_hard_drop_score(current_y, landing_y):
    """Calculate points for hard drop"""
    return 2 * (landing_y - current_y)

def clear_lines(grid):
    """Clear completed lines and return score"""
    global score_animation, score_timer, clear_message
    lines_cleared = 0

    for y in range(design.GRID_HEIGHT):
        if all(cell != design.TRANSPARENT for cell in grid[y]):
            del grid[y]
            grid.insert(0, [design.TRANSPARENT for _ in range(design.GRID_WIDTH)])
            lines_cleared += 1

    messages = {1: "Single", 2: "Double", 3: "Triple", 4: "Tetris"}
    if lines_cleared > 0:
        score_animation = f"+{SCORES.get(lines_cleared, 0)}"
        clear_message = messages.get(lines_cleared, "")
        score_timer = 200

    return lines_cleared, SCORES.get(lines_cleared, 0)

def update_combo(combo_count, lines_cleared, grid):
    """Update combo count and calculate bonuses"""
    global combo_animation, combo_timer, back_to_back, all_clear, clear_message

    if lines_cleared == 0:
        return 0, 0  

    combo_count += 1
    total_bonus = 0

    if combo_count > 1:
        bonus_index = min(combo_count, len(COMBO_BONUS) - 1)
        combo_bonus = COMBO_BONUS[bonus_index]
        total_bonus += combo_bonus
        combo_animation = f"COMBO x{combo_count}! +{combo_bonus}"
        combo_timer = 200

    if lines_cleared == 4:
        if back_to_back:
            b2b_bonus = int(SCORES[4] * (BACK_TO_BACK_BONUS - 1))
            total_bonus += b2b_bonus
            clear_message = "BACK-TO-BACK TETRIS!"
        back_to_back = True
    else:
        back_to_back = False

    if all(all(cell == design.TRANSPARENT for cell in row) for row in grid):
        total_bonus += ALL_CLEAR_BONUS
        score_animation = f"+{ALL_CLEAR_BONUS}"
        score_timer = 300
        clear_message = "PERFECT CLEAR!"
        all_clear = True
    else:
        all_clear = False

    return combo_count, total_bonus

def get_ghost_piece(block, grid):
    """Create a ghost piece showing where the block will land"""
    if not block:
        return None

    ghost_block = Block(block.shape_index)
    ghost_block.shape = [row[:] for row in block.shape]
    ghost_block.x, ghost_block.y = block.x, block.y
    ghost_block.color = tuple(min(255, c + 50) for c in block.color)

    while is_valid_move(ghost_block, grid, dy=1):
        ghost_block.y += 1

    return ghost_block

def load_high_scores():
    """Load high scores from file with compatibility for old format"""
    if not os.path.exists(HIGH_SCORE_FILE):
        return []
    
    with open(HIGH_SCORE_FILE, "r") as file:
        try:
            data = json.load(file)
            if not data:
                return []
            if all(isinstance(item, (int, float)) for item in data):
                return [{"score": int(item), "name": "AAA", "date": "2025-03-09"} for item in data]
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def save_high_scores(high_scores):
    """Save high scores to file"""
    if not high_scores:
        high_scores = []
    
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            json.dump(high_scores, file, indent=4)
        print(f"Successfully saved high scores to {os.path.abspath(HIGH_SCORE_FILE)}")
    except Exception as e:
        print(f"Error saving high scores: {e}")


def update_high_scores(new_score, player_name=None):
    """Update high score list with name"""
    import datetime
    high_scores = load_high_scores()
    if not isinstance(new_score, int):
        return False

    # 如果没有提供名字，暂时不保存
    if player_name is None or player_name.strip() == "":
        return True

    if len(high_scores) < MAX_SCORES or new_score > min(high_scores, key=lambda x: x["score"], default={"score": 0})["score"]:
        entry = {
            "score": new_score,
            "name": player_name,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        high_scores.append(entry)
        high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)[:MAX_SCORES]
        save_high_scores(high_scores)
        return True
    return False

def reset_game(initial_level=1, keep_lines_cleared=False, current_lines_cleared=0):
    global current_bag
    current_bag = create_blocks_bag()
    current_block = create_block()
    next_blocks = [create_block() for _ in range(3)]
    hold_block = None
    hold_used = False
    grid = [[design.TRANSPARENT for _ in range(design.GRID_WIDTH)] for _ in range(design.GRID_HEIGHT)]
    score = combo_count = 0
    lines_cleared = current_lines_cleared if keep_lines_cleared else 0
    return current_block, next_blocks, hold_block, hold_used, grid, score, combo_count, lines_cleared, initial_level

def end_game(score, player_name=None):
    """Handle game over with optional player name"""
    if player_name and player_name.strip():
        update_high_scores(score, player_name)
    else:
        print("No valid player name provided, score not saved.")

def check_for_tspin(block, grid, last_action_was_rotation):
    """检查是否为T-Spin"""
    if block.shape_index != 6 or not last_action_was_rotation:
        return False
    
    center_x, center_y = block.x + 1, block.y + 1
    corners = [
        (center_x - 1, center_y - 1), (center_x + 1, center_y - 1),
        (center_x - 1, center_y + 1), (center_x + 1, center_y + 1)
    ]
    
    filled_corners = 0
    for x, y in corners:
        if (x < 0 or x >= len(grid[0]) or y >= len(grid) or
            (0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] != design.TRANSPARENT)):
            filled_corners += 1
    
    return filled_corners >= 3