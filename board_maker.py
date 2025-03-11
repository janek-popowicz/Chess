import pygame
import sys
import board_and_fields
import figures
import json
import time

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960", "icons": "classic"}

def draw_board(screen, SQUARE_SIZE, board_state, pieces):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board_state[r][c].figure
            if piece:
                piece_key = f"{piece.color}{piece.type[0].upper() if piece.type != 'p' else piece.type}"
                piece_image = pieces[piece_key]
                screen.blit(piece_image, (c*SQUARE_SIZE+5, r*SQUARE_SIZE+5))

def draw_pieces_selection(screen, SQUARE_SIZE, pieces, config, selected_piece):
    icon_type = config["icons"]
    piece_types = ["R", "N", "B", "Q", "K", "p"]
    colors = ["w", "b"]
    for i, color in enumerate(colors):
        for j, piece_type in enumerate(piece_types):
            piece_key = f"{color}{piece_type}"
            piece_image = pieces[piece_key]
            col = j % 2
            row = j // 2
            x = 8*SQUARE_SIZE + col * (SQUARE_SIZE + 10)
            y = (i * 3 + row) * SQUARE_SIZE + 10
            if selected_piece == (color, piece_type):
                pygame.draw.rect(screen, pygame.Color("yellow"), pygame.Rect(x-5, y-5, SQUARE_SIZE, SQUARE_SIZE), 3)
            screen.blit(piece_image, (x, y))

def board_to_fen(board_state):
    fen = ""
    for row in board_state:
        empty_count = 0
        for field in row:
            if field.figure is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                piece = field.figure
                piece_char = piece.type[0].upper() if piece.type != 'pawn' else 'P'
                if piece.color == 'b':
                    piece_char = piece_char.lower()
                fen += piece_char
        if empty_count > 0:
            fen += str(empty_count)
        fen += "/"
    fen = fen[:-1]  # Remove the trailing slash
    fen += " w - - 0 1"  # Add default FEN suffix
    return fen

def main():
    pygame.init()
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Custom Board Setup")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    YELLOW = pygame.Color("yellow")
    RED = pygame.Color("red")

    font = pygame.font.Font(None, 36)

    # Ładowanie ikon figur
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    pieces = {}
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(pygame.image.load("pieces/" + icon_type + "/" + piece + ".png"), (SQUARE_SIZE-10, SQUARE_SIZE-10))

    # Mapowanie nazw figur na ich klasy
    piece_classes = {
        "R": figures.Rook,
        "N": figures.Knight,
        "B": figures.Bishop,
        "Q": figures.Queen,
        "K": figures.King,
        "p": figures.Pawn
    }

    board_state = [[board_and_fields.Field(c, r) for c in range(8)] for r in range(8)]

    running = True
    selected_piece = None
    white_king_count = 0
    black_king_count = 0
    show_error = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                if col < 8 and row < 8:
                    if selected_piece:
                        piece_type = selected_piece[1]
                        piece_color = selected_piece[0]
                        if piece_type == "K":
                            if piece_color == "w" and white_king_count >= 1:
                                continue
                            elif piece_color == "b" and black_king_count >= 1:
                                continue
                        piece_class = piece_classes[piece_type]
                        board_state[row][col].figure = piece_class(piece_color)
                        if piece_type == "K":
                            if piece_color == "w":
                                white_king_count += 1
                            else:
                                black_king_count += 1
                        selected_piece = None
                    else:
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
                    for i, color in enumerate(["w", "b"]):
                        for j, piece_type in enumerate(["R", "N", "B", "Q", "K", "p"]):
                            col = j % 2
                            row = j // 2
                            if 8*SQUARE_SIZE + col * (SQUARE_SIZE + 10) <= pos[0] <= 8*SQUARE_SIZE + col * (SQUARE_SIZE + 10) + SQUARE_SIZE and (i * 3 + row) * SQUARE_SIZE + 10 <= pos[1] <= (i * 3 + row) * SQUARE_SIZE + 10 + SQUARE_SIZE:
                                selected_piece = (color, piece_type)
                # Sprawdzenie kliknięcia na przycisk "Zapisz i wyjdź"
                if pos[0] > SQUARE_SIZE*8 and pos[0] <= width-20 and pos[1] >= height-80:
                    if white_king_count == 1 and black_king_count == 1:
                        running = False
                    else:
                        show_error = True
                # Sprawdzenie kliknięcia na przycisk "Wyjdź bez zapisywania"
                if pos[0] > SQUARE_SIZE*8 and pos[0] <= width-20 and pos[1] >= height-140 and pos[1] <height-80:
                    running = False

        screen.fill(GRAY)
        draw_board(screen, SQUARE_SIZE, board_state, pieces)
        draw_pieces_selection(screen, SQUARE_SIZE, pieces, config, selected_piece)
        # Rysowanie przycisku "Zapisz i wyjdź"
        pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, height-80, width-SQUARE_SIZE*8-20, 60))
        exit_text = font.render("Zapisz i graj", True, WHITE)
        screen.blit(exit_text, (SQUARE_SIZE*8+10, height-70))
        # Rysowanie przycisku "Wyjdź bez zapisywania"
        pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, height-140, width-SQUARE_SIZE*8-20, 60))
        exit_without_save_text = font.render("Wyjdź bez zapisywania", True, WHITE)
        screen.blit(exit_without_save_text, (SQUARE_SIZE*8+10, height-130))
        # Wyświetlanie komunikatu o błędzie
        if show_error:
            error_text = font.render("Musisz ustawić królów!", True, RED)
            screen.blit(error_text, (SQUARE_SIZE*8+10, height-200))

        pygame.display.flip()

    pygame.quit()

    if white_king_count == 1 and black_king_count == 1:
        # Zapisz ustawienie szachownicy do pliku w formacie FEN
        fen = board_to_fen(board_state)
        with open("custom_board.fen", "w") as file:
            file.write(fen)

        # Uruchom normal_game.py z nowym ustawieniem szachownicy
        import normal_game_custom_board
        normal_game_custom_board.main()
        return
    
    import launcher
    launcher.main()

if __name__ == "__main__":
    main()