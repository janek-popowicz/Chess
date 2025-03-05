import pygame
import sys

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Chess Game Launcher")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HIGHLIGHT = (200, 200, 200)

# Czcionka
font = pygame.font.Font(None, 74)

# Opcje menu
menu_options = [
    "Normal Game Terminal Mode",
    "Random AI Game (not done)",
    "Settings (not done)",
    "Exit"
]

# Funkcja do rysowania menu
def draw_menu(selected_option):
    screen.fill(BLACK)
    for i, option in enumerate(menu_options):
        color = WHITE if i == selected_option else GRAY
        text = font.render(option, True, color)
        text_rect = text.get_rect(center=(400, 150 + i * 100))
        screen.blit(text, text_rect)
    pygame.display.flip()

# Funkcja główna
def main():
    selected_option = 0
    running = True

    # Dodanie muzyki
    pygame.mixer.music.load("menu_background_music.mp3")
    pygame.mixer.music.play(start=5)
    pygame.mixer.music.set_volume(10)
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        running = False
                        pygame.mixer.music.stop()
                        pygame.quit()
                        import test_mode_normal_game
                        test_mode_normal_game.main()
                    elif selected_option == 1:
                        running = False
                        pygame.mixer.music.stop()
                        pygame.quit()
                        import test_mode_random_ai_game
                        test_mode_random_ai_game.main()
                    elif selected_option == 2:
                        # Tutaj można dodać kod do ustawień
                        pass
                    elif selected_option == 3:
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, option in enumerate(menu_options):
                    text_rect = font.render(option, True, WHITE).get_rect(center=(400, 150 + i * 100))
                    if text_rect.collidepoint(mouse_pos):
                        selected_option = i
                        if selected_option == 0:
                            running = False
                            pygame.mixer.music.stop()
                            pygame.quit()
                            import test_mode_normal_game
                            test_mode_normal_game.main()
                        elif selected_option == 1:
                            running = False
                            pygame.mixer.music.stop()
                            pygame.quit()
                            import test_mode_random_ai_game
                            test_mode_random_ai_game.main()
                        elif selected_option == 2:
                            # Tutaj można dodać kod do ustawień
                            pass
                        elif selected_option == 3:
                            running = False

        # Sprawdzenie kolizji myszy z opcjami menu
        for i, option in enumerate(menu_options):
            text_rect = font.render(option, True, WHITE).get_rect(center=(400, 150 + i * 100))
            if text_rect.collidepoint(mouse_pos):
                selected_option = i

        draw_menu(selected_option)

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
    sys.exit()
