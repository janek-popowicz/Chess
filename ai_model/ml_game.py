import pygame
import time
import threading
import queue
import copy

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from graphics import *
from algorithms.minimax import *
from algorithms.monte_carlo_tree_search import *
import ai_model.ml as ml



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

    player_turn = choose_color_dialog(screen, SQUARE_SIZE)
    algorithm = choose_algorithm_dialog(screen, SQUARE_SIZE)

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

    # Dodaj zmienne do obsługi wątku
    #minimax_thread = None
    result_queue = queue.Queue()
    #calculating = False

    # Aktualizacja wyświetlania czasów
    def update_time_display(white_time, black_time, current_time, start_time, turn):
        if turn == 'w':
            current_white_time = white_time + (current_time - start_time)
            current_black_time = black_time
        else:
            current_black_time = black_time + (current_time - start_time)
            current_white_time = white_time
            
        return (
            (font.render(format_time(current_white_time), True, YELLOW if turn == 'w' else GRAY), 
             (8 * SQUARE_SIZE + 10, height - 150)),
            (font.render(format_time(current_black_time), True, YELLOW if turn == 'b' else GRAY),
             (8 * SQUARE_SIZE + 10, 80))
        )

    while running:
        # Obsługa zdarzeń zawsze na początku pętli
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                '''if minimax_thread and minimax_thread.is_alive():
                    minimax_thread.stop()
                    minimax_thread.join(timeout=0.1)
                # W obsłudze wyjścia
                if monte_carlo_thread and monte_carlo_thread.is_alive():
                    monte_carlo_thread.stop()
                    monte_carlo_thread.join(timeout=0.1)'''
                running = False
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Obsługa przycisków zawsze dostępna
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20:
                    if pos[1] >= height - 80:  # Przycisk "Wyjście"
                        
                        running = False
                        return
                    elif height - 130 <= pos[1] < height - 80:  # Przycisk "Cofnij ruch"
                        if confirm_undo_dialog(screen, SQUARE_SIZE):
                            if undoMove(main_board):
                                turn = 'w' if turn == 'b' else 'b'
                                start_time = time.time()
                
                # Obsługa ruchów gracza tylko w jego turze
                if turn == player_turn:
                    col = 7 - (pos[0] // SQUARE_SIZE)
                    row = 7 - (pos[1] // SQUARE_SIZE)
                    if col < 8 and row < 8:
                        if selected_piece:
                            if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                                draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck)
                                draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    '''if minimax_thread and minimax_thread.is_alive():
                        minimax_thread.stop()
                        minimax_thread.join(timeout=0.1)'''
                    running = False
                # W obsłudze wyjścia
                    '''if monte_carlo_thread and monte_carlo_thread.is_alive():
                        monte_carlo_thread.stop()
                        monte_carlo_thread.join(timeout=0.1)'''

        # Ruch AI w osobnym bloku
        if turn != player_turn:
            #move - ai move 
            move = ml.get_ai_move(main_board, turn)
            if move:
                from_row, from_col, to_row, to_col = move
                if tryMove(turn, main_board, from_row, from_col, to_row, to_col):
                    if turn == 'w':
                        white_time += time.time() - start_time
                    else:
                        black_time += time.time() - start_time
                    turn = 'w' if turn == 'b' else 'b'
                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, from_row, from_col, to_row, to_col)
                    if whatAfter == "promotion":
                        promotion_choice = '10'  # Zawsze promuj do królowej
                        promotion(yForPromotion, xForPromotion, main_board, promotion_choice)
                        whatAfter, _, _ = afterMove(turn, main_board, from_row, from_col, to_row, to_col)
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
                start_time = time.time()

                        

        # Przed renderowaniem
        current_time = time.time()
        player_times_font = update_time_display(white_time, black_time, current_time, start_time, turn)

        # Rendering zawsze na końcu pętli
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check)
        
        # Dodanie podświetlania ruchów
        try:
            if selected_piece and (config["highlight_enemy"] or main_board.get_piece(selected_piece[0], selected_piece[1])[0] == turn):
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]], 
                              SQUARE_SIZE, main_board, HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except (TypeError, AttributeError):
            pass

        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text)
        


        pygame.display.flip()
        clock.tick(60)
    


    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    return

if __name__ == "__main__":

    main()
