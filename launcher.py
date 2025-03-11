import pygame
import sys
import json
# Funkcja do rysowania menu
def draw_menu(selected_option:int, screen, menu_texts, text_white, text_gray,BLACK)->None:
    """rysuje menu i renderuje tekst

    Args:
        selected_option (int): numer wybranej opcji z listy menu_options
    """
    screen.fill(BLACK)
    for i, (text_white, text_gray) in enumerate(menu_texts):
        text = text_white if i == selected_option else text_gray
        text_rect = text.get_rect(center=(800, 150 + i * 100))
        screen.blit(text, text_rect)
    pygame.display.flip()

def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960"}

# Funkcja główna
def main():


    # Inicjalizacja Pygame
    pygame.init()
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)
    # Ustawienia ekranu
    screen = pygame.display.set_mode((1600, 1000))
    pygame.display.set_caption("Chess Game Launcher")
    config = load_config()
    volume = config["volume"]
    volume = volume/100
    # Kolory
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    HIGHLIGHT = (200, 200, 200)

    # Czcionka
    font = pygame.font.Font(None, 74)

    # Opcje menu
    menu_options = [
        "Zwykła gra",
        "Tryb niestandardowy",
        "Board maker",
        "Ustawienia",
        "Wyjście"
    ]

    selected_option = 0
    running = True

    # Renderowanie tekstu tylko raz
    menu_texts = []
    for option in menu_options:
        text_white = font.render(option, True, WHITE)
        text_gray = font.render(option, True, GRAY)
        menu_texts.append((text_white, text_gray))

    # Dodanie muzyki
    pygame.mixer.music.load("menu_background_music.mp3")
    pygame.mixer.music.play(start=5)
    pygame.mixer.music.set_volume(volume)

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
                        import normal_game
                        normal_game.main()
                    elif selected_option == 1:
                        running = False
                        pygame.mixer.music.stop()
                        pygame.quit()
                        import normal_game_custom_board
                        normal_game_custom_board.main()
                    elif selected_option == 2:
                        running = False
                        pygame.mixer.music.stop()
                        pygame.quit()
                        import board_maker
                        board_maker.main()
                    elif selected_option == 3:
                        running=False
                        pygame.mixer.music.stop()
                        pygame.quit()
                        import settings
                        settings.main()
                    elif selected_option == 4:
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text_white, text_gray) in enumerate(menu_texts):
                    text_rect = text_white.get_rect(center=(800, 150 + i * 100))
                    if text_rect.collidepoint(mouse_pos):
                        selected_option = i
                        if selected_option == 0:
                            running = False
                            pygame.mixer.music.stop()
                            pygame.quit()
                            import normal_game
                            normal_game.main()
                        elif selected_option == 1:
                            running = False
                            pygame.mixer.music.stop()
                            pygame.quit()
                            import normal_game_custom_board
                            normal_game_custom_board.main()
                        elif selected_option == 2:
                            running = False
                            pygame.mixer.music.stop()
                            pygame.quit()
                            import board_maker
                            board_maker.main()
                        elif selected_option == 3:
                            running=False
                            pygame.mixer.music.stop()
                            pygame.quit()
                            import settings
                            settings.main()
                        elif selected_option == 4:
                            running = False

        # Sprawdzenie kolizji myszy z opcjami menu
        for i, (text_white, text_gray) in enumerate(menu_texts):
            text_rect = text_white.get_rect(center=(800, 150 + i * 100))
            if text_rect.collidepoint(mouse_pos):
                selected_option = i

        draw_menu(selected_option, screen, menu_texts, text_white, text_gray,BLACK)

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

main()