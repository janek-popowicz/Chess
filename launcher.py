import pygame
import json

import sys
import os

# Dodaj katalog główny do sys.path, jeśli nie jest już w nim zawarty
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import normal_games.normal_game
import normal_games.test_mode_normal_game
import custom_board_game.board_maker
import custom_board_game.normal_game_custom_board
import grandmaster.grandmaster_game
import settings
import graphics

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
    volume = volume / 100
    
    # Kolory
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    HIGHLIGHT = (200, 200, 200)

    # Czcionka
    font = pygame.font.Font(None, 74)

    # Opcje menu
    menu_options = [
        "Graj z przyjacielem na tym komputerze", #0
        "Graj z własną planszą",#1
        "Kreator planszy",#2
        "Graj z botem",#3
        "Graj z arcymistrzem",#4
        "Graj w sieci lokalnej",#5
        "Ustawienia",#6
        "Wyjście do systemu",#7
        "Tryb terminalowy"#8
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

    # Load the background image
    background = pygame.image.load("background.png")
    background = pygame.transform.scale(background, (1600, 1000))  # Ensure the image fits the screen size

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
                    if do_an_action(selected_option, screen) == False:
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text_white, text_gray) in enumerate(menu_texts):
                    text_rect = text_white.get_rect(center=(800, 150 + i * 100))
                    if text_rect.collidepoint(mouse_pos):
                        selected_option = i
                        if do_an_action(selected_option, screen) == False:
                            running = False

        # Sprawdzenie kolizji myszy z opcjami menu
        for i, (text_white, text_gray) in enumerate(menu_texts):
            text_rect = text_white.get_rect(center=(800, 150 + i * 100))
            if text_rect.collidepoint(mouse_pos):
                selected_option = i

        # Draw background and menu
        draw_menu(selected_option, screen, menu_texts, background, text_white, text_gray, BLACK)

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()


def do_an_action(selected_option, screen):
    if selected_option == 0: # Normalna gra
        normal_games.normal_game.main()
    elif selected_option == 1: # Custom board game
        pygame.mixer.music.stop()
        custom_board_game.normal_game_custom_board.main()
    elif selected_option == 2: # Board maker
        pygame.mixer.music.stop()
        custom_board_game.board_maker.main()
    elif selected_option == 4: # Arcymistrz
        pygame.mixer.music.stop()
        player_color = graphics.choose_color_dialog(screen, 100)
        grandmaster_name = graphics.choose_grandmaster_dialog(screen, 100)
        grandmaster.grandmaster_game.main('b', 'kasparov')
    elif selected_option == 6: # Ustawienia
        pygame.mixer.music.stop()
        settings.main()
    elif selected_option == 7: #Wyjście do systemu
        return False
    elif selected_option == 8:
        normal_games.test_mode_normal_game.main()
    elif selected_option == 5:
        server_or_client = graphics.choose_color_dialog(screen, 100)
        if server_or_client == "w":
            import multiplayer.client
            multiplayer.client.main()
        elif server_or_client == "b":
            import multiplayer.server
            multiplayer.server.main()
    elif selected_option == 3:
        import algorithms.ai_game
        algorithms.ai_game.main()
    return True



# Funkcja do rysowania menu
def draw_menu(selected_option:int, screen, menu_texts, background, text_white, text_gray, BLACK)->None:
    """rysuje menu i renderuje tekst

    Args:
        selected_option (int): numer wybranej opcji z listy menu_options
    """
    screen.blit(background, (0, 0))  # Draw the background image first
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


main()