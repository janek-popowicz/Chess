"""
Moduł zawiera funkcje odpowiedzialne za grafikę i interfejs użytkownika w grze szachowej.

Funkcje te obejmują rysowanie szachownicy, figur, podświetlanie możliwych ruchów, wyświetlanie interfejsu oraz obsługę okien dialogowych.
"""

import pygame
import json
import sys

CONFIG_FILE = "config.json"

def load_config():
    """
    Ładuje konfigurację gry z pliku JSON.

    Returns:
        dict: Słownik zawierający ustawienia gry (np. głośność, rozdzielczość, ikony, podświetlanie).
    """
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960", "icons": "classic", "highlight": 0}

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

def draw_pieces(screen, board, SQUARE_SIZE, pieces):
    """
    Rysuje figury na szachownicy.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        board (Board): Obiekt planszy szachowej.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        pieces (dict): Słownik zawierający obrazy figur.
    """
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece != "--":
                screen.blit(pieces[piece], pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlight_moves(screen, field, square_size: int, board, color_move, color_take, highlight):
    """
    Podświetla możliwe ruchy dla wybranej figury.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        field (Field): Pole, na którym znajduje się wybrana figura.
        square_size (int): Rozmiar pojedynczego pola na szachownicy.
        board (Board): Obiekt planszy szachowej.
        color_move (tuple): Kolor podświetlenia dla możliwych ruchów.
        color_take (tuple): Kolor podświetlenia dla możliwych bić.
    """
    try:
        cords = board.get_legal_moves(field, field.figure.color)
    except AttributeError:
        return None
    if highlight or field.figure:
        for cord in cords:
            highlighted_tile = pygame.Surface((square_size, square_size))
            highlighted_tile.fill(color_move)
            if board.board_state[cord[0]][cord[1]].figure:
                if field.figure.color != board.board_state[cord[0]][cord[1]].figure.color:
                    highlighted_tile.fill(color_take)
            if field.figure.type == 'p' and (field.x - cord[1]) != 0:
                highlighted_tile.fill(color_take)
            screen.blit(highlighted_tile, (((7-cord[1]) * square_size), ((7-cord[0]) * square_size)))

def draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times, in_check, check_text):
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
    """
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, 0, 200, SQUARE_SIZE*8))
    if turn == 'w':
        screen.blit(texts[0][0], texts[0][1])
    else:
        screen.blit(texts[1][0], texts[1][1])
    screen.blit(player_times[0][0], player_times[0][1])
    screen.blit(player_times[1][0], player_times[1][1])
    screen.blit(texts[2][0], texts[2][1])
    if in_check:
        screen.blit(check_text, (8*SQUARE_SIZE+10, 150))

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