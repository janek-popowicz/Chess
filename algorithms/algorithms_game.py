import pygame
import time
import threading
import queue
import copy
from multiprocessing import Process, Queue as multiQueue

# Importy modułów
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from interface.graphics import *
from algorithms.minimax import *
from algorithms.monte_carlo_tree_search import *
from algorithms.evaluation import get_evaluation
from interface.nerd_view import *


def calculate_minimax(board, depth, color, time_limit, min_time, result_queue):
    """
    Funkcja obliczająca najlepszy ruch za pomocą algorytmu Minimax.

    Args:
        board (Board): Obiekt planszy szachowej.
        depth (int): Głębokość przeszukiwania.
        color (str): Kolor gracza ('w' lub 'b').
        time_limit (float): Maksymalny czas na obliczenia.
        min_time (float): Minimalny czas oczekiwania przed zwróceniem wyniku.
        result_queue (Queue): Kolejka do przechowywania wyniku.

    Returns:
        None: Wynik jest umieszczany w kolejce `result_queue`.
    """
    minimax_start_time = time.time()
    board_copy = copy.deepcopy(board)
    minimax_obj = Minimax(board_copy, depth, color, time_limit)
    best_move, additional_info, moves_from_list = minimax_obj.get_best_move()
    all_info = (best_move, additional_info, moves_from_list)

    # Upewnij się, że obliczenia trwają co najmniej `min_time`
    elapsed_time = time.time() - minimax_start_time
    if elapsed_time < min_time:
        time.sleep(min_time - elapsed_time)

    result_queue.put(all_info)


class MonteCarloThread(threading.Thread):
    """
    Wątek do wykonywania obliczeń za pomocą algorytmu Monte Carlo Tree Search (MCTS).
    """

    def __init__(self, board, max_depth, turn, result_queue):
        """
        Inicjalizuje wątek Monte Carlo.

        Args:
            board (Board): Obiekt planszy szachowej.
            max_depth (int): Maksymalna głębokość przeszukiwania.
            turn (str): Tura gracza ('w' lub 'b').
            result_queue (Queue): Kolejka do przechowywania wyniku.
        """
        super().__init__()
        self.board = copy.deepcopy(board)
        self.max_depth = max_depth
        self.turn = turn
        self.result_queue = result_queue
        self._stop_event = threading.Event()

    def stop(self):
        """Zatrzymuje wątek."""
        self._stop_event.set()

    def stopped(self):
        """Sprawdza, czy wątek został zatrzymany."""
        return self._stop_event.is_set()

    def run(self):
        """
        Wykonuje algorytm Monte Carlo Tree Search i umieszcza wynik w kolejce `result_queue`.
        """
        try:
            mc_obj = Mcts(self.turn)
            if not self.stopped():
                move = mc_obj.pick_best_move(self.board, MAX_TIME, self.max_depth)
                if not self.stopped():
                    self.result_queue.put(move)
        except Exception as e:
            # Obsługa błędów
            self.result_queue.put(None)


def update_times_display(white_time, black_time, turn, player_color, font, SQUARE_SIZE, YELLOW, GRAY, height):
    """
    Aktualizuje wyświetlanie czasu graczy.

    Args:
        white_time (float): Pozostały czas dla białego gracza.
        black_time (float): Pozostały czas dla czarnego gracza.
        turn (str): Aktualna tura ('w' lub 'b').
        player_color (str): Kolor gracza ('w' lub 'b').
        font (pygame.font.Font): Czcionka do renderowania tekstu.
        SQUARE_SIZE (int): Rozmiar pola na planszy.
        YELLOW (tuple): Kolor dla aktywnego gracza.
        GRAY (tuple): Kolor dla nieaktywnego gracza.
        height (int): Wysokość ekranu.

    Returns:
        tuple: Wyświetlane czasy dla obu graczy.
    """
    return (
        (font.render(f"{global_translations.get('black')}: {format_time(black_time)}", True, YELLOW if turn == 'b' else GRAY),
         (8 * SQUARE_SIZE + 10, 80)),
        (font.render(f"{global_translations.get('white')}: {format_time(white_time)}", True, YELLOW if turn == 'w' else GRAY),
         (8 * SQUARE_SIZE + 10, height - 150))
    ) if player_color == 'w' else (
        (font.render(f"{global_translations.get('white')}: {format_time(white_time)}", True, YELLOW if turn == 'w' else GRAY),
         (8 * SQUARE_SIZE + 10, 80)),
        (font.render(f"{global_translations.get('black')}: {format_time(black_time)}", True, YELLOW if turn == 'b' else GRAY),
         (8 * SQUARE_SIZE + 10, height - 150))
    )


def main(player_turn, algorithm, game_time):
    """
    Główna funkcja gry szachowej z obsługą AI.

    Args:
        player_turn (str): Kolor gracza ('w' lub 'b').
        algorithm (str): Algorytm do użycia ('minimax' lub 'monte_carlo').
        game_time (float): Całkowity czas gry dla każdego gracza w sekundach.

    Returns:
        None
    """
    pygame.init()

    # Ładowanie konfiguracji
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8

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
    pieces = {piece: pygame.transform.scale(pygame.image.load(f"pieces/{icon_type}/{piece}.png"), (SQUARE_SIZE - 10, SQUARE_SIZE - 10)) for piece in pieces_short}

    # Inicjalizacja zmiennych
    main_board = Board()
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()
    minimax_process = None
    monte_carlo_thread = None
    is_reversed = player_turn != 'w'
    running = True

    # Teksty interfejsu
    texts = (
        (font.render(f"{global_translations.get('turn_white')}", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"{global_translations.get('turn_black')}", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"{global_translations.get('exit')}", True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(f"{global_translations.get('confirm_undo_text')}", True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),
    )
    check_text = font.render(global_translations.get("check"), True, pygame.Color("red"))



    # Właświwości algorytmów
    global MAX_TIME
    global MIN_TIME
    min_depth = 1 if algorithm == "minimax" else 5
    max_depth = 4 if algorithm == "minimax" else 30
    ai_settings = choose_ai_settings_dialog(screen, SQUARE_SIZE, min_depth, max_depth)
    if ai_settings == None:
        return
    depth, MIN_TIME, MAX_TIME = ai_settings

    # Dodaj zmienne do obsługi wątku
    minimax_process = None
    result_queue = queue.Queue()
    minimax_queue = multiQueue()
    calculating = False


    nerd_view = config["nerd_view"]
    if nerd_view:
        from queue import Queue
        nerd_view_queue = Queue()
        moves_queue = Queue()
        root = tk.Tk()
        root.geometry("600x400+800+100")  # Pozycja obok okna gry
        stats_window = NormalStatsWindow(root, nerd_view_queue, moves_queue)
        moves_number = sum(len(value) for value in main_board.get_all_moves(turn))

        algo_root = tk.Toplevel()
        moves = []
        info_window = AlgorithmInfoWindow(
            algo_root,
            moves_list = moves,
            algorithm_name = algorithm,
            search_depth=depth,
            additional_info="...",
            best_move=(None)
        )

    # Czasy graczy
    black_time = game_time
    white_time = game_time
    start_time = time.time()
    result = ""
    winner = ""
    in_check = None

    while running:
        # Obsługa zdarzeń zawsze na początku pętli
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try: root.destroy()
                except: pass
                try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
                except: pass
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
                        running = False
                        try: minimax_process.terminate()
                        except: pass
                        try: root.destroy()
                        except: pass
                        if monte_carlo_thread and monte_carlo_thread.is_alive():
                            monte_carlo_thread.stop()
                            monte_carlo_thread.join(timeout=0.1)
                        return
                    elif height - 130 <= pos[1] < height - 80:  # Przycisk "Cofnij ruch"
                        # Reset thread variables
                        calculating = False
                        try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
                        except: pass
                        if monte_carlo_thread and monte_carlo_thread.is_alive():
                            monte_carlo_thread.stop()
                            monte_carlo_thread.join(timeout=0.1)
                        
                        # Clear result queue
                        while not result_queue.empty():
                            result_queue.get_nowait()
                        while not minimax_queue.empty():
                            minimax_queue.get_nowait()
                        
                        if confirm_undo_dialog(screen, SQUARE_SIZE):
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
                                        result = global_translations.get("checkmate")  # "Szach Mat!"
                                        winner = global_translations.get("white") if turn == 'b' else global_translations.get("black")
                                        running = False
                                    elif whatAfter == "stalemate":
                                        result = global_translations.get("stalemate")  # "Pat"
                                        winner = global_translations.get("draw")  # "Remis"
                                        running = False
                                    elif whatAfter == "check":
                                        in_check = turn
                                    else:
                                        in_check = None
                                selected_piece = None
                                #liczenie liczby ruchów, ważne pod nerd_view
                                if nerd_view:
                                    moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                    moves_queue.put(move_time)
                                start_time = time.time()

                            else:
                                selected_piece = (row, col)
                        else:
                            selected_piece = (row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # W obsłudze wyjścia
                    try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
                    except: pass
                    if monte_carlo_thread and monte_carlo_thread.is_alive():
                        monte_carlo_thread.stop()
                        monte_carlo_thread.join(timeout=0.1)

        # Ruch AI w osobnym bloku
        if turn != player_turn and running:
            if algorithm == "minimax":
                if not calculating:
                    calculating = True
                    minimax_process = Process(
                        target=calculate_minimax,
                        args=(main_board,depth,turn,MAX_TIME,MIN_TIME,minimax_queue),
                        daemon=True
                    )
                    minimax_process.start()
                if calculating and not minimax_queue.empty():
                    all_info = minimax_queue.get(timeout=0.01)
                    move, additional_info, moves_from_list = all_info
                    if nerd_view:
                        info_window.update_moves(moves_from_list)
                        info_window.update_additional_info(additional_info)
                        info_window.update_best_move(move)
                    y1, x1, y2, x2 = move
                    if tryMove(turn, main_board, y1, x1, y2, x2):
                        # Handle successful move
                        move_time = time.time() - start_time
                        if turn == 'w':
                            white_time -= move_time
                        else:
                            black_time -= move_time
                        turn = 'w' if turn == 'b' else 'b'
                        
                        # Handle promotion and game state
                        whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, y1, x1, y2, x2)
                        if whatAfter == "promotion":
                            promotion(yForPromotion, xForPromotion, main_board, '4')  # Always queen
                            whatAfter, _, _ = afterMove(turn, main_board, y1, x1, y2, x2)
                        
                        # Update game state
                        if whatAfter == "checkmate":
                            result = global_translations.get("checkmate")  # "Szach Mat!"
                            winner = global_translations.get("white") if turn == 'b' else global_translations.get("black")
                            running = False
                        elif whatAfter == "stalemate":
                            result = global_translations.get("stalemate")  # "Pat"
                            winner = global_translations.get("draw")  # "Remis"
                            running = False
                        elif whatAfter == "check":
                            in_check = turn
                        else:
                            in_check = None
                        #liczenie liczby ruchów, ważne pod nerd_view
                        if nerd_view:
                            moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                            moves_queue.put(move_time)
                        start_time = time.time()
                        calculating = False
                        minimax_process.terminate()  # Natychmiastowe zabicie procesu

            elif algorithm == "monte_carlo":
                if not calculating:
                    calculating = True
                    result_queue = queue.Queue()
                    monte_carlo_thread = MonteCarloThread(main_board, depth, turn, result_queue)
                    monte_carlo_thread.start()
                
                try:
                    move = result_queue.get_nowait()
                    calculating = False
                    if move:
                        from_row, from_col, to_row, to_col = move
                        if tryMove(turn, main_board, from_row, from_col, to_row, to_col):
                            move_time = time.time() - start_time
                            if turn == 'w':
                                white_time -= move_time
                            else:
                                black_time -= move_time
                            turn = 'w' if turn == 'b' else 'b'
                            whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, from_row, from_col, to_row, to_col)
                            if whatAfter == "promotion":
                                promotion_choice = '10'  # Zawsze promuj do królowej
                                promotion(yForPromotion, xForPromotion, main_board, promotion_choice)
                                whatAfter, _, _ = afterMove(turn, main_board, from_row, from_col, to_row, to_col)
                            if whatAfter == "checkmate":
                                result = global_translations.get("checkmate")  # "Szach Mat!"
                                winner = global_translations.get("white") if turn == 'b' else global_translations.get("black")
                                running = False
                            elif whatAfter == "stalemate":
                                result = global_translations.get("stalemate")  # "Pat"
                                winner = global_translations.get("draw")  # "Remis"
                                running = False
                            elif whatAfter == "check":
                                in_check = turn
                            else:
                                in_check = None
                            #liczenie liczby ruchów, ważne pod nerd_view
                            if nerd_view:
                                moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                moves_queue.put(move_time)
                            start_time = time.time()
                except queue.Empty:
                    pass  # Kontynuuj bez blokowania
                        


        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if turn == 'w':
            current_white_time = max(0, white_time - (current_time - start_time))  # Odliczanie od ustawionego czasu
            current_black_time = black_time  # Zachowaj czas czarnego
        else:
            current_black_time = max(0, black_time - (current_time - start_time))  # Odliczanie od ustawionego czasu
            current_white_time = white_time  # Zachowaj czas białego

        # Sprawdzenie, czy czas się skończył
        if current_white_time <= 0 or current_black_time <= 0:
            running = False
            result = global_translations.get("time_out")  # "Czas się skończył!"
            winner = global_translations.get("black") if current_white_time <= 0 else global_translations.get("white")
            running = False
        # Przed renderowaniem
        current_time = time.time()
        player_times_font = update_times_display(
            current_white_time, current_black_time, turn, player_turn,
            font, SQUARE_SIZE, YELLOW, GRAY, height
        )

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
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text)
        
        if calculating:
            calculating_text = font.render(global_translations.get("calculating"), True, WHITE)
            screen.blit(calculating_text, (8 * SQUARE_SIZE + 10, height - 200))
            dots = "." * ((int(time.time() * 2) % 4))
            calculating_dots = font.render(dots, True, WHITE)
            screen.blit(calculating_dots, (8 * SQUARE_SIZE + 150, height - 200))

        pygame.display.flip()
        clock.tick(60)

        if nerd_view: #rysowanie nerd_view
            current_time_for_stats = time.time()
            evaluation = get_evaluation(main_board)
            evaluation = evaluation[0] - evaluation[1]
            nerd_view_queue.put((current_time_for_stats, evaluation, moves_number))
            root.update()
    
    try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
    except: pass
    # W obsłudze wyjścia
    if monte_carlo_thread and monte_carlo_thread.is_alive():
        monte_carlo_thread.stop()
        monte_carlo_thread.join(timeout=0.1)

    save_in_short_algebraic(main_board, winner, result)
    save_in_long_algebraic(main_board, winner, result)
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)

    try: root.destroy()
    except: pass
    return

if __name__ == "__main__":

    main()
