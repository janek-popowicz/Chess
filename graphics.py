"""
Moduł zawiera funkcje odpowiedzialne za grafikę i interfejs użytkownika w grze szachowej.

Funkcje te obejmują rysowanie szachownicy, figur, podświetlanie możliwych ruchów, wyświetlanie interfejsu oraz obsługę okien dialogowych.
"""

import pygame
import json
import sys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from language import global_translations  # Import tłumaczeń

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
        # Domyślne ustawienia w przypadku braku pliku konfiguracyjnego
        return {
            "volume": 0.5, 
            "resolution": "1260x960", 
            "icons": "classic", 
            "highlight": 0,
            "nerd_view": False  # Domyślne ustawienie trybu nerd_view
        }

def draw_board(screen, SQUARE_SIZE, main_board, in_check, is_reversed=False):
    """
    Rysuje szachownicę na ekranie.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        main_board (Board): Obiekt planszy szachowej.
        in_check (str): Kolor gracza, którego król jest szachowany ('w' lub 'b').
        is_reversed (bool, optional): Czy plansza ma być odwrócona. Defaults to False.
    """
    colors = [pygame.Color("white"), pygame.Color("gray")]
    coord_font = pygame.font.Font(None, 34)  # Smaller font for coordinates
    
    # Draw squares
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            if in_check and main_board.board_state[r][c].figure and main_board.board_state[r][c].figure.type == 'K' and main_board.board_state[r][c].figure.color == in_check:
                color = pygame.Color("red")
                
            if is_reversed:
                x = c * SQUARE_SIZE
                y = r * SQUARE_SIZE
            else:
                x = (7-c) * SQUARE_SIZE
                y = (7-r) * SQUARE_SIZE
                
            pygame.draw.rect(screen, color, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))
            
            # Draw coordinates in the corners of border squares
            coord_color = colors[(r + c + 1) % 2]  # Opposite color of square
            
            # Numbers (1-8) on leftmost squares
            numbers = ("1", "2", "3", "4", "5", "6", "7", "8")
            letters = ("a", "b", "c", "d", "e", "f", "g", "h")
            if (c == 0 and is_reversed) or (c == 7 and not is_reversed):
                number = numbers[r] if is_reversed else numbers[r]  # '1' through '8'
                num_surf = coord_font.render(number, True, coord_color)
                screen.blit(num_surf, (x + 1, y + 1))
            
            # Letters (a-h) on bottom squares
            if (r == 7 and is_reversed) or (r == 0 and not is_reversed):
                letter = letters[7-c] if is_reversed else letters[7-c]  # 'a' through 'h'
                let_surf = coord_font.render(letter, True, coord_color)
                screen.blit(let_surf, (x + SQUARE_SIZE - 25, y + SQUARE_SIZE - 30))

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

def draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times, in_check, check_text, nerd_view=False, ping=None):
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
        ping (int, optional): Ping w ms. Defaults to None.
    """
    # Czarny prostokąt z prawej - tło
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE * 8, 0, 200, SQUARE_SIZE * 8))
    # teksty tur graczy
    if turn == 'w':
        screen.blit(texts[0][0], texts[0][1])
    else:
        screen.blit(texts[1][0], texts[1][1])

    # czasy graczy
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
    font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)

    # Tekst pytania
    dialog_text = global_translations.get("promotion_dialog_text")
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje figur
    options = [
        ("1. " + global_translations.get("knight"), pygame.Color("blue")),
        ("2. " + global_translations.get("bishop"), pygame.Color("green")),
        ("3. " + global_translations.get("rook"), pygame.Color("purple")),
        ("4. " + global_translations.get("queen"), pygame.Color("gold"))
    ]
    button_width = SQUARE_SIZE * 2
    button_height = SQUARE_SIZE * 2
    spacing = SQUARE_SIZE // 2
    total_width = len(options) * button_width + (len(options) - 1) * spacing
    start_x = (screen.get_width() - total_width) // 2
    start_y = (screen.get_height() - button_height) // 2

    option_rects = []
    for i, (label, color) in enumerate(options):
        rect = pygame.Rect(start_x + i * (button_width + spacing), start_y, button_width, button_height)
        option_rects.append((label, color, rect))

    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)
    last_hovered = None

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Wyśrodkowanie napisu "Wybierz figurę do promocji"
        dialog_x = screen.get_width() // 2 - dialog.get_width() // 2
        dialog_y = start_y - SQUARE_SIZE * 2
        screen.blit(dialog, (dialog_x, dialog_y))
        
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for label, color, rect in option_rects:
            if rect.collidepoint(mouse_pos):
                if last_hovered != rect:
                    menu_cursor_sound.play()
                    last_hovered = rect
                pygame.draw.rect(screen, pygame.Color("yellow"), rect.inflate(10, 10), border_radius=15)
            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, pygame.Color("yellow"), rect, 3, border_radius=15)  # Obrys
            text = button_font.render(label, True, pygame.Color("black"))
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
                for label, _, rect in option_rects:
                    if rect.collidepoint(pos):
                        return label[0]  # Zwraca pierwszą literę opcji (1, 2, 3, 4)
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
    winner_text = font.render(f"{global_translations.get('winner')}: {winner}", True, WHITE)
    white_time_label = font.render(global_translations.get("white_time_label"), True, WHITE)
    white_time_value = font.render(format_time(white_time), True, WHITE)
    black_time_label = font.render(global_translations.get("black_time_label"), True, WHITE)
    black_time_value = font.render(format_time(black_time), True, WHITE)
    exit_text = font.render(global_translations.get("exit_to_menu"), True, pygame.Color("yellow"))
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
    dialog_text = global_translations.get("confirm_undo_text")
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje
    options = [global_translations.get("yes"), global_translations.get("no")]
    option_rects = []
    for i, option in enumerate(options):
        text = font.render(option, True, pygame.Color("white"))
        rect = text.get_rect(center=(SQUARE_SIZE * 4, SQUARE_SIZE * (3 + i)))
        option_rects.append((text, rect))

    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)
    last_hovered = None

    while True:
        screen.fill(pygame.Color("black"))
        screen.blit(dialog, (SQUARE_SIZE * 2, SQUARE_SIZE * 2))
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for i, (text, rect) in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                if last_hovered != rect:
                    menu_cursor_sound.play()
                    last_hovered = rect
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
    font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)

    # Tekst pytania
    dialog_text = global_translations.get("choose_color_text")
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje kolorów
    options = [
        (global_translations.get("white"), pygame.Color("white"), 'w'),
        (global_translations.get("black"), pygame.Color("black"), 'b'),
        (global_translations.get("cancel"), pygame.Color("red"), None)  # Add "Cancel" option
    ]
    button_width = SQUARE_SIZE * 2
    button_height = SQUARE_SIZE * 2
    spacing = SQUARE_SIZE // 2  # Reduce spacing to fit within the window
    total_width = len(options) * button_width + (len(options) - 1) * spacing
    start_x = max(0, (screen.get_width() - total_width) // 2)  # Ensure buttons don't go off-screen
    start_y = max(0, (screen.get_height() - button_height) // 2)  # Ensure buttons fit vertically

    option_rects = []
    for i, (label, color, _) in enumerate(options):
        rect = pygame.Rect(start_x + i * (button_width + spacing), start_y, button_width, button_height)
        option_rects.append((label, color, rect))

    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)  # Adjust volume as needed
    last_hovered = None  # Track the last hovered option

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Wyśrodkowanie napisu "Wybierz kolor gry"
        dialog_x = screen.get_width() // 2 - dialog.get_width() // 2
        dialog_y = start_y - SQUARE_SIZE * 2
        screen.blit(dialog, (dialog_x, dialog_y))
        
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for label, color, rect in option_rects:
            if rect.collidepoint(mouse_pos):
                if last_hovered != rect:  # Play sound only when hovering over a new option
                    menu_cursor_sound.play()
                    last_hovered = rect
                pygame.draw.rect(screen, pygame.Color("yellow"), rect.inflate(10, 10), border_radius=15)
            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, pygame.Color("yellow"), rect, 3, border_radius=15)  # Obrys
            text = button_font.render(label, True, pygame.Color("black") if color == pygame.Color("white") else pygame.Color("white"))
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
                        if label == "Anuluj":  # Handle "Cancel" option
                            return None
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
        str: 'minimax' dla algorytmu Minimax, 'monte_carlo' dla Monte Carlo, 'neural' dla sieci neuronowej.
    """
    font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)

    # Tekst pytania
    dialog_text = global_translations.get("choose_algorithm_text")
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    # Opcje algorytmów
    options = [
        (global_translations.get("minimax"), pygame.Color("blue"), 'minimax'),
        (global_translations.get("monte_carlo"), pygame.Color("green"), 'monte_carlo')
    ]
    
    # Dostosowanie wielkości i pozycji przycisków
    button_width = SQUARE_SIZE * 3
    button_height = SQUARE_SIZE * 2
    spacing = SQUARE_SIZE // 2
    total_width = len(options) * button_width + (len(options) - 1) * spacing
    start_x = (screen.get_width() - total_width) // 2
    start_y = (screen.get_height() - button_height) // 2

    option_rects = []
    for i, (label, color, _) in enumerate(options):
        rect = pygame.Rect(start_x + i * (button_width + spacing), start_y, button_width, button_height)
        option_rects.append((label, color, rect))

    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)
    last_hovered = None

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Wyśrodkowanie napisu "Wybierz algorytm gry"
        dialog_x = screen.get_width() // 2 - dialog.get_width() // 2
        dialog_y = start_y - SQUARE_SIZE * 2
        screen.blit(dialog, (dialog_x, dialog_y))
        
        mouse_pos = pygame.mouse.get_pos()

        # Rysowanie opcji
        for label, color, rect in option_rects:
            if rect.collidepoint(mouse_pos):
                if last_hovered != rect:
                    menu_cursor_sound.play()
                    last_hovered = rect
                pygame.draw.rect(screen, pygame.Color("yellow"), rect.inflate(10, 10), border_radius=15)
            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, pygame.Color("yellow"), rect, 3, border_radius=15)  # Obrys
            text = button_font.render(label, True, pygame.Color("white"))
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
                for label, color, algo_type in options:
                    if option_rects[options.index((label, color, algo_type))][2].collidepoint(pos):
                        return algo_type
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # Klawisz "M" dla Minimax
                    return 'minimax'
                elif event.key == pygame.K_c:  # Klawisz "C" dla Monte Carlo
                    return 'monte_carlo'
                elif event.key == pygame.K_n:  # Klawisz "N" dla Neural Network
                    return 'neural'

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

    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)
    last_hovered = None

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Tytuł
        title_text = font.render(global_translations.get("choose_grandmaster_title"), True, pygame.Color("gold"))
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
                if last_hovered != portrait_rect:  # Poprawka: użycie portrait_rect zamiast rect
                    menu_cursor_sound.play()
                    last_hovered = portrait_rect
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
        button_text = font.render(global_translations.get("choose_custom_file"), True, color)
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
    options = [
        global_translations.get("play_custom_board"),
        global_translations.get("create_custom_board")
    ]
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

    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)
    last_hovered = None

    while True:
        screen.fill(pygame.Color("gray20"))
        
        # Tytuł
        title = font.render(global_translations.get("choose_custom_board_mode_title"), True, pygame.Color("gold"))
        title_rect = title.get_rect(center=(1260 // 2, 150))
        screen.blit(title, title_rect)
        
        # Rysowanie przycisków
        mouse_pos = pygame.mouse.get_pos()
        for i, (button, text) in enumerate(zip(buttons, options)):
            if button.collidepoint(mouse_pos):
                if last_hovered != button:
                    menu_cursor_sound.play()
                    last_hovered = button
                color = pygame.Color("gold")
            else:
                color = pygame.Color("white")
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

def choose_ai_settings_dialog(screen, SQUARE_SIZE: int, min_depth=1, max_depth=5) -> tuple:
    """
    Shows a dialog with sliders to configure AI settings.
    
    Args:
        screen (pygame.Surface): Game screen surface
        SQUARE_SIZE (int): Size of a board square
        min_depth (int): Minimum depth value
        max_depth (int): Maximum depth value
        
    Returns:
        tuple: (depth, min_time, max_time) or None if canceled
    """
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    # Settings and their ranges
    settings = {
        "Głębokość przeszukiwania": {
            "value": (min_depth + max_depth) // 2,
            "min": min_depth,
            "max": max_depth,
            "step": 1
        },
        "Minimalny czas (s)": {
            "value": 1,
            "min": 0,
            "max": 5,
            "step": 0.1
        },
        "Maksymalny czas (s)": {
            "value": 3,
            "min": 1,
            "max": 30,
            "step": 0.5
        }
    }

    # Slider properties
    SLIDER_WIDTH = 400
    SLIDER_HEIGHT = 8
    HANDLE_SIZE = 20
    SPACING = 100

    # Button properties
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 60
    
    # Calculate positions
    start_y = 200
    sliders = {}
    for i, key in enumerate(settings.keys()):
        slider_x = (screen.get_width() - SLIDER_WIDTH) // 2
        slider_y = start_y + i * SPACING
        sliders[key] = {
            "rect": pygame.Rect(slider_x, slider_y, SLIDER_WIDTH, SLIDER_HEIGHT),
            "handle": pygame.Rect(
                slider_x + (settings[key]["value"] - settings[key]["min"]) / 
                (settings[key]["max"] - settings[key]["min"]) * SLIDER_WIDTH - HANDLE_SIZE//2,
                slider_y - HANDLE_SIZE//2 + SLIDER_HEIGHT//2,
                HANDLE_SIZE, HANDLE_SIZE
            )
        }

    # Create buttons
    buttons = {
        "Zatwierdź": pygame.Rect((screen.get_width() - BUTTON_WIDTH*2 - 20)//2, 
                                start_y + len(settings) * SPACING + 50,
                                BUTTON_WIDTH, BUTTON_HEIGHT),
        "Anuluj": pygame.Rect((screen.get_width() + 20)//2, 
                             start_y + len(settings) * SPACING + 50,
                             BUTTON_WIDTH, BUTTON_HEIGHT)
    }

    active_slider = None
    while True:
        screen.fill(pygame.Color("gray20"))
        mouse_pos = pygame.mouse.get_pos()

        # Draw title
        title = font.render("Ustawienia AI", True, pygame.Color("gold"))
        title_rect = title.get_rect(center=(screen.get_width()//2, 100))
        screen.blit(title, title_rect)

        # Draw sliders
        for name, slider in sliders.items():
            # Draw slider background
            pygame.draw.rect(screen, pygame.Color("gray40"), slider["rect"])
            pygame.draw.rect(screen, pygame.Color("gray60"), slider["rect"], 1)
            
            # Draw handle
            handle_color = pygame.Color("gold") if slider["handle"].collidepoint(mouse_pos) else pygame.Color("white")
            pygame.draw.circle(screen, handle_color, slider["handle"].center, HANDLE_SIZE//2)
            
            # Draw labels and values
            label = small_font.render(name, True, pygame.Color("white"))
            screen.blit(label, (slider["rect"].x, slider["rect"].y - 30))
            
            # Calculate and display value
            value_range = settings[name]["max"] - settings[name]["min"]
            relative_pos = (slider["handle"].centerx - slider["rect"].x) / SLIDER_WIDTH
            value = settings[name]["min"] + relative_pos * value_range
            value = round(value / settings[name]["step"]) * settings[name]["step"]
            settings[name]["value"] = value
            
            value_text = small_font.render(f"{value:.1f}", True, pygame.Color("white"))
            screen.blit(value_text, (slider["rect"].right + 20, slider["rect"].y - 5))

        # Draw buttons
        for text, rect in buttons.items():
            color = pygame.Color("gold") if rect.collidepoint(mouse_pos) else pygame.Color("white")
            pygame.draw.rect(screen, color, rect, 3)
            button_text = small_font.render(text, True, color)
            text_rect = button_text.get_rect(center=rect.center)
            screen.blit(button_text, text_rect)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check slider handles
                for slider in sliders.values():
                    if slider["handle"].collidepoint(event.pos):
                        active_slider = slider
                        break
                
                # Check buttons
                if buttons["Zatwierdź"].collidepoint(event.pos):
                    return (
                        int(settings["Głębokość przeszukiwania"]["value"]),
                        settings["Minimalny czas (s)"]["value"],
                        settings["Maksymalny czas (s)"]["value"]
                    )
                elif buttons["Anuluj"].collidepoint(event.pos):
                    return None
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                active_slider = None
                
            elif event.type == pygame.MOUSEMOTION and active_slider:
                # Update slider handle position
                new_x = min(max(event.pos[0], active_slider["rect"].left), active_slider["rect"].right)
                active_slider["handle"].centerx = new_x
                
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

def choose_time_control_dialog(screen, SQUARE_SIZE: int) -> int:
    """
    Displays a dialog for selecting game time control.
    
    Args:
        screen (pygame.Surface): Game screen surface
        SQUARE_SIZE (int): Size of a board square
        
    Returns:
        int: Selected time in minutes or None if canceled
    """
    font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)

    # Time options in minutes
    time_options = [1, 2, 3, 5, 10, 30, 60]
    
    # Button properties
    BUTTON_WIDTH = SQUARE_SIZE * 2
    BUTTON_HEIGHT = SQUARE_SIZE
    BUTTONS_PER_ROW = 4
    SPACING_X = SQUARE_SIZE // 2
    SPACING_Y = SQUARE_SIZE // 2

    # Calculate layout
    total_width = min(BUTTONS_PER_ROW, len(time_options)) * (BUTTON_WIDTH + SPACING_X) - SPACING_X
    total_rows = (len(time_options) + BUTTONS_PER_ROW - 1) // BUTTONS_PER_ROW
    start_x = (screen.get_width() - total_width) // 2
    start_y = (screen.get_height() - (total_rows * (BUTTON_HEIGHT + SPACING_Y) - SPACING_Y)) // 2

    # Create buttons
    buttons = []
    for i, minutes in enumerate(time_options):
        row = i // BUTTONS_PER_ROW
        col = i % BUTTONS_PER_ROW
        x = start_x + col * (BUTTON_WIDTH + SPACING_X)
        y = start_y + row * (BUTTON_HEIGHT + SPACING_Y)
        buttons.append((
            pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT),
            minutes
        ))

    # Sound effect
    menu_cursor_sound = pygame.mixer.Sound(global_translations.get("menu_cursor_sound_path"))
    menu_cursor_sound.set_volume(0.5)
    last_hovered = None

    while True:
        screen.fill(pygame.Color("gray20"))
        mouse_pos = pygame.mouse.get_pos()

        # Draw title
        title = font.render(global_translations.get("choose_time_control_title"), True, pygame.Color("gold"))
        title_rect = title.get_rect(center=(screen.get_width()//2, start_y - 80))
        screen.blit(title, title_rect)

        # Draw time buttons
        for button, minutes in buttons:
            # Handle hover effect
            if button.collidepoint(mouse_pos):
                if last_hovered != button:
                    menu_cursor_sound.play()
                    last_hovered = button
                pygame.draw.rect(screen, pygame.Color("gold"), button.inflate(10, 10), border_radius=15)
            
            # Draw button background
            pygame.draw.rect(screen, pygame.Color("gray40"), button, border_radius=15)
            pygame.draw.rect(screen, pygame.Color("gold"), button, 3, border_radius=15)
            
            # Draw time text
            if minutes >= 60:
                text = f"{minutes//60}{global_translations.get('hours_suffix')}"
            else:
                text = f"{minutes}{global_translations.get('minutes_suffix')}"
            
            time_text = button_font.render(text, True, pygame.Color("white"))
            text_rect = time_text.get_rect(center=button.center)
            screen.blit(time_text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, minutes in buttons:
                    if button.collidepoint(event.pos):
                        return float(minutes * 60)  # Return time in seconds
                        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                # Number keys 1-7 for quick selection
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                    index = event.key - pygame.K_1
                    if index < len(time_options):
                        return time_options[index] * 60

def show_error_dialog(screen, message: str, SQUARE_SIZE: int) -> None:
    """
    Displays a modal error dialog with an OK button.
    
    Args:
        screen (pygame.Surface): Game screen surface
        message (str): Error message to display
        SQUARE_SIZE (int): Size of a board square for scaling
    """
    font = pygame.font.Font(None, 36)
    
    # Dialog box properties
    DIALOG_WIDTH = min(300 - 100, max(400, len(message) * 15))
    DIALOG_HEIGHT = 200
    dialog_rect = pygame.Rect(
        (screen.get_width() - DIALOG_WIDTH) // 2,
        (screen.get_height() - DIALOG_HEIGHT) // 2,
        DIALOG_WIDTH,
        DIALOG_HEIGHT
    )
    
    # OK button properties
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 40
    button_rect = pygame.Rect(
        (screen.get_width() - BUTTON_WIDTH) // 2,
        dialog_rect.bottom - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    
    # Error icon (X symbol)
    icon_size = 40
    icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    icon_color = pygame.Color("red")
    pygame.draw.circle(icon_surface, icon_color, (icon_size//2, icon_size//2), icon_size//2)
    pygame.draw.line(icon_surface, pygame.Color("white"), 
                    (12, 12), (icon_size-12, icon_size-12), 4)
    pygame.draw.line(icon_surface, pygame.Color("white"), 
                    (12, icon_size-12), (icon_size-12, 12), 4)
    
    # Sound effect
    menu_cursor_sound = pygame.mixer.Sound("sounds/menu_cursor.mp3")
    menu_cursor_sound.set_volume(0.5)
    error_sound = pygame.mixer.Sound("sounds/error.mp3")
    error_sound.play()
    
    last_hovered = False
    
    # Store the background
    background = screen.copy()
    
    while True:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        pygame.draw.rect(screen, pygame.Color("gray20"), dialog_rect)
        pygame.draw.rect(screen, pygame.Color("red"), dialog_rect, 3)
        
        # Draw error icon
        icon_pos = (dialog_rect.centerx - icon_size//2, dialog_rect.top + 20)
        screen.blit(icon_surface, icon_pos)
        
        # Draw error message
        text_surface = font.render(message, True, pygame.Color("white"))
        text_rect = text_surface.get_rect(
            center=(dialog_rect.centerx, dialog_rect.centery)
        )
        screen.blit(text_surface, text_rect)
        
        # Draw OK button
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = button_rect.collidepoint(mouse_pos)
        
        if button_hovered and not last_hovered:
            menu_cursor_sound.play()
        
        button_color = pygame.Color("gold") if button_hovered else pygame.Color("white")
        pygame.draw.rect(screen, pygame.Color("gray40"), button_rect, border_radius=5)
        pygame.draw.rect(screen, button_color, button_rect, 3, border_radius=5)
        
        ok_text = font.render("OK", True, button_color)
        ok_rect = ok_text.get_rect(center=button_rect.center)
        screen.blit(ok_text, ok_rect)
        
        last_hovered = button_hovered
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return