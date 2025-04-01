import pygame
import time

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from interface.graphics import *
from algorithms.evaluation import get_evaluation  # Import evaluation function
from interface.nerd_view import *


# Funkcja główna
def main(game_time):
    pygame.init()
    # Ładowanie konfiguracji
    config = load_config()
    resolution = config["resolution"]
    nerd_view = config["nerd_view"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    print(width, height, SQUARE_SIZE)
    # Ustawienia ekranu
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(global_translations.get("chess_game_launcher"))
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
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    # Teksty interfejsu
    texts = (
        (font.render(f"{global_translations.get('turn')}: {global_translations.get('white')}", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"{global_translations.get('turn')}: {global_translations.get('black')}", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(global_translations.get("exit_to_menu"), True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(global_translations.get("confirm_undo_text"), True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),  # Dodano przycisk "Cofnij ruch"
    )
    check_text = font.render(global_translations.get("check"), True, pygame.Color("red"))

    # Czasy graczy
    white_time = game_time
    black_time = game_time
    start_time = time.time()
    result = ""
    winner = ""
    in_check = None

    # Add player color setting (white by default)
    is_reversed = False  # Will be True for black player view

    #przystosowywanie pod nerd_view
    if nerd_view:
        from queue import Queue
        nerd_view_queue = Queue()
        moves_queue = Queue()
        root = tk.Tk()
        root.geometry("600x800+800+100")  # Pozycja obok okna gry
        stats_window = NormalStatsWindow(root, nerd_view_queue, moves_queue)
        moves_number = sum(len(value) for value in main_board.get_all_moves(turn))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                try: root.destroy()
                except: pass
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Modify click detection based on board orientation
                if is_reversed:
                    col = pos[0] // SQUARE_SIZE
                    row = pos[1] // SQUARE_SIZE
                else:
                    col = 7 - (pos[0] // SQUARE_SIZE)
                    row = 7 - (pos[1] // SQUARE_SIZE)
                
                if col < 8 and row < 8:
                    if selected_piece:
                        if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                            draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck, is_reversed)
                            draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
                            move_time = time.time() - start_time
                            if turn == 'w':
                                white_time -= move_time
                            else:
                                black_time -= move_time
                            turn = 'w' if turn == 'b' else 'b'
                            
                            #sprawdzanie co po ruchu
                            if selected_piece!=None:
                                whatAfter, yForPromotion, xForPromotion = afterMove(turn,main_board, selected_piece[0], selected_piece[1], row, col)
                                if whatAfter == "promotion":
                                    choiceOfPromotion = promotion_dialog(screen, SQUARE_SIZE, turn)
                                    promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
                                if whatAfter == "checkmate":
                                    result = global_translations.get("checkmate")
                                    winner = global_translations.get("white") if turn == 'b' else global_translations.get("black")
                                    running = False
                                elif whatAfter == "stalemate":
                                    result = global_translations.get("stalemate")
                                    winner = global_translations.get("draw")
                                    running = False
                                elif whatAfter == "check":
                                    in_check = turn
                                else:
                                    in_check = None
                            
                            #liczenie liczby ruchów, ważne pod nerd_view
                            if nerd_view:
                                moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                moves_queue.put(move_time)
                            selected_piece = None
                            start_time = time.time()
                           
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                # Obsługa przycisku "Wyjście"
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    running = False
                    try: root.destroy()
                    except: pass
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

        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if turn == 'w':
            current_white_time = max(0, white_time - (current_time - start_time))  # Odliczanie od ustawionego czasu
            current_black_time = black_time  # Zachowaj czas czarnego
            is_reversed = False  # Board from white's perspective
        else:
            current_black_time = max(0, black_time - (current_time - start_time))  # Odliczanie od ustawionego czasu
            current_white_time = white_time  # Zachowaj czas białego
            is_reversed = True   # Board from black's perspective

        # Sprawdzenie, czy czas się skończył
        if current_white_time <= 0 or current_black_time <= 0:
            running = False
            result = global_translations.get("time_out")
            winner = global_translations.get("black") if current_white_time <= 0 else global_translations.get("white")
            running = False
        

        player_times_font = (
            (font.render(f"{global_translations.get('white_time_label')}: {format_time(current_white_time)}", True, YELLOW if turn == 'w' else GRAY), 
             (8 * SQUARE_SIZE + 10, height - 150)),
            (font.render(f"{global_translations.get('black_time_label')}: {format_time(current_black_time)}", True, YELLOW if turn == 'b' else GRAY), 
             (8 * SQUARE_SIZE + 10, 80))
        )
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check, is_reversed)
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text)
        try:
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == turn:
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES, is_reversed)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed=is_reversed)
        pygame.display.flip()
        clock.tick(60)

        if nerd_view: #rysowanie nerd_view
            current_time_for_stats = time.time()
            evaluation = get_evaluation(main_board)
            evaluation = evaluation[0] - evaluation[1]
            nerd_view_queue.put((current_time_for_stats, evaluation, moves_number))
            root.update()
    
    save_in_short_algebraic(main_board, winner, result)
    save_in_long_algebraic(main_board, winner, result)
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    try: root.destroy()
    except: pass
    return
if __name__ == "__main__":

    main(10 * 60)
