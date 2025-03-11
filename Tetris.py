import pygame
import gameplay
import design
import control
import menu

def run_game(screen, clock, state, current_level):
    """运行游戏主循环，返回状态（QUIT 或 GAME_OVER）"""
    base_fall_speed = 1000
    LINES_PER_LEVEL = 10
    level_speed_factor = max(0.1, 1.0 - ((current_level - 1) * 0.15))
    state.fall_speed = base_fall_speed * level_speed_factor
    
    base_level = current_level
    restart_button = None
    was_game_over = False
    input_active = False
    input_text = ""
    new_high_score = False
    input_buffer_frame = False
    flash_start_time = 0

    while state.running:
        screen.fill(design.BACKGROUND_COLOR)
        delta_time = clock.tick(60)

        game_events = pygame.event.get()
        for event in game_events:
            if event.type == pygame.QUIT:
                print("QUIT event detected in game loop")
                state.running = False
                return "QUIT"

        control.handle_events(state, game_events)
        if not state.running:
            break

        if not state.game_over:
            control.handle_continuous_input(state)
            control.handle_gravity(state, delta_time)

            new_level = base_level + (state.lines_cleared // LINES_PER_LEVEL)
            if new_level != current_level:
                current_level = new_level
                level_speed_factor = max(0.1, 1.0 - ((current_level - 1) * 0.15))
                state.fall_speed = base_fall_speed * level_speed_factor

        ghost_block = gameplay.get_ghost_piece(state.current_block, state.grid) if not state.game_over else None

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
                new_high_score = gameplay.update_high_scores(state.score)
                if new_high_score:
                    input_active = True
                    input_text = ""
                    pygame.event.clear()
                    pygame.event.pump()
                    pygame.key.get_pressed()
                    print(f"Entering input mode, input_text initialized to: '{input_text}'")
                    input_buffer_frame = True
                    flash_start_time = pygame.time.get_ticks()  # 初始设置
                was_game_over = True

            pygame.event.set_grab(False)
            restart_button = menu.draw_game_over(
                screen, state.score, new_high_score, input_active, input_text, flash_start_time
            )

            if input_active:
                if input_buffer_frame:
                    pygame.event.clear()
                    input_buffer_frame = False
                    print("Skipping first frame of input to clear residual events")
                else:
                    input_active, input_text = menu.handle_game_over_input(game_events, input_text, state.score)
                    if not input_active and new_high_score:  # 输入完成后且是新高分
                        flash_start_time = pygame.time.get_ticks()  # 重置闪烁开始时间
                        print("Input completed, resetting flash_start_time for 5-second flash")

            for event in game_events:
                if event.type == pygame.MOUSEBUTTONDOWN and restart_button and restart_button.collidepoint(event.pos):
                    print("Restart button clicked")
                    state = control.GameState(current_level)
                    state.fall_speed = base_fall_speed * level_speed_factor
                    state.running = True
                    state.game_over = False
                    state.lines_cleared = 0
                    state.score = 0
                    state.combo_count = 0
                    input_active = False
                    new_high_score = False
                    was_game_over = False

        pygame.display.update()

    return "GAME_OVER" if state.game_over else "QUIT"

def main():
    pygame.init()
    
    screen = menu.create_screen()
    clock = pygame.time.Clock()
    countdown_font = pygame.font.Font(None, 100)
    
    menu_active = True
    running = True
    play_button = None
    level_button = None
    current_level = menu.LEVEL_OPTIONS[menu.current_level_index]

    while running:
        screen.fill(design.BACKGROUND_COLOR)
        delta_time = clock.tick(60)
        
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
                        while countdown > 0 and running:
                            menu.draw_countdown(screen, countdown_font, countdown)
                            pygame.display.update()
                            current_time = pygame.time.get_ticks()
                            if current_time - countdown_start_time >= 1000:
                                countdown -= 1
                                countdown_start_time = current_time
                            countdown_events = pygame.event.get()
                            for event in countdown_events:
                                if event.type == pygame.QUIT:
                                    print("QUIT event detected in countdown")
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
            if result == "GAME_OVER":
                menu_active = False  # 保持游戏结束状态，直到重启
            elif result == "QUIT":
                running = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()