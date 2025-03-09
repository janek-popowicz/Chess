import pygame
import sys
import engine
import board_and_fields
import json
import time

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960", "icons": "classic"}

# Funkcja do rysowania szachownicy
def draw_board(screen, SQUARE_SIZE):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board, SQUARE_SIZE, pieces):
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece != "--":
                screen.blit(pieces[piece], pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
# Funkcja do podświetlania możliwych ruchów
def highlight_moves(screen, field, square_size:int,board, color_move, color_take):
    try:
        cords = board.get_legal_moves(field, field.figure.color)
    except AttributeError:
        return None
    for cord in cords:
        highlighted_tile = pygame.Surface((square_size, square_size))
        highlighted_tile.fill(color_move)
        if board.board_state[cord[0]][cord[1]].figure != None:
            if field.figure.color != board.board_state[cord[0]][cord[1]].figure.color:
                highlighted_tile.fill(color_take)
        if field.figure.type == 'p' and (field.x - cord[1]) != 0:
            highlighted_tile.fill(color_take)
        screen.blit(highlighted_tile, (((7-cord[1]) * square_size),((7- cord[0]) * square_size)))
# Funkcja do rysowania interfejsu
def draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times):
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, 0, 200, SQUARE_SIZE*8))
    if turn == 'w':
        screen.blit(texts[0][0], texts[0][1])
    else:
        screen.blit(texts[1][0], texts[1][1])
    screen.blit(player_times[0][0], player_times[0][1])
    screen.blit(player_times[1][0], player_times[1][1])
    screen.blit(texts[2][0], texts[2][1])

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02}"

# Funkcja główna
def main():
    pygame.init()
    # Ładowanie konfiguracji
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    print(width, height, SQUARE_SIZE)
    # Ustawienia ekranu
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess Game")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Kolory
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    HIGHLIGHT_MOVES = (100, 200, 100)
    HIGHLIGHT_TAKES = (200, 100, 100)

    # Czcionka
    font = pygame.font.Font(None, 36)

    # Ładowanie ikon figur
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    pieces = {}
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(pygame.image.load("pieces/" + icon_type + "/" + piece + ".png"), (SQUARE_SIZE-10, SQUARE_SIZE-10))
    
    running = True
    main_board = board_and_fields.Board()
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    # Teksty interfejsu
    texts = ((font.render(f"Kolejka: Białas", True, WHITE),(8*SQUARE_SIZE+10, 10)),
            (font.render(f"Kolejka: Czarnuch", True, WHITE), (8*SQUARE_SIZE+10, 10)),
            (font.render(f"Wyjście", True, WHITE), (8*SQUARE_SIZE+10, height-50)))

    # Czasy graczy
    start_time = time.time()
    black_time = 0
    white_time = 0
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece:
                        if engine.tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                            draw_board(screen,SQUARE_SIZE,)
                            draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
                            move_time = time.time() - start_time
                            if turn == 'w':
                                white_time += move_time
                            else:
                                black_time += move_time
                            turn = 'w' if turn == 'b' else 'b'
                            
                            #sprawdzanie co po ruchu
                            if selected_piece!=None:
                                whatAfter, yForPromotion, xForPromotion = engine.afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
                                if whatAfter == "promotion":
                                    main_board.print_board()
                                    choiceOfPromotion = input(f"""Pionek w kolumnie {xForPromotion} dotarł do końca planszy. Wpisz:
                                1 - Aby zmienić go w Skoczka
                                2 - Aby zmienić go w Gońca
                                3 - Aby zmienić go w Wieżę
                                4 - Aby zmienić go w Królową
                                                    """)
                                    engine.promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                                if whatAfter == "checkmate":
                                    print("Szach Mat!")
                                    running = False
                                elif whatAfter == "stalemate":
                                    print("Pat")
                                    running = False
                            selected_piece = None
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    running = False
                    pygame.quit()
                    import launcher
                    launcher.main()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if turn == 'w':
            current_white_time = white_time + (current_time - start_time)
            current_black_time = black_time
        else:
            current_black_time = black_time + (current_time - start_time)
            current_white_time = white_time

        player_times_font = ((font.render(format_time(current_white_time), True, WHITE),(8*SQUARE_SIZE+10,height - 150)),
                             (font.render(format_time(current_black_time), True, WHITE),(8*SQUARE_SIZE+10,80)))
        screen.fill(BLACK)
        draw_board(screen,SQUARE_SIZE,)
        draw_interface(screen, turn, SQUARE_SIZE,BLACK, texts, player_times_font)
        try:
            highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except TypeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    import launcher
    launcher.main()
    sys.exit()

if __name__ == "__main__":
    main()
