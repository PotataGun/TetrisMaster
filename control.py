'''control.py - Handling user input for Tetronimos'''
import pygame
import gameplay
import design
from constants import *

class GameState:
    def __init__(self, current_level=1):
        """Represents the state of the Tetris game, including block positions, score, and game status."""
        self.current_block, self.next_blocks, self.hold_block, self.hold_used, self.grid, \
        self.score, self.combo_count, self.lines_cleared, _ = gameplay.reset_game(current_level)
        self.game_over = False
        self.running = True
        self.fall_time = 0
        self.fall_speed = 1000
        self.lock_time = 0
        self.has_landed = False
        self.lock_resets = 0
        self.max_lock_resets = MAX_LOCK_RESETS
        self.is_soft_dropping = False
        self.soft_drop_distance = 0
        self.das_left = InputTimer(DAS_DELAY, ARR_DELAY)
        self.das_right = InputTimer(DAS_DELAY, ARR_DELAY)
        self.last_movement_time = 0
        self.move_repeat_delay = MOVE_REPEAT_DELAY
        self.last_action_was_rotation = False

    def reset(self, keep_lines=False):
        self.current_block, self.next_blocks, self.hold_block, self.hold_used, self.grid, \
        self.score, self.combo_count, self.lines_cleared, _ = gameplay.reset_game(
            keep_lines_cleared=keep_lines, current_lines_cleared=0)
        self.game_over = False
        self.running = True
        self.fall_time = 0
        self.fall_speed = 1000
        self.lock_time = 0
        self.has_landed = False
        self.lock_resets = 0
        self.is_soft_dropping = False
        self.soft_drop_distance = 0
        self.last_action_was_rotation = False
        self.das_left = InputTimer(DAS_DELAY, ARR_DELAY)
        self.das_right = InputTimer(DAS_DELAY, ARR_DELAY)
        self.last_movement_time = 0

class InputTimer:
    def __init__(self, das_delay, arr_delay):
        self.das_delay = das_delay # Delayed Auto Shift
        self.arr_delay = arr_delay # Auto Repeat Rate
        self.last_time = 0 # Last time the key was pressed
        self.is_das_active = False # Whether DAS is currently active

    def update(self, current_time, key_pressed, initial_press):
        if key_pressed:
            if initial_press:
                self.last_time = current_time
                return True
            if not self.is_das_active:
                if current_time - self.last_time >= self.das_delay:
                    self.is_das_active = True
                    self.last_time = current_time
                    return True
            elif current_time - self.last_time >= self.arr_delay:
                self.last_time = current_time
                return True
        else:
            self.is_das_active = False
            self.last_time = current_time
        return False

def handle_events(state, events):
    current_time = pygame.time.get_ticks()
    for event in events:
        if event.type == pygame.QUIT:
            state.running = False
            return
        if not state.game_over:
            handle_key_presses(state, event, current_time)
            handle_key_releases(state, event)

def handle_key_presses(state, event, current_time):
    if event.type != pygame.KEYDOWN:
        return
    
    if event.key == pygame.K_UP:
        try_rotate(state)
    elif event.key == pygame.K_LEFT:
        if state.das_left.update(current_time, True, True):
            move_block(state, -1, 0)
        state.das_right = InputTimer(DAS_DELAY, ARR_DELAY)
    elif event.key == pygame.K_RIGHT:
        if state.das_right.update(current_time, True, True):
            move_block(state, 1, 0)
        state.das_left = InputTimer(DAS_DELAY, ARR_DELAY)
    elif event.key == pygame.K_DOWN:
        state.fall_speed = 50
        state.is_soft_dropping = True
        state.soft_drop_distance = 0
    elif event.key == pygame.K_SPACE:
        handle_hard_drop(state)
    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and not state.hold_used:
        handle_hold(state)

def handle_key_releases(state, event):
    if event.type != pygame.KEYUP:
        return
    
    if event.key == pygame.K_DOWN:
        state.fall_speed = 1000
        if state.is_soft_dropping and state.soft_drop_distance > 0:
            soft_drop_score = gameplay.calculate_soft_drop_score(state.soft_drop_distance)
            state.score += soft_drop_score
            if soft_drop_score > 0:
                gameplay.score_animation = f"+{soft_drop_score}"
                gameplay.score_timer = 100
        state.is_soft_dropping = False
        state.soft_drop_distance = 0

def handle_continuous_input(state):
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    block_moved = False

    if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        if state.das_left.update(current_time, True, False) and current_time - state.last_movement_time >= state.move_repeat_delay:
            block_moved = move_block(state, -1, 0)
    if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
        if state.das_right.update(current_time, True, False) and current_time - state.last_movement_time >= state.move_repeat_delay:
            block_moved = move_block(state, 1, 0)

    return block_moved

def handle_gravity(state, delta_time):
    state.fall_time += delta_time
    current_time = pygame.time.get_ticks()

    if state.fall_time >= state.fall_speed:
        state.fall_time = 0
        if gameplay.is_valid_move(state.current_block, state.grid, dy=1):
            state.current_block.y += 1
            if state.is_soft_dropping:
                state.soft_drop_distance += 1
            state.has_landed = False
            state.lock_time = 0
        else:
            if not state.has_landed:
                state.has_landed = True
                state.lock_time = current_time

    if state.has_landed and current_time - state.lock_time >= LOCK_DELAY:
        if state.is_soft_dropping and state.soft_drop_distance > 0:
            soft_drop_score = gameplay.calculate_soft_drop_score(state.soft_drop_distance)
            state.score += soft_drop_score
            state.soft_drop_distance = 0
        is_tspin = gameplay.check_for_tspin(state.current_block, state.grid, state.last_action_was_rotation)
        handle_block_placement(state, is_tspin)
        state.has_landed = False
        state.lock_time = 0
        state.lock_resets = 0
        state.last_action_was_rotation = False

def try_rotate(state):
    '''Attempt to rotate the current block, including wall kicks.'''
    original_x, original_y = state.current_block.x, state.current_block.y
    if state.current_block.rotate(state.grid):
        reset_lock_delay(state)
        state.last_action_was_rotation = True
        return True
    
    kicks = [(1, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)]
    for dx, dy in kicks:
        state.current_block.x = original_x + dx
        state.current_block.y = original_y + dy
        if state.current_block.rotate(state.grid):
            reset_lock_delay(state)
            state.last_action_was_rotation = True
            return True
        state.current_block.x, state.current_block.y = original_x, original_y
    return False

def move_block(state, dx, dy):
    if gameplay.is_valid_move(state.current_block, state.grid, dx=dx, dy=dy):
        state.current_block.x += dx
        state.current_block.y += dy
        state.last_movement_time = pygame.time.get_ticks()
        reset_lock_delay(state)
        state.last_action_was_rotation = False
        return True
    return False

def reset_lock_delay(state):
    if state.has_landed and state.lock_resets < state.max_lock_resets:
        state.lock_time = pygame.time.get_ticks()
        state.lock_resets += 1

def handle_hard_drop(state):
    initial_y = state.current_block.y
    while gameplay.is_valid_move(state.current_block, state.grid, dy=1):
        state.current_block.y += 1
    drop_score = gameplay.calculate_hard_drop_score(initial_y, state.current_block.y)
    state.score += drop_score
    if drop_score > 0:
        gameplay.score_animation = f"+{drop_score}"
        gameplay.score_timer = 100
    is_tspin = gameplay.check_for_tspin(state.current_block, state.grid, state.last_action_was_rotation)
    handle_block_placement(state, is_tspin)
    state.has_landed = False
    state.lock_time = 0
    state.lock_resets = 0
    state.last_action_was_rotation = False

def handle_hold(state):
    if state.hold_block is None:
        state.hold_block = state.current_block
        state.current_block = state.next_blocks.pop(0)
        state.next_blocks.append(gameplay.create_block())
    else:
        state.hold_block, state.current_block = state.current_block, state.hold_block
    state.hold_used = True
    state.current_block.x = design.GRID_WIDTH // 2 - len(state.current_block.get_shape()[0]) // 2
    state.current_block.y = 0
    state.has_landed = False
    state.lock_time = 0
    state.lock_resets = 0
    state.last_action_was_rotation = False

def handle_block_placement(state, is_tspin):
    gameplay.place_block(state.current_block, state.grid)
    cleared, line_score = gameplay.clear_lines(state.grid)
    state.lines_cleared += cleared
    
    if is_tspin and cleared > 0:
        line_score = int(line_score * 1.5)
        gameplay.score_animation = f"T-SPIN +{line_score}"
        gameplay.score_timer = 150
    
    state.score += line_score
    state.combo_count, combo_score = gameplay.update_combo(state.combo_count, cleared, state.grid)
    state.score += combo_score
    
    state.current_block = state.next_blocks.pop(0)
    state.next_blocks.append(gameplay.create_block())
    state.hold_used = False
    
    if not gameplay.is_valid_move(state.current_block, state.grid):
        state.game_over = True