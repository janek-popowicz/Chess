import pygame
import json

# Importy modułów silnika i grafiki
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from engine.fen_operations import *
import interface.graphics as graphics

CONFIG_FILE = "config.json"

def load_config():
    """
    Ładuje konfigurację z pliku JSON.

    Returns:
        dict: Słownik z ustawieniami konfiguracji.
    """
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        # Domyślne ustawienia w przypadku braku pliku konfiguracyjnego
        return {"volume": 0.5, "resolution": "1260x960", "icons": "classic"}

def draw_board(screen, SQUARE_SIZE, board_state, pieces):
    """
    Rysuje szachownicę i figury na ekranie.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        board_state (list): Stan planszy (tablica pól).
        pieces (dict): Słownik z obrazami figur.
    """
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            # Rysowanie pól szachownicy
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board_state[r][c].figure
            if piece:
                # Rysowanie figur na planszy
                piece_key = f"{piece.color}{piece.type[0].upper() if piece.type != 'p' else piece.type}"
                piece_image = pieces[piece_key]
                screen.blit(piece_image, (c * SQUARE_SIZE + 5, r * SQUARE_SIZE + 5))

def draw_pieces_selection(screen, SQUARE_SIZE, pieces, config, selected_piece):
    """
    Rysuje panel wyboru figur.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.
        pieces (dict): Słownik z obrazami figur.
        config (dict): Konfiguracja gry.
        selected_piece (tuple): Aktualnie wybrana figura (kolor, typ).
    """
    icon_type = config["icons"]
    piece_types = ["R", "N", "B", "Q", "K", "p"]
    colors = ["w", "b"]
    for i, color in enumerate(colors):
        for j, piece_type in enumerate(piece_types):
            # Obliczanie pozycji figur w panelu wyboru
            piece_key = f"{color}{piece_type}"
            piece_image = pieces[piece_key]
            col = j % 2
            row = j // 2
            x = 8 * SQUARE_SIZE + col * (SQUARE_SIZE + 10)
            y = (i * 3 + row) * SQUARE_SIZE + 10
            # Podświetlenie wybranej figury
            if selected_piece == (color, piece_type):
                pygame.draw.rect(screen, pygame.Color("yellow"), pygame.Rect(x, y - 10, SQUARE_SIZE, SQUARE_SIZE), 3)
            screen.blit(piece_image, (x + 3, y - 3))

def main():
    """
    Główna funkcja programu do tworzenia niestandardowej szachownicy.
    """
    pygame.init()
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Custom Board Setup")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Kolory i czcionki
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    YELLOW = pygame.Color("yellow")
    RED = pygame.Color("red")
    font = pygame.font.Font(None, 36)

    # Ładowanie ikon figur
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    pieces = {piece: pygame.transform.scale(pygame.image.load(f"pieces/{icon_type}/{piece}.png"), (SQUARE_SIZE - 10, SQUARE_SIZE - 10)) for piece in pieces_short}

    # Mapowanie nazw figur na ich klasy
    piece_classes = {
        "R": figures.Rook,
        "N": figures.Knight,
        "B": figures.Bishop,
        "Q": figures.Queen,
        "K": figures.King,
        "p": figures.Pawn
    }

    # Inicjalizacja stanu planszy
    board_state = [[board_and_fields.Field(c, r) for c in range(8)] for r in range(8)]

    running = True
    selected_piece = None
    white_king_count = 0
    black_king_count = 0
    show_no_king_error = False
    show_check_error = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Obsługa kliknięcia myszy
                show_check_error = False
                show_no_king_error = False
                pos = pygame.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                if col < 8 and row < 8:
                    # Obsługa wyboru figury na planszy
                    if selected_piece:
                        piece_type = selected_piece[1]
                        piece_color = selected_piece[0]
                        if piece_type == "K":
                            if piece_color == "w" and white_king_count >= 1:
                                continue
                            if piece_color == "b" and black_king_count >= 1:
                                continue
                            if piece_color == "w":
                                white_king_count += 1
                            else:
                                black_king_count += 1
                        piece_class = piece_classes[piece_type]
                        if board_state[row][col].figure:
                            # Aktualizacja liczby królów, jeśli figura to król
                            if board_state[row][col].figure.type == 'K':
                                if board_state[row][col].figure.color == 'w':
                                    white_king_count -= 1
                                else:
                                    black_king_count -= 1
                        board_state[row][col].figure = piece_class(piece_color)
                        selected_piece = None
                    else:
                        # Usunięcie figury z planszy
                        piece = board_state[row][col].figure
                        if piece:
                            selected_piece = (piece.color, piece.type)
                            if piece.type == "K":
                                if piece.color == "w":
                                    white_king_count -= 1
                                else:
                                    black_king_count -= 1
                            board_state[row][col].figure = None
                else:
                    # Obsługa wyboru figury z panelu
                    for i, color in enumerate(["w", "b"]):
                        for j, piece_type in enumerate(["R", "N", "B", "Q", "K", "p"]):
                            col = j % 2
                            row = j // 2
                            if 8 * SQUARE_SIZE + col * (SQUARE_SIZE + 10) <= pos[0] <= 8 * SQUARE_SIZE + col * (SQUARE_SIZE + 10) + SQUARE_SIZE and (i * 3 + row) * SQUARE_SIZE + 10 <= pos[1] <= (i * 3 + row) * SQUARE_SIZE + 10 + SQUARE_SIZE:
                                selected_piece = (color, piece_type)

                # Obsługa kliknięcia na przycisk "Zapisz i wyjdź"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and pos[1] >= height - 80:
                    if white_king_count == 1 and black_king_count == 1:
                        board = board_and_fields.Board([[board_and_fields.Field(c, r, board_state[r][c].figure) for c in range(8)] for r in range(8)])
                        board.is_in_check('w')
                        if not board.incheck:
                            board.is_in_check('b')
                        if not board.incheck:
                            running = False
                            fen = board_to_fen(board_state)
                            with open("custom_board.fen", "w") as file:
                                file.write(fen)
                            import custom_board_game.normal_game_custom_board
                            custom_board_game.normal_game_custom_board.main(graphics.choose_time_control_dialog(screen, SQUARE_SIZE))
                            return
                        else:
                            show_check_error = True
                    else:
                        show_no_king_error = True

                # Obsługa kliknięcia na przycisk "Wyjdź bez zapisywania"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and pos[1] >= height - 140 and pos[1] < height - 80:
                    running = False
                    return

        # Rysowanie interfejsu
        screen.fill(GRAY)
        draw_board(screen, SQUARE_SIZE, board_state, pieces)
        draw_pieces_selection(screen, SQUARE_SIZE, pieces, config, selected_piece)

        # Rysowanie przycisków
        pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE * 8, height - 80, width - SQUARE_SIZE * 8, 80))
        exit_text = font.render("Zapisz i graj", True, WHITE)
        screen.blit(exit_text, (SQUARE_SIZE * 8 + 10, height - 70))

        pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE * 8, height - 140, width - SQUARE_SIZE * 8, 60))
        exit_without_save_text = font.render("Wyjdź bez zapisywania", True, WHITE)
        screen.blit(exit_without_save_text, (SQUARE_SIZE * 8 + 10, height - 130))

        # Wyświetlanie komunikatów o błędach
        if show_no_king_error:
            error_text = font.render("Musisz ustawić królów!", True, RED)
            screen.blit(error_text, (SQUARE_SIZE * 8 + 10, height - 200))
        if show_check_error:
            check_error_text = font.render("Szach!", True, RED)
            screen.blit(check_error_text, (SQUARE_SIZE * 8 + 10, height - 230))

        pygame.display.flip()

    return
