import pygame
import json
import subprocess
import sys
import os

# Dodaj katalog główny do sys.path, jeśli nie jest już w nim zawarty
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import normal_games.normal_game
import normal_games.test_mode_normal_game
import custom_board_game.board_maker
import custom_board_game.normal_game_custom_board
import grandmaster.grandmaster_game
import algorithms.algorithms_game
import settings
import graphics
import grandmaster.pgn_to_fen
import ai_model.ml_game as ml_game
from language import global_translations, language_selection_screen  # Add this import at the top

# Funkcja główna
def main():
    # Inicjalizacja Pygame
    pygame.init()
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)
    
    # Ustawienia ekranu
    screen = pygame.display.set_mode((1260, 960))
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
    menu_options = global_translations.get('menu_options')

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

    #Dodanie tła
    background = pygame.image.load("interface/background.png")
    background = pygame.transform.scale(background, (1260, 960))

    # Load menu sounds
    try:
        menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
        menu_cursor_sound.set_volume(volume)
    except:
        print("Warning: Could not load menu sound effect")
        menu_cursor_sound = None

    # Create language icon rect outside the main loop
    lang_icon_rect = pygame.Rect(screen.get_width() - 70, screen.get_height() - 70, 50, 50)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                    if menu_cursor_sound:
                        menu_cursor_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                    if menu_cursor_sound:
                        menu_cursor_sound.play()
                elif event.key == pygame.K_RETURN:
                    if do_an_action(selected_option, screen) == False:
                        running = False
                    else:
                        # Restart the main function
                        pygame.quit()
                        return main()
            # Add language icon click handling here
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check language icon click first
                if lang_icon_rect.collidepoint(mouse_pos):
                    language_selection_screen(screen)
                
                # Rest of the click handling
                for i, (text_white, text_gray) in enumerate(menu_texts):
                    text_rect = text_white.get_rect(center=(630, 50 + i * 90))
                    if text_rect.collidepoint(mouse_pos):
                        selected_option = i
                        if do_an_action(selected_option, screen) == False:
                            running = False
                        else:
                            # Restart the main function
                            pygame.quit()
                            return main()

        # Sprawdzenie kolizji myszy z opcjami menu
        for i, (text_white, text_gray) in enumerate(menu_texts):
            text_rect = text_white.get_rect(center=(630, 50 + i * 90))
            if text_rect.collidepoint(mouse_pos) and selected_option != i:
                if menu_cursor_sound:
                    menu_cursor_sound.play()
                selected_option = i

        # Draw background and menu
        draw_menu(selected_option, screen, menu_texts, background, text_white, text_gray, BLACK)

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()


def do_an_action(selected_option, screen):
    if selected_option == 0: # Normalna gra
        normal_games.normal_game.main(600)
        return True
    elif selected_option == 1: # Niestandardowa plansza
        pygame.mixer.music.stop()
        choice = graphics.choose_custom_board_mode(screen, 100)
        if choice == "play":
            custom_board_game.normal_game_custom_board.main()
        elif choice == "create":
            custom_board_game.board_maker.main()
        return True
    elif selected_option == 2: # Bot
        pygame.mixer.music.stop()
        player_color = graphics.choose_color_dialog(screen, 100)
        if player_color == None:
            return True
        algorithm = graphics.choose_algorithm_dialog(screen, 100)
        if algorithm == "neural":
            # Temporarily disable neural network
            print("Neural network not implemented yet")
            return True
        elif algorithm == "minimax" or algorithm == "monte_carlo":
            algorithms.algorithms_game.main(player_color, algorithm)
        return True
    elif selected_option == 3: # Arcymistrz
        pygame.mixer.music.stop()
        player_color = graphics.choose_color_dialog(screen, 100)
        if player_color == None:
            return True
        grandmaster_name = graphics.choose_grandmaster_dialog(screen, 100)
        grandmaster.grandmaster_game.main(player_color, grandmaster_name)
        return True
    elif selected_option == 4: # Gra w sieci
        server_or_client = graphics.choose_color_dialog(screen, 100)
        if server_or_client == None:
            return True
        if server_or_client == "w":
            import multiplayer.client
            multiplayer.client.main()
        elif server_or_client == "b":
            import multiplayer.server
            multiplayer.server.main()
        return True
    elif selected_option == 5: # Ustawienia
        pygame.mixer.music.stop()
        settings.main()
        return True
    elif selected_option == 6: # Wyjście
        return False
    elif selected_option == 7: # Konwerter PGN do FEN
        pygame.mixer.music.stop()
        grandmaster.pgn_to_fen.main()
        return True
    elif selected_option == 8: #Pomoc
        open_pdf("help.pdf")
    return True



# Funkcja do rysowania menu
def draw_menu(selected_option:int, screen, menu_texts, background, text_white, text_gray, BLACK)->None:
    """rysuje menu i renderuje tekst z czarnym tłem pod wybraną opcją"""
    screen.blit(background, (0, 0))
    
    # Get mouse position for hover effect
    mouse_pos = pygame.mouse.get_pos()
    
    # Draw menu options
    for i, (text_white, text_gray) in enumerate(menu_texts):
        text = text_white if i == selected_option else text_gray
        text_rect = text.get_rect(center=(630, 50 + i * 90))
        
        if text_rect.collidepoint(mouse_pos) or i == selected_option:
            background_rect = text_rect.inflate(20, 10)
            background_surface = pygame.Surface((background_rect.width, background_rect.height))
            background_surface.fill(BLACK)
            background_surface.set_alpha(200)
            screen.blit(background_surface, background_rect)
            screen.blit(text_white, text_rect)
        else:
            screen.blit(text_gray, text_rect)
    
    # Draw language icon
    try:
        lang_icon = pygame.image.load('interface/language.png')
        lang_icon = pygame.transform.scale(lang_icon, (50, 50))
        lang_icon_rect = pygame.Rect(screen.get_width() - 70, screen.get_height() - 70, 50, 50)
        
        # Add hover effect for language icon
        if lang_icon_rect.collidepoint(pygame.mouse.get_pos()):
            hover_surface = pygame.Surface((50, 50))
            hover_surface.fill((255, 215, 0))  # Gold color
            hover_surface.set_alpha(100)
            screen.blit(hover_surface, lang_icon_rect)
        
        screen.blit(lang_icon, lang_icon_rect)
    except:
        print("Warning: Could not load language icon")
            
    pygame.display.flip()


def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960"}

def open_pdf(PDF_PATH):
    try:
        if sys.platform == "win32":
            subprocess.run(["start", PDF_PATH], shell=True)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", PDF_PATH])
        else:  # Linux
            subprocess.run(["xdg-open", PDF_PATH])
    except Exception as e:
        print(f"Nie udało się otworzyć pliku PDF: {e}")

# Start the launcher
if __name__ == "__main__":
    while True:
        main()
        break

