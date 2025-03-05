import pygame
import sys
import engine
import board_and_fields

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
screen = pygame.display.set_mode((1000, 800))
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

# Funkcja do rysowania szachownicy
def draw_board(screen, board):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c*100, r*100, 100, 100))
            piece = board.get_piece(r, c)
            if piece != "--":
                screen.blit(pieces[piece], pygame.Rect(c*100, r*100, 100, 100))

# Funkcja główna
def main():
    running = True
    main_board = board_and_fields.Board()
    turn = 'b'
    selected_piece = None
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // 100
                row = pos[1] // 100
                if selected_piece:
                    if engine.tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                        selected_piece = None
                        turn = 'w' if turn == 'b' else 'b'
                    else:
                        selected_piece = (row, col)
                else:
                    selected_piece = (row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill(BLACK)
        draw_board(screen, main_board)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()