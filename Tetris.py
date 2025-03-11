import pygame
import gameplay
import design
import control
import menu
from pygame import mixer

# Constants
FPS = 60
BASE_FALL_SPEED = 1000
LINES_PER_LEVEL = 10
MIN_SPEED_FACTOR = 0.1
TRANSITION_DELAY = 1000  # ms for countdown and animations

def run_game(screen, clock, state, current_level):
    """Run the main game loop, returning state (QUIT, GAME_OVER, or MENU)."""
    level_speed_factor = max(MIN_SPEED_FACTOR, 1.0 - ((current_level - 1) * 0.15))
    state.fall_speed = BASE_FALL_SPEED * level_speed_factor
    
    base_level = current_level
    restart_button = None
    pause_button = None
    was_game_over = False
    input_active = False
    input_text = ""
    new_high_score = False
    input_buffer_frame = False
    flash_start_time = 0
    paused = False
    
    # Sound effects
    mixer.init()
    line_clear_sound = mixer.Sound("assets/sounds/line_clear.wav")
    game_over_sound = mixer.Sound("assets/sounds/game_over.wav")

    while state.running:
        screen.fill(design.BACKGROUND_COLOR)
        delta_time = clock.tick(FPS)

        game_events = pygame.event.get()
        for event in game_events:
            if event.type == pygame.QUIT:
                print("QUIT event detected in game loop")
                state.running = False
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused
                mixer.Sound("assets/sounds/pause.wav").play()

        if not state.running:
            break

        if paused:
            design.draw_pause_screen(screen)
            pygame.display.update()
            continue

        if not state.game_over:
            control.handle_events(state, game_events)
            control.handle_continuous_input(state)
            control.handle_gravity(state, delta_time)

            new_level = base_level + (state.lines_cleared // LINES_PER_LEVEL)
            if new_level != current_level:
                current_level = new_level
                level_speed_factor = max(MIN_SPEED_FACTOR, 1.0 - ((current_level - 1) * 0.15))
                state.fall_speed = BASE_FALL_SPEED * level_speed_factor
                mixer.Sound("assets/sounds/level_up.wav").play()

            if state.lines_cleared % LINES_PER_LEVEL == 0 and state.lines_cleared > 0:
                line_clear_sound.play()

        ghost_block = gameplay.get_ghost_piece(state.current_block, state.grid) if not state.game_over else None

        # Enhanced rendering
        design.draw_background(screen)  # Assume this adds a gradient or texture
        design.draw_grid(screen, state.grid)
        if not state.game_over:
            design.draw_ghost_piece(screen, ghost_block)
            design.draw_block(screen, state.current_block)
        design.draw_next_blocks(screen, state.next_blocks)
        design.draw_held_piece(screen, state.hold_block)
        design.draw_score(screen, state.score, state.combo_count)
        design.draw_game_level(screen, current_level)
        design.draw_lines_cleared(screen, state.lines_cleared)
        design.draw_score_animation(screen, design.font, design.SCREEN_WIDTH - 120, design.SCREEN_HEIGHT // 2)

        if state.game_over:
            if not was_game_over:
                game_over_sound.play()
                new_high_score = gameplay.update_high_scores(state.score)
                if new_high_score:
                    input_active = True
                    input_text = ""
                    pygame.event.clear()
                    pygame.key.get_pressed()
                    print(f"Entering input mode, input_text: '{input_text}'")
                    input_buffer_frame = True
                    flash_start_time = pygame.time.get_ticks()
                was_game_over = True

            pygame.event.set_grab(False)
            restart_button, pause_button = menu.draw_game_over(
                screen, state.score, new_high_score, input_active, input_text, flash_start_time
            )

            if input_active:
                if input_buffer_frame:
                    pygame.event.clear()
                    input_buffer_frame = False
                else:
                    input_active, input_text = menu.handle_game_over_input(game_events, input_text, state.score)
                    if not input_active and new_high_score:
                        flash_start_time = pygame.time.get_ticks()
                        print("Input completed, resetting flash_start_time")

            for event in game_events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button and restart_button.collidepoint(event.pos):
                        print("Restart clicked")
                        return "RESTART"
                    if pause_button and pause_button.collidepoint(event.pos):
                        print("Menu clicked")
                        return "MENU"

        pygame.display.update()

    return "GAME_OVER" if state.game_over else "QUIT"

def main():
    pygame.init()
    mixer.init()
    screen = menu.create_screen()
    clock = pygame.time.Clock()
    countdown_font = pygame.font.Font(None, 100)
    
    menu_active = True
    running = True
    play_button = None
    level_button = None
    current_level = menu.LEVEL_OPTIONS[menu.current_level_index]
    
    # Background music
    mixer.music.load("assets/music/background.mp3")
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)  # Loop indefinitely

    while running:
        screen.fill(design.BACKGROUND_COLOR)
        delta_time = clock.tick(FPS)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                print("QUIT event detected in main loop")
                running = False
                break

        if menu_active:
            play_button, level_button = menu.draw_start_menu(screen)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button and play_button.collidepoint(event.pos):
                        current_level = menu.LEVEL_OPTIONS[menu.current_level_index]
                        menu_active = False
                        countdown = 3
                        countdown_start_time = pygame.time.get_ticks()
                        mixer.Sound("assets/sounds/countdown.wav").play()
                        while countdown > 0 and running:
                            menu.draw_countdown(screen, countdown_font, countdown)
                            pygame.display.update()
                            current_time = pygame.time.get_ticks()
                            if current_time - countdown_start_time >= TRANSITION_DELAY:
                                countdown -= 1
                                countdown_start_time = current_time
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    running = False
                                    countdown = 0
                                    break
                    elif level_button and level_button.collidepoint(event.pos):
                        current_level = menu.handle_level_button_click()
                        play_button, level_button = menu.draw_start_menu(screen)
                        pygame.display.update()
        else:
            state = control.GameState(current_level)
            result = run_game(screen, clock, state, current_level)
            if result == "RESTART":
                menu_active = False
                continue
            elif result == "MENU":
                menu_active = True
            elif result == "QUIT":
                running = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
