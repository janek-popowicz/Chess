"""
Moduł zawiera funkcje odpowiedzialne za grafikę i interfejs użytkownika w grze szachowej.

Funkcje te obejmują rysowanie szachownicy, figur, podświetlanie możliwych ruchów, wyświetlanie interfejsu oraz obsługę okien dialogowych.
"""

import pygame
import json
import sys
import time
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import subprocess
CONFIG_FILE = "config.json"

def load_config():
    """
    Ładuje konfigurację gry z pliku JSON.

    Returns:
        dict: Słownik zawierający ustawienia gry.
    """
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "volume": 0.5, 
            "resolution": "1260x960", 
            "icons": "classic", 
            "highlight": 0,
            "nerd_view": False  # Add default nerd_view setting
        }

def draw_board(screen, SQUARE_SIZE, main_board, in_check):
    """
    Rysuje szachownicę na ekranie.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        main_board (Board): Obiekt planszy szachowej.
        in_check (str): Kolor gracza, którego król jest szachowany ('w' lub 'b').
    """
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            if in_check and main_board.board_state[r][c].figure and main_board.board_state[r][c].figure.type == 'K' and main_board.board_state[r][c].figure.color == in_check:
                color = pygame.Color("red")
            pygame.draw.rect(screen, color, pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board, SQUARE_SIZE, pieces, is_reversed=False):
    """
    Rysuje figury na szachownicy.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        board (Board): Obiekt planszy szachowej.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        pieces (dict): Słownik zawierający obrazy figur.
        is_reversed (bool, optional): Czy plansza ma być odwrócona. Defaults to False.
    """
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece != "--":
                if is_reversed:
                    x = c * SQUARE_SIZE
                    y = r * SQUARE_SIZE
                else:
                    x = (7-c) * SQUARE_SIZE
                    y = (7-r) * SQUARE_SIZE
                screen.blit(pieces[piece], pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))

def highlight_moves(screen, field, square_size: int, board, color_move, color_take, is_reversed=False):
    """
    Podświetla możliwe ruchy dla wybranej figury.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        field (Field): Pole, na którym znajduje się wybrana figura.
        square_size (int): Rozmiar pojedynczego pola na szachownicy.
        board (Board): Obiekt planszy szachowej.
        color_move (tuple): Kolor podświetlenia dla możliwych ruchów.
        color_take (tuple): Kolor podświetlenia dla możliwych bić.
        is_reversed (bool, optional): Czy plansza ma być odwrócona. Defaults to False.
    """
    try:
        cords = board.get_legal_moves(field, field.figure.color)
    except AttributeError:
        return None
    for cord in cords:
        highlighted_tile = pygame.Surface((square_size, square_size))
        highlighted_tile.fill(color_move)
        if board.board_state[cord[0]][cord[1]].figure:
            if field.figure.color != board.board_state[cord[0]][cord[1]].figure.color:
                highlighted_tile.fill(color_take)
        if field.figure.type == 'p' and (field.x - cord[1]) != 0:
            highlighted_tile.fill(color_take)
            
        # Calculate position based on is_reversed
        if is_reversed:
            x = cord[1] * square_size
            y = cord[0] * square_size
        else:
            x = (7-cord[1]) * square_size
            y = (7-cord[0]) * square_size
            
        screen.blit(highlighted_tile, (x, y))

def draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times, in_check, check_text, nerd_view=False, evaluation=None, ping=None):
    """
    Rysuje interfejs użytkownika obok szachownicy.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        turn (str): Aktualna tura ('w' dla białych, 'b' dla czarnych).
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        BLACK (tuple): Kolor tła interfejsu.
        texts (tuple): Teksty wyświetlane w interfejsie.
        player_times (tuple): Czas gry dla obu graczy.
        in_check (str): Kolor gracza, którego król jest szachowany ('w' lub 'b').
        check_text (pygame.Surface): Tekst informujący o szachu.
        nerd_view (bool, optional): Czy wyświetlać dodatkowe informacje. Defaults to False.
        evaluation (float, optional): Ocena pozycji. Defaults to None.
        ping (int, optional): Ping w ms. Defaults to None.
    """

    # In files where you're using draw_interface (like normal_game.py, client.py, etc.)
    config = load_config()
    nerd_view = config.get("nerd_view", False)  # Get nerd_view from config with False as default

    # Czarny prostokąt z prawej - tło
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE * 8, 0, 200, SQUARE_SIZE * 8))
    # teksty tur graczy
    if turn == 'w':
        screen.blit(texts[0][0], texts[0][1])
    else:
        screen.blit(texts[1][0], texts[1][1])

    #czasty graczy
    screen.blit(player_times[0][0], player_times[0][1])
    screen.blit(player_times[1][0], player_times[1][1])
    screen.blit(texts[2][0], texts[2][1])
    screen.blit(texts[3][0], texts[3][1])

    # Wyświetlanie tekstu o szachu
    if in_check:
        screen.blit(check_text, (8 * SQUARE_SIZE + 10, 150))

    # Dodaj wyświetlanie informacji dla trybu nerd
    if nerd_view:
        small_font = pygame.font.Font(None, 28)
        
        # Wyświetl evaluation jeśli dostępne
        if evaluation is not None:
            # Evaluation dla białych (dodatni = przewaga białych)
            eval_color_white = pygame.Color("green") if evaluation > 0 else pygame.Color("red")
            eval_text_white = small_font.render(f"Eval (white): +{evaluation:.2f}" if evaluation > 0 
                                              else f"Eval (white): {evaluation:.2f}", True, eval_color_white)
            screen.blit(eval_text_white, (8 * SQUARE_SIZE + 10, SQUARE_SIZE * 4))

            # Evaluation dla czarnych (odwrotność białych)
            black_eval = -evaluation
            eval_color_black = pygame.Color("green") if black_eval > 0 else pygame.Color("red")
            eval_text_black = small_font.render(f"Eval (black): +{black_eval:.2f}" if black_eval > 0 
                                              else f"Eval (black): {black_eval:.2f}", True, eval_color_black)
            screen.blit(eval_text_black, (8 * SQUARE_SIZE + 10, SQUARE_SIZE * 4.3))

        # Wyświetl ping jeśli dostępny
        if ping is not None:
            ping_color = pygame.Color("white")
            if ping > 200:  # Wysoki ping
                ping_color = pygame.Color("red")
            elif ping > 100:  # Średni ping
                ping_color = pygame.Color("yellow")
            ping_text = small_font.render(f"Ping: {ping}ms", True, ping_color)
            screen.blit(ping_text, (8 * SQUARE_SIZE + 10, SQUARE_SIZE * 6.6))

def format_time(seconds):
    """
    Formatuje czas gry na minuty i sekundy.

    Args:
        seconds (float): Czas w sekundach.

    Returns:
        str: Sformatowany czas w formacie "MM:SS".
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02}"

def promotion_dialog(screen, SQUARE_SIZE: int, color: str) -> str:
    """
    Wyświetla okno dialogowe do wyboru figury przy promocji pionka.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        color (str): Kolor gracza ('w' dla białych, 'b' dla czarnych).

    Returns:
        str: Wybrana figura ('1' dla skoczka, '2' dla gońca, '3' dla wieży, '4' dla królowej).
    """
    font = pygame.font.Font(None, 36)

    dialog_text = "Pionek dotarł do końca planszy. Wybierz figurę do odzyskania."
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    options = ["1. Koń", "2. Goniec", "3. Wieża", "4. Królowa"]
    option_rects = []
    for i, option in enumerate(options):
        text = font.render(option, True, pygame.Color("white"))
        rect = text.get_rect(center=(SQUARE_SIZE*4, SQUARE_SIZE*(2+i)))
        option_rects.append((text, rect))
    
    while True:
        screen.fill(pygame.Color("black"))
        screen.blit(dialog, (100, 100))
        mouse_pos = pygame.mouse.get_pos()
        for i, (text, rect) in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, pygame.Color("yellow"), rect.inflate(10, 10), 2)
            screen.blit(text, rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, (text, rect) in enumerate(option_rects):
                    if rect.collidepoint(pos):
                        return options[i][0]  # Zwraca pierwszą literę opcji (1, 2, 3, 4)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return '1'
                elif event.key == pygame.K_2:
                    return '2'
                elif event.key == pygame.K_3:
                    return '3'
                elif event.key == pygame.K_4:
                    return '4'

def end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK):
    """
    Wyświetla ekran końcowy z wynikami gry.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        result (str): Wynik gry (np. "Szach Mat!", "Pat").
        winner (str): Zwycięzca gry.
        white_time (float): Czas gry białego gracza.
        black_time (float): Czas gry czarnego gracza.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        width (int): Szerokość ekranu.
        height (int): Wysokość ekranu.
        WHITE (tuple): Kolor tekstu.
        BLACK (tuple): Kolor tła.
    """
    font = pygame.font.Font(None, 36)
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, 0, 200, SQUARE_SIZE*8))
    result_text = font.render(result, True, WHITE)
    winner_text = font.render(f"Zwycięzca: {winner}", True, WHITE)
    white_time_label = font.render("Czas białego gracza:", True, WHITE)
    white_time_value = font.render(format_time(white_time), True, WHITE)
    black_time_label = font.render("Czas czarnego gracza:", True, WHITE)
    black_time_value = font.render(format_time(black_time), True, WHITE)
    exit_text = font.render("Wyjście do menu", True, pygame.Color("yellow"))
    screen.blit(result_text, (SQUARE_SIZE*8+10, SQUARE_SIZE*2))
    screen.blit(winner_text, (SQUARE_SIZE*8+10, SQUARE_SIZE*3))
    screen.blit(white_time_label, (SQUARE_SIZE*8+10, SQUARE_SIZE*4))
    screen.blit(white_time_value, (SQUARE_SIZE*8+10, SQUARE_SIZE*4+30))
    screen.blit(black_time_label, (SQUARE_SIZE*8+10, SQUARE_SIZE*5))
    screen.blit(black_time_value, (SQUARE_SIZE*8+10, SQUARE_SIZE*5+30))
    screen.blit(exit_text, (8*SQUARE_SIZE+10, height-50))
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[0] > SQUARE_SIZE*8 and pos[1] >= height-80:
                    return


def confirm_undo_dialog(screen, SQUARE_SIZE: int) -> bool:
    """
    Wyświetla okno dialogowe z pytaniem, czy użytkownik zgadza się na cofnięcie ruchu.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.

    Returns:
        bool: True, jeśli użytkownik zaakceptuje cofnięcie ruchu, False w przeciwnym razie.
    """
    font = pygame.font.Font(None, 36)

    # Tekst pytania
    dialog_text = "Czy zgadzasz się na cofnięcie ruchu?"
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje
    options = ["Tak", "Nie"]
    option_rects = []
    for i, option in enumerate(options):
        text = font.render(option, True, pygame.Color("white"))
        rect = text.getRect(center=(SQUARE_SIZE * 4, SQUARE_SIZE * (3 + i)))
        option_rects.append((text, rect))

    while True:
        screen.fill(pygame.Color("black"))
        screen.blit(dialog, (SQUARE_SIZE * 2, SQUARE_SIZE * 2))
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for i, (text, rect) in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, pygame.Color("yellow"), rect.inflate(10, 10), 2)
            screen.blit(text, rect)

        pygame.display.flip()

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, (text, rect) in enumerate(option_rects):
                    if rect.collidepoint(pos):
                        return i == 0  # Zwraca True dla "Tak" (pierwsza opcja), False dla "Nie" (druga opcja)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:  # Klawisz "Y" dla "Tak"
                    return True
                elif event.key == pygame.K_n:  # Klawisz "N" dla "Nie"
                    return False

def choose_color_dialog(screen, SQUARE_SIZE: int) -> str:
    """
    Wyświetla okno dialogowe z pytaniem, jaki kolor gry wybiera użytkownik.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.

    Returns:
        str: 'w' dla białego, 'b' dla czarnego.
    """
    font = pygame.font.Font(None, 36)

    # Tekst pytania
    dialog_text = "Wybierz kolor gry:"
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje kolorów
    options = [("Biały", pygame.Color("white"), 'w'), ("Czarny", pygame.Color("black"), 'b')]
    option_rects = []
    for i, (label, color, _) in enumerate(options):
        rect = pygame.Rect(SQUARE_SIZE * 3, SQUARE_SIZE * (3 + i), SQUARE_SIZE * 2, SQUARE_SIZE)
        option_rects.append((label, color, rect))

    while True:
        screen.fill(pygame.Color("gray"))
        screen.blit(dialog, (SQUARE_SIZE * 2, SQUARE_SIZE * 2))
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for label, color, rect in option_rects:
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, pygame.Color("yellow"), rect, 3)  # Obrys
            text = font.render(label, True, pygame.Color("black") if color == pygame.Color("white") else pygame.Color("white"))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for label, color, rect in option_rects:
                    if rect.collidepoint(pos):
                        return 'w' if color == pygame.Color("white") else 'b'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:  # Klawisz "W" dla białego
                    return 'w'
                elif event.key == pygame.K_b:  # Klawisz "B" dla czarnego
                    return 'b'

def choose_algorithm_dialog(screen, SQUARE_SIZE: int) -> str:
    """
    Wyświetla okno dialogowe z pytaniem, jaki algorytm gry wybiera użytkownik.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.

    Returns:
        str: 'minimax' dla algorytmu Minimax, 'monte_carlo' dla Monte Carlo.
    """
    font = pygame.font.Font(None, 36)

    # Tekst pytania
    dialog_text = "Wybierz algorytm gry:"
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje algorytmów
    options = [("Minimax", pygame.Color("blue"), 'minimax'), ("Monte Carlo", pygame.Color("green"), 'monte_carlo')]
    option_rects = []
    for i, (label, color, _) in enumerate(options):
        rect = pygame.Rect(SQUARE_SIZE * 3, SQUARE_SIZE * (3 + i), SQUARE_SIZE * 4, SQUARE_SIZE)
        option_rects.append((label, color, rect))

    while True:
        screen.fill(pygame.Color("gray"))
        screen.blit(dialog, (SQUARE_SIZE * 2, SQUARE_SIZE * 2))
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for label, color, rect in option_rects:
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, pygame.Color("yellow"), rect, 3)  # Obrys
            text = font.render(label, True, pygame.Color("white"))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for label, color, rect in option_rects:
                    if rect.collidepoint(pos):
                        return 'minimax' if label == "Minimax" else 'monte_carlo'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # Klawisz "M" dla Minimax
                    return 'minimax'
                elif event.key == pygame.K_c:  # Klawisz "C" dla Monte Carlo
                    return 'monte_carlo'

def choose_grandmaster_dialog(screen, SQUARE_SIZE: int) -> str:
    """
    Wyświetla dialog wyboru arcymistrza z portretami lub wyborem pliku.
    """
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    # Lista predefiniowanych arcymistrzów
    grandmasters = [
        "kasparov", "fischer", "carlsen", "hikaru", 
        "capablanca", "mikhail", "morphy paul", "alekhine",
        "viswanathan", "polgar", "botvinnik", "caruana"
    ]
    
    # Stałe do pozycjonowania
    PORTRAIT_SIZE = int(SQUARE_SIZE * 1.8)
    GRID_START_X = (1260 - (4 * PORTRAIT_SIZE + 3 * 40)) // 2
    GRID_START_Y = 150
    SPACING = 40
    
    # Przycisk "Wybierz plik"
    BUTTON_WIDTH = 400
    BUTTON_HEIGHT = 80
    button_rect = pygame.Rect(
        (1260 - BUTTON_WIDTH) // 2,
        850,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    
    # Ładowanie portretów
    portraits = {}
    portrait_rects = {}
    for gm in grandmasters:
        try:
            portrait = pygame.image.load(f"grandmaster/portraits/{gm.lower()}.png")
            portrait = pygame.transform.scale(portrait, (PORTRAIT_SIZE, PORTRAIT_SIZE))
            portraits[gm] = portrait
        except:
            placeholder = pygame.Surface((PORTRAIT_SIZE, PORTRAIT_SIZE))
            placeholder.fill(pygame.Color("gray40"))
            name_text = small_font.render(gm, True, pygame.Color("white"))
            name_rect = name_text.get_rect(center=(PORTRAIT_SIZE//2, PORTRAIT_SIZE//2))
            placeholder.blit(name_text, name_rect)
            portraits[gm] = placeholder

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Tytuł
        title_text = font.render("Wybierz Arcymistrza", True, pygame.Color("gold"))
        title_rect = title_text.get_rect(center=(1260 // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Rysowanie portretów
        mouse_pos = pygame.mouse.get_pos()
        for i, gm in enumerate(grandmasters):
            row = i // 4
            col = i % 4
            x = GRID_START_X + col * (PORTRAIT_SIZE + SPACING)
            y = GRID_START_Y + row * (PORTRAIT_SIZE + SPACING)
            
            portrait_rect = portraits[gm].get_rect(topleft=(x, y))
            portrait_rects[gm] = portrait_rect
            
            if portrait_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, pygame.Color("gold"), portrait_rect.inflate(6, 6), 3)
            
            screen.blit(portraits[gm], portrait_rect)
            name_text = small_font.render(gm.title(), True, pygame.Color("white"))
            name_rect = name_text.get_rect(center=(x + PORTRAIT_SIZE//2, y + PORTRAIT_SIZE + 25))
            screen.blit(name_text, name_rect)
        
        # Przycisk "Wybierz własny plik"
        if button_rect.collidepoint(mouse_pos):
            color = pygame.Color("gold")
        else:
            color = pygame.Color("white")
        pygame.draw.rect(screen, color, button_rect, 3)
        button_text = font.render("Wybierz własny plik", True, color)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Sprawdzenie kliknięcia na portrety
                for gm, rect in portrait_rects.items():
                    if rect.collidepoint(event.pos):
                        return gm.lower()
                
                # Sprawdzenie kliknięcia na przycisk
                if button_rect.collidepoint(event.pos):
                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.askopenfilename(
                        initialdir="grandmaster/json/",
                        title="Wybierz plik JSON z ruchami arcymistrza",
                        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
                    )
                    if file_path:
                        return Path(file_path).stem
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

def choose_custom_board_mode(screen, SQUARE_SIZE: int) -> str:
    """
    Wyświetla dialog wyboru trybu dla niestandardowej planszy.
    
    Args:
        screen (pygame.Surface): Powierzchnia ekranu
        SQUARE_SIZE (int): Rozmiar pojedynczego pola
        
    Returns:
        str: 'play' dla gry z własną planszą lub 'create' dla kreatora planszy
    """
    font = pygame.font.Font(None, 74)
    clock = pygame.time.Clock()
    
    # Opcje
    options = ["Graj z własną planszą", "Kreator planszy"]
    selected = None
    
    # Przyciski
    button_width = 600
    button_height = 100
    button_spacing = 50
    
    buttons = []
    for i, text in enumerate(options):
        x = (1260 - button_width) // 2
        y = 300 + i * (button_height + button_spacing)
        buttons.append(pygame.Rect(x, y, button_width, button_height))

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Tytuł
        title = font.render("Wybierz tryb", True, pygame.Color("gold"))
        title_rect = title.get_rect(center=(1260 // 2, 150))
        screen.blit(title, title_rect)
        
        # Rysowanie przycisków
        mouse_pos = pygame.mouse.get_pos()
        for i, (button, text) in enumerate(zip(buttons, options)):
            color = pygame.Color("gold") if button.collidepoint(mouse_pos) else pygame.Color("white")
            pygame.draw.rect(screen, color, button, 3)
            
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=button.center)
            screen.blit(text_surf, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.collidepoint(event.pos):
                        return "play" if i == 0 else "create"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

def choose_pgn_file_dialog(screen, SQUARE_SIZE: int) -> str:
    """
    Opens system's native file dialog to select a PGN file.
    Returns the filename without extension.
    """
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Open the file dialog
    file_path = filedialog.askopenfilename(
        initialdir="grandmaster/pgn/",
        title="Wybierz plik PGN",
        filetypes=(("PGN files", "*.pgn"), ("All files", "*.*"))
    )
    
    if file_path:
        # Extract filename without extension and directory path
        filename = Path(file_path).stem
        # Check if file exists in the correct directory
        if Path(f"grandmaster/pgn/{filename}.pgn").exists():
            return filename
        else:
            # Show error message on pygame screen
            font = pygame.font.Font(None, 48)
            error_text = font.render("Plik musi być w katalogu grandmaster/pgn/", True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            
            screen.fill((32, 32, 32))
            screen.blit(error_text, error_rect)
            pygame.display.flip()
            
            # Wait for a moment
            pygame.time.wait(2000)
            
    return None