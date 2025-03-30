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
from algorithms.evaluation import get_evaluation  # Import evaluation function

MONTE_CARLO_LIMIT = 10
MONTE_CARLO_DEPTH = 5

def minimaxThread():
    pass

# Dodaj nową klasę po MinimaxThread
class MonteCarloThread(threading.Thread):
    def __init__(self, board, max_depth, turn, result_queue):
        super().__init__()
        self.board = copy.deepcopy(board)
        self.max_depth = max_depth
        self.turn = turn
        self.result_queue = result_queue
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        try:
            mc_obj = Mcts(self.turn)
            # Sprawdzamy czy wątek nie został zatrzymany przed każdą symulacją
            if not self.stopped():
                move = mc_obj.pick_best_move(self.board, MONTE_CARLO_LIMIT, self.max_depth)
                if not self.stopped():
                    self.result_queue.put(move)
        except Exception as e:
            print(f"Błąd w wątku Monte Carlo: {e}")
            self.result_queue.put(None)

# Funkcja główna
def main(player_turn, algorithm):
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
    
    minimax_thread = 0
    monte_carlo_thread = 0
    running = True
    main_board = Board()
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    minimax_thread = None
    monte_carlo_thread = None

    is_reversed = False if player_turn == 'w' else True

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
    minimax_thread = None
    result_queue = queue.Queue()
    calculating = False

    # Aktualizacja wyświetlania czasów
    def update_time_display(white_time, black_time, current_time, start_time, turn, player_turn):
        """Update time display with player's time always at bottom"""
        if turn == 'w':
            current_white_time = white_time + (current_time - start_time)
            current_black_time = black_time
        else:
            current_black_time = black_time + (current_time - start_time)
            current_white_time = white_time
        
        # If player is white, white time goes bottom
        if player_turn == 'w':
            return (
                (font.render(format_time(current_black_time), True, YELLOW if turn == 'b' else GRAY),
                 (8 * SQUARE_SIZE + 10, 80)),  # Bot's time (black) at top
                (font.render(format_time(current_white_time), True, YELLOW if turn == 'w' else GRAY),
                 (8 * SQUARE_SIZE + 10, height - 150))  # Player's time (white) at bottom
            )
        # If player is black, black time goes bottom
        else:
            return (
                (font.render(format_time(current_white_time), True, YELLOW if turn == 'w' else GRAY),
                 (8 * SQUARE_SIZE + 10, 80)),  # Bot's time (white) at top
                (font.render(format_time(current_black_time), True, YELLOW if turn == 'b' else GRAY),
                 (8 * SQUARE_SIZE + 10, height - 150))  # Player's time (black) at bottom
            )

    while running:
        # Obsługa zdarzeń zawsze na początku pętli
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if minimax_thread and minimax_thread.is_alive():
                    minimax_thread.stop()
                    minimax_thread.join(timeout=0.1)
                # W obsłudze wyjścia
                if monte_carlo_thread and monte_carlo_thread.is_alive():
                    monte_carlo_thread.stop()
                    monte_carlo_thread.join(timeout=0.1)
                running = False
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Modify click detection based on board orientation
                if is_reversed:
                    col = pos[0] // SQUARE_SIZE
                    row = pos[1] // SQUARE_SIZE
                else:
                    col = 7 - (pos[0] // SQUARE_SIZE)
                    row = 7 - (pos[1] // SQUARE_SIZE)
                # Obsługa przycisków zawsze dostępna
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20:
                    if pos[1] >= height - 80:  # Przycisk "Wyjście"
                        if minimax_thread and minimax_thread.is_alive():
                            minimax_thread.stop()
                            minimax_thread.join(timeout=0.1)
                        running = False
                        return
                    elif height - 130 <= pos[1] < height - 80:  # Przycisk "Cofnij ruch"
                        if confirm_undo_dialog(screen, SQUARE_SIZE):
                            # Stop minimax thread if running
                            if minimax_thread and minimax_thread.is_alive():
                                minimax_thread.stop()
                                minimax_thread.join(timeout=0.1)
                            
                            # Reset thread variables
                            minimax_thread = None
                            calculating = False
                            
                            # Clear result queue
                            while not result_queue.empty():
                                result_queue.get_nowait()
                            
                            # Perform undo
                            if undoMove(main_board):
                                turn = 'w' if turn == 'b' else 'b'
                                start_time = time.time()
                 
                # Obsługa ruchów gracza tylko w jego turze
                if turn == player_turn:
                    if col < 8 and row < 8:
                        if selected_piece:
                            if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                                draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck, is_reversed)
                                draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
                                pygame.display.flip()
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
                    if minimax_thread and minimax_thread.is_alive():
                        minimax_thread.stop()
                        minimax_thread.join(timeout=0.1)
                    running = False
                # W obsłudze wyjścia
                    if monte_carlo_thread and monte_carlo_thread.is_alive():
                        monte_carlo_thread.stop()
                        monte_carlo_thread.join(timeout=0.1)

        # Ruch AI w osobnym bloku
        if turn != player_turn and running:
            if algorithm == "minimax":
                minimax_obj = Minimax(main_board, 2, turn, 1000)
                y1, x1, y2, x2 = minimax_obj.get_best_move()
                if tryMove(turn, main_board, y1, x1, y2, x2):
                    # Handle successful move
                    if turn == 'w':
                        white_time += time.time() - start_time
                    else:
                        black_time += time.time() - start_time
                    turn = 'w' if turn == 'b' else 'b'
                    
                    # Handle promotion and game state
                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, y1, x1, y2, x2)
                    if whatAfter == "promotion":
                        promotion(yForPromotion, xForPromotion, main_board, '4')  # Always queen
                        whatAfter, _, _ = afterMove(turn, main_board, y1, x1, y2, x2)
                    
                    # Update game state
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

            elif algorithm == "monte_carlo":
                if not calculating:
                    calculating = True
                    result_queue = queue.Queue()
                    monte_carlo_thread = MonteCarloThread(main_board, MONTE_CARLO_DEPTH, turn, result_queue)
                    monte_carlo_thread.start()
                
                try:
                    move = result_queue.get_nowait()
                    calculating = False
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
                except queue.Empty:
                    pass  # Kontynuuj bez blokowania
                        

        # Przed renderowaniem
        current_time = time.time()
        evaluation = get_evaluation(main_board)[0] - get_evaluation(main_board)[1]  # Calculate evaluation
        player_times_font = update_time_display(white_time, black_time, current_time, start_time, turn, player_turn)

        # Rendering zawsze na końcu pętli
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check, is_reversed)
        
        # Dodanie podświetlania ruchów
        try:
            if selected_piece and (config["highlight_enemy"] or main_board.get_piece(selected_piece[0], selected_piece[1])[0] == turn):
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]], 
                              SQUARE_SIZE, main_board, HIGHLIGHT_MOVES, HIGHLIGHT_TAKES, is_reversed)
        except (TypeError, AttributeError):
            pass

        draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text, evaluation=evaluation)
        
        if calculating:
            calculating_text = font.render("Obliczanie...", True, WHITE)
            screen.blit(calculating_text, (8 * SQUARE_SIZE + 10, height - 200))
            dots = "." * ((int(time.time() * 2) % 4))
            calculating_dots = font.render(dots, True, WHITE)
            screen.blit(calculating_dots, (8 * SQUARE_SIZE + 150, height - 200))

        pygame.display.flip()
        clock.tick(60)
    
    # Upewnij się, że wątek zostanie zakończony przy wyjściu
    if minimax_thread and minimax_thread.is_alive():
        minimax_thread.stop()
        minimax_thread.join(timeout=0.1)
    # W obsłudze wyjścia
    if monte_carlo_thread and monte_carlo_thread.is_alive():
        monte_carlo_thread.stop()
        monte_carlo_thread.join(timeout=0.1)

    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    return

if __name__ == "__main__":

    main()
