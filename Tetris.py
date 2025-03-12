'''Tetris.py - Main loop and game initialization'''
import pygame
from GSM import GameStateManager, MenuState, PlayingState, GameOverState
from constants import *
import menu

def main():
    pygame.init()
    screen = menu.create_screen()
    clock = pygame.time.Clock()
    countdown_font = pygame.font.Font(None, 100)

    manager = GameStateManager()
    manager.register_state("menu", MenuState())
    manager.register_state("playing", PlayingState())
    manager.register_state("game_over", GameOverState())
    manager.switch_state("menu")

    running = True
    countdown = None
    countdown_start_time = None
    next_state_pending = None
    next_data_pending = None

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        delta_time = clock.tick(60)

        # Handle countdown before entering next state
        if countdown is not None:
            screen.fill(BACKGROUND_COLOR)
            menu.draw_countdown(screen, countdown_font, countdown)
            current_time = pygame.time.get_ticks()
            if current_time - countdown_start_time >= 1000:
                countdown -= 1
                countdown_start_time = current_time
            if countdown <= 0:
                countdown = None
                if next_state_pending == "playing":
                    manager.switch_state(next_state_pending, next_data_pending)
                next_state_pending = None
                next_data_pending = None
            pygame.display.flip()  # 更新倒计时画面
        else:
            # Update the current state without immediate switching
            next_state, data = manager.current_state.update(events, delta_time)  # 直接调用当前状态的update
            if next_state == "playing":
                countdown = 3
                countdown_start_time = pygame.time.get_ticks()
                next_state_pending = next_state
                next_data_pending = data
            elif next_state == "quit":
                running = False
            elif next_state:
                manager.switch_state(next_state, data)

            # 绘制当前状态
            manager.draw(screen)
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()