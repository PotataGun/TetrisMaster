import pygame
import design
import gameplay
import control
import menu

def draw_countdown(screen, font, count):
    """绘制倒计时数字"""
    text = font.render(str(count), True, design.WHITE)
    text_rect = text.get_rect(center=(design.SCREEN_WIDTH // 2, design.SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

def main():
    pygame.init()
    
    screen = menu.create_screen()
    clock = pygame.time.Clock()
    
    # 创建一个较大的字体用于倒计时
    countdown_font = pygame.font.Font(None, 100)
    
    # Initial state
    menu_active = True
    running = True
    play_button = None
    level_button = None
    current_level = menu.LEVEL_OPTIONS[menu.current_level_index]

    while running:
        screen.fill(design.BACKGROUND_COLOR)
        delta_time = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and menu_active:
                if play_button and play_button.collidepoint(event.pos):
                    current_level = menu.LEVEL_OPTIONS[menu.current_level_index]
                    menu_active = False
                    # 开始倒计时
                    countdown = 3
                    countdown_start_time = pygame.time.get_ticks()
                    while countdown > 0:
                        screen.fill(design.BACKGROUND_COLOR)
                        draw_countdown(screen, countdown_font, countdown)
                        pygame.display.update()
                        # 每秒减少一次
                        current_time = pygame.time.get_ticks()
                        if current_time - countdown_start_time >= 1000:
                            countdown -= 1
                            countdown_start_time = current_time
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                countdown = 0  # 退出倒计时
                    if not running:
                        break
                elif level_button and level_button.collidepoint(event.pos):
                    current_level = menu.handle_level_button_click()
                    play_button, level_button = menu.draw_start_menu(screen)
                    pygame.display.update()

        if menu_active:
            play_button, level_button = menu.draw_start_menu(screen)
        else:
            state = control.GameState(current_level)
            base_fall_speed = 1000
            LINES_PER_LEVEL = 10
            level_speed_factor = max(0.1, 1.0 - ((current_level - 1) * 0.15))
            state.fall_speed = base_fall_speed * level_speed_factor
            
            base_level = current_level
            restart_button = None
            was_game_over = False

            while not menu_active and state.running:
                screen.fill(design.BACKGROUND_COLOR)
                delta_time = clock.tick(60)

                control.handle_events(state, restart_button)
                running = state.running

                if not state.game_over:
                    block_moved = control.handle_continuous_input(state)
                    control.handle_gravity(state, delta_time)

                    # 更新关卡和速度
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
                        gameplay.end_game(state.score)
                        was_game_over = True
                    restart_button = menu.draw_game_over(screen, state.score)

                pygame.display.update()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()