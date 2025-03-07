import pygame
import sys
import engine
import board_and_fields
import json

def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960"}

# Funkcja do rysowania szachownicy
def draw_board(screen, board, SQUARE_SIZE, pieces):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board.get_piece(r, c)
            if piece != "--":
                screen.blit(pieces[piece], pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


# Funkcja do rysowania interfejsu
def draw_interface(screen, turn, SQUARE_SIZE,BLACK, texts):
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, 0, 200, SQUARE_SIZE*8))
    if turn =='w':
        screen.blit(texts[0][0], texts[0][1])
    else:
        screen.blit(texts[1][0], texts[1][1])
    screen.blit(texts[2][0], texts[2][1])

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

    # Kolory
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    HIGHLIGHT = (200, 200, 200)

    # Czcionka
    font = pygame.font.Font(None, 36)

    # Ładowanie ikon figur
    pieces = {
        "wp": pygame.image.load("pieces/wp.png"),
        "wR": pygame.image.load("pieces/wR.png"),
        "wN": pygame.image.load("pieces/wN.png"),
        "wB": pygame.image.load("pieces/wB.png"),
        "wQ": pygame.image.load("pieces/wQ.png"),
        "wK": pygame.image.load("pieces/wK.png"),
        "bp": pygame.image.load("pieces/bp.png"),
        "bR": pygame.image.load("pieces/bR.png"),
        "bN": pygame.image.load("pieces/bN.png"),
        "bB": pygame.image.load("pieces/bB.png"),
        "bQ": pygame.image.load("pieces/bQ.png"),
        "bK": pygame.image.load("pieces/bK.png")
    }
    
    running = True
    main_board = board_and_fields.Board()
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    # Teksty interfejsu
    texts = ((font.render(f"Kolejka: Białas", True, WHITE),(8*SQUARE_SIZE+10, 10)),
            (font.render(f"Kolejka: Czarnuch", True, WHITE), (8*SQUARE_SIZE+10, 10)),
            (font.render(f"Wyjście", True, WHITE), (8*SQUARE_SIZE+10, height-50)))

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
                            selected_piece = None
                            turn = 'w' if turn == 'b' else 'b'
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
                                    engine.promotion(turn, yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                                if whatAfter == "checkmate":
                                    print("Szach Mat!")
                                    running = False
                                elif whatAfter == "stalemate":
                                    print("Pat")
                                    running = False
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

        screen.fill(BLACK)
        draw_board(screen, main_board, SQUARE_SIZE, pieces)
        draw_interface(screen, turn, SQUARE_SIZE,BLACK, texts)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
