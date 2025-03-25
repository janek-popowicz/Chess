import pygame
import time
import json
from pathlib import Path

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from engine.fen_operations import *
from graphics import *
from random import randint


def load_grandmaster_moves(grandmaster_name):
    """Wczytuje ruchy arcymistrza z pliku JSON."""
    json_path = Path(f"grandmaster/json/{grandmaster_name}.json")
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Nie znaleziono pliku z ruchami arcymistrza: {json_path}")
        return {}

def get_grandmaster_move(board, turn, grandmaster_moves):
    """Wybiera ruch arcymistrza na podstawie aktualnej pozycji."""
    current_fen = board_to_fen_inverted(board, turn)
    fen_parts = current_fen.split(' ')
    position_fen = f"{fen_parts[0]}"
    print(position_fen)
    if position_fen in grandmaster_moves:
        moves_list = grandmaster_moves[position_fen]
        return moves_list[randint(1,len(moves_list))]  # Bierzemy pierwszy dostępny ruch
    return None

# Funkcja główna
def main(player_color, grandmaster_name):
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
    YELLOW = pygame.Color("yellow")
    HIGHLIGHT_MOVES = (100, 200, 100)
    HIGHLIGHT_TAKES = (147, 168, 50)

    # Czcionka
    font = pygame.font.Font(None, 36)

    # Ładowanie ikon figur
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    pieces = {}
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(pygame.image.load("pieces/" + icon_type + "/" + piece + ".png"), (SQUARE_SIZE-10, SQUARE_SIZE-10))
    
    running = True
    main_board = Board()
    grandmaster_color = 'w' if player_color == 'b' else 'b'
    grandmaster_moves = load_grandmaster_moves(grandmaster_name)
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    # Teksty interfejsu
    texts = (
        (font.render(f"Kolejka: białe", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Kolejka: czarne", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Wyjście", True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(f"Cofnij ruch", True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),  # Dodano przycisk "Cofnij ruch"
    )
    check_text = font.render("Szach!", True, pygame.Color("red"))

    # Czasy graczy
    start_time = time.time()
    black_time = 0
    white_time = 0
    result = ""
    winner = ""
    in_check = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece:
                        if turn == player_color and tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                            move_time = time.time() - start_time
                            if turn == 'w':
                                white_time += move_time
                            else:
                                black_time += move_time
                            turn = 'w' if turn == 'b' else 'b'
                            
                            #sprawdzanie co po ruchu
                            if selected_piece!=None:
                                whatAfter, yForPromotion, xForPromotion = afterMove(turn,main_board, selected_piece[0], selected_piece[1], row, col)
                                if whatAfter == "promotion":
                                    choiceOfPromotion = promotion_dialog(screen, SQUARE_SIZE, turn)
                                    promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
                                if whatAfter == "checkmate":
                                    result = "Szach Mat!"
                                    winner = "Białe" if turn == 'b' else "Czarne"
                                    running = False
                                elif whatAfter == "stalemate":
                                    result = "Pat"
                                    winner = "Remis"
                                    running = False
                                elif whatAfter == "check":
                                    in_check = turn
                                else:
                                    in_check = None
                            selected_piece = None
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                # Obsługa przycisku "Wyjście"
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    running = False
                    return
                # Obsługa przycisku "Cofnij ruch"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and height - 100 <= pos[1] < height - 80:
                    if confirm_undo_dialog(screen, SQUARE_SIZE):
                        if undoMove(main_board):  # Cofnięcie ruchu
                            turn = 'w' if turn == 'b' else 'b'  # Zmiana tury
                            start_time = time.time()  # Reset czasu tury
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        if turn != player_color:
            move_time = time.time() - start_time
            if turn == 'w':
                white_time += move_time
            else:
                black_time += move_time
            turn = 'w' if turn == 'b' else 'b'
            draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck)
            draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
            pygame.display.flip()
            time.sleep(1)
            grandmaster_move = get_grandmaster_move(main_board, grandmaster_color, grandmaster_moves)
            if grandmaster_move:
                print(grandmaster_move)
                cords = notation_to_cords(main_board, grandmaster_move, turn)
                print(cords)
                y1, x1, y2, x2 = cords
            else:
                print("Nie znaleziono ruchu dla danej pozycji")
                print(grandmaster_move)
                break
            #sprawdzanie co po ruchu
            if selected_piece!=None:
                whatAfter, yForPromotion, xForPromotion = afterMove(turn,main_board, y1, x1, y2, x2)
                if whatAfter == "promotion":
                    choiceOfPromotion = "4"
                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, x1, y1, x2, y2)
                if whatAfter == "checkmate":
                    result = "Szach Mat!"
                    winner = "Białe" if turn == 'b' else "Czarne"
                    running = False
                elif whatAfter == "stalemate":
                    result = "Pat"
                    winner = "Remis"
                    running = False
                elif whatAfter == "check":
                    in_check = turn
                else:
                    in_check = None
            selected_piece = None
            start_time = time.time()
            

        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if turn == 'w':
            current_white_time = white_time + (current_time - start_time)
            current_black_time = black_time
        else:
            current_black_time = black_time + (current_time - start_time)
            current_white_time = white_time

        player_times_font = ((font.render(format_time(current_white_time), True, YELLOW if turn=='w' else GRAY),(8*SQUARE_SIZE+10,height - 150)),
                             (font.render(format_time(current_black_time), True, YELLOW if turn=='b' else GRAY),(8*SQUARE_SIZE+10,80)))
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check)
        draw_interface(screen, turn, SQUARE_SIZE,BLACK, texts, player_times_font, in_check, check_text)
        try:
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == turn:
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)
    
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    return
if __name__ == "__main__":

    main('w', 'Nakamura')  # Przykładowe wywołanie
