'''GSM.py - Game State Manager(manage game states transitions)'''
import pygame
import control
import design
import gameplay
import menu
from constants import *

class GameState:
    """Base class for all game states."""
    def update(self, events, delta_time):
        pass
    
    def draw(self, screen):
        pass
    
    def on_enter(self):
        pass
    
    def on_exit(self):
        pass

class MenuState(GameState):
    """Main menu state."""
    def __init__(self):
        self.current_level_index = 0
        self.play_button = None
        self.level_button = None

    def update(self, events, delta_time):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button and self.play_button.collidepoint(event.pos):
                    menu.current_level_index = self.current_level_index
                    print(f"Play button clicked, switching to playing with level {LEVEL_OPTIONS[self.current_level_index]}")
                    return "playing", LEVEL_OPTIONS[self.current_level_index]
                elif self.level_button and self.level_button.collidepoint(event.pos):
                    self.current_level_index = (self.current_level_index + 1) % len(LEVEL_OPTIONS)
                    menu.current_level_index = self.current_level_index
                    print(f"Level button clicked, new level index: {self.current_level_index}")
        return None, None

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        self.play_button, self.level_button = menu.draw_start_menu(screen)

    def on_enter(self):
        pygame.display.set_caption("Tetris - Menu")
        if hasattr(menu, 'current_level_index'):
            self.current_level_index = menu.current_level_index

class PlayingState(GameState):
    """Game playing state."""
    def __init__(self):
        self.state = None
        self.current_level = 1

    def update(self, events, delta_time):
        if not self.state:
            return None, None

        for event in events:
            if event.type == pygame.QUIT:
                print("QUIT event detected in game loop")
                self.state.running = False
                return "quit", None  # 返回"quit"作为退出信号

        control.handle_events(self.state, events)
        if not self.state.running:
            return "quit", None

        if not self.state.game_over:
            control.handle_continuous_input(self.state)
            control.handle_gravity(self.state, delta_time)
            new_level = self.current_level + (self.state.lines_cleared // LINES_PER_LEVEL)
            if new_level != self.current_level:
                self.current_level = new_level
                level_speed_factor = max(0.1, 1.0 - ((self.current_level - 1) * 0.15))
                self.state.fall_speed = BASE_FALL_SPEED * level_speed_factor
        elif self.state.game_over:
            return "game_over", {"score": self.state.score, "current_level": self.current_level}

        return None, None

    def draw(self, screen):
        if not self.state:
            return
        screen.fill(BACKGROUND_COLOR)
        ghost_block = gameplay.get_ghost_piece(self.state.current_block, self.state.grid) if not self.state.game_over else None
        design.draw_grid(screen, self.state.grid)
        if not self.state.game_over:
            design.draw_ghost_piece(screen, ghost_block)
            design.draw_block(screen, self.state.current_block)
        design.draw_next_blocks(screen, self.state.next_blocks)
        design.draw_held_piece(screen, self.state.hold_block)
        design.draw_score(screen, self.state.score, self.state.combo_count)
        design.draw_game_level(screen, self.current_level)
        design.draw_lines_cleared(screen, self.state.lines_cleared)
        design.draw_score_animation(screen, design.font, SCREEN_WIDTH - 120, SCREEN_HEIGHT // 2)

    def on_enter(self):
        self.state = control.GameState(self.current_level)
        self.state.fall_speed = BASE_FALL_SPEED * max(0.1, 1.0 - ((self.current_level - 1) * 0.15))
        pygame.display.set_caption("Tetris - Playing")

    def on_exit(self):
        self.state = None

class GameOverState(GameState):
    """Game over state."""
    def __init__(self):
        self.score = 0
        self.current_level = 1
        self.input_active = False
        self.input_text = ""
        self.new_high_score = False
        self.flash_start_time = 0
        self.restart_button = None
        self.was_game_over = False

    def update(self, events, delta_time):
        if not self.was_game_over:
            self.new_high_score = gameplay.update_high_scores(self.score)
            if self.new_high_score:
                self.input_active = True
                self.input_text = ""
                pygame.event.clear()
                pygame.event.pump()
                pygame.key.get_pressed()
                print(f"Entering input mode, input_text initialized to: '{self.input_text}'")
                self.flash_start_time = pygame.time.get_ticks()
            self.was_game_over = True

        pygame.event.set_grab(False)
        if self.input_active:
            self.input_active, self.input_text = menu.handle_game_over_input(events, self.input_text, self.score)
            if not self.input_active and self.new_high_score:
                self.flash_start_time = pygame.time.get_ticks()
                print("Input completed, resetting flash_start_time for 5-second flash")

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.restart_button and self.restart_button.collidepoint(event.pos):
                print("Restart button clicked")
                return "playing", self.current_level
        return None, None

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        self.restart_button = menu.draw_game_over(
            screen, self.score, self.new_high_score, self.input_active, self.input_text, self.flash_start_time
        )

    def on_enter(self):
        pygame.display.set_caption("Tetris - Game Over")

    def on_exit(self):
        self.was_game_over = False

class GameStateManager:
    """Manages game states and transitions."""
    def __init__(self):
        self.states = {}
        self.current_state = None

    def register_state(self, state_name, state_instance):
        self.states[state_name] = state_instance

    def switch_state(self, state_name, data=None):
        if self.current_state:
            self.current_state.on_exit()
        self.current_state = self.states[state_name]
        if state_name == "playing" and data is not None:
            self.current_state.current_level = data
        elif state_name == "game_over" and data is not None:
            self.current_state.score = data["score"]
            self.current_state.current_level = data["current_level"]
        self.current_state.on_enter()

    def update(self, events, delta_time):
        if self.current_state:
            return self.current_state.update(events, delta_time)  # 只返回状态，不执行切换
        return None, None

    def draw(self, screen):
        if self.current_state:
            self.current_state.draw(screen)