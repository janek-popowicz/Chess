import pygame
import time
import json
from pathlib import Path
import copy
from random import randint
from multiprocessing import Process, Queue as multiQueue

# Wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from engine.fen_operations import *
from interface.graphics import *
from algorithms.evaluation import *
from algorithms.minimax import *
from interface.nerd_view import *

def calculate_minimax(board: Board, color: str, result_queue: multiQueue) -> None:
    """
    Oblicza najlepszy ruch dla podanej planszy przy użyciu algorytmu minimax.

    Wykonuje kopię planszy, inicjuje obiekt minimax z głębokością wyszukiwania równą 6,
    a następnie zwraca najlepszy ruch, dodatkowe informacje oraz listę ruchów. Aby zagwarantować
    minimalny czas obliczeń (2 sekundy), funkcja w razie potrzeby uśpiewa wątek przed umieszczeniem
    wyniku w kolejce.

    :param board: Aktualny stan planszy (obiekt typu Board).
    :param color: Kolor gracza wykonującego ruch ('w' dla białych, 'b' dla czarnych).
    :param result_queue: Kolejka multiprocessing.Queue, do której zostanie wrzucony wynik obliczeń.
    :return: None
    """
    minimax_start_time = time.time()
    board_copy = copy.deepcopy(board)
    minimax_obj = Minimax(board_copy, 2, color, 6)
    best_move, additional_info, moves_list = minimax_obj.get_best_move()
    full_info = best_move, additional_info, moves_list
    if time.time() - minimax_start_time < 2:
        time.sleep(2 - (time.time() - minimax_start_time))
    result_queue.put(full_info)


def load_grandmaster_moves(grandmaster_name: str) -> dict:
    """
    Wczytuje ruchy arcymistrza z pliku JSON.

    Plik powinien znajdować się w katalogu "grandmaster/json/" i być nazwany zgodnie z
    podaną nazwą arcymistrza. W przypadku braku pliku zwracany jest pusty słownik.

    :param grandmaster_name: Nazwa arcymistrza (np. "Nakamura").
    :return: Słownik zawierający ruchy arcymistrza.
    """
    json_path = Path(f"grandmaster/json/{grandmaster_name}.json")
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Nie znaleziono pliku z ruchami arcymistrza: {json_path}")
        return {}


def get_grandmaster_move(board: Board, turn: str, grandmaster_moves: dict) -> tuple:
    """
    Wybiera ruch arcymistrza na podstawie aktualnej pozycji.

    Funkcja konwertuje bieżący stan planszy do notacji FEN (odwróconej) i wyszukuje odpowiadający
    klucz w słowniku ruchów arcymistrza. Jeśli pozycja zostanie znaleziona, wybiera losowy ruch z
    dostępnej listy ruchów.

    :param board: Aktualny stan planszy (obiekt typu Board).
    :param turn: Aktualna tura ('w' lub 'b').
    :param grandmaster_moves: Słownik ruchów arcymistrza wczytany z pliku JSON.
    :return: Krotka zawierająca wybrany ruch (jako krotkę czterech wartości) oraz listę ruchów.
             Jeśli ruch nie został znaleziony, zwraca ((0, 0, 0, 0), []).
    """
    current_fen = board_to_fen_inverted(board, turn)
    fen_parts = current_fen.split(' ')
    position_fen = f"{fen_parts[0]} {fen_parts[1]}"
    if position_fen in grandmaster_moves:
        moves_list = grandmaster_moves[position_fen]
        return moves_list[randint(1, len(moves_list)) - 1], moves_list  # Bierzemy losowy ruch
    return (0, 0, 0, 0), []


def update_times_display(
    white_time: float,
    black_time: float,
    turn: str,
    player_color: str,
    font: pygame.font.Font,
    SQUARE_SIZE: int,
    YELLOW,
    GRAY,
    height: int
) -> tuple:
    """
    Generuje obiekty renderujące czasy graczy do wyświetlenia na interfejsie gry.

    Pozycje wyświetlania są ustalane zależnie od koloru gracza.
    Dla gracza koloru 'w' czasy są przypisywane odpowiednio (czarny u góry, biały u dołu) i vice versa.

    :param white_time: Pozostały czas dla białych (w sekundach).
    :param black_time: Pozostały czas dla czarnych (w sekundach).
    :param turn: Aktualna tura ('w' lub 'b').
    :param player_color: Kolor gracza ('w' lub 'b').
    :param font: Obiekt czcionki pygame do renderowania tekstu.
    :param SQUARE_SIZE: Rozmiar pojedynczego pola szachownicy.
    :param YELLOW: Kolor żółty (do podświetlenia aktywnego gracza).
    :param GRAY: Kolor szary (dla nieaktywnego gracza).
    :param height: Wysokość okna gry.
    :return: Krotka zawierająca dwie krotki, z których każda zawiera obiekt Surface z wyrenderowanym tekstem
             oraz krotkę określającą pozycję wyświetlania.
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


def main(player_color: str, grandmaster_name: str, game_time: float) -> None:
    """
    Główna funkcja uruchamiająca grę szachową.

    Inicjuje środowisko Pygame, ładuje konfigurację, obrazy figur, ustawia interfejs użytkownika,
    inicjalizuje planszę oraz zarządza główną pętlą gry. Obsługuje zdarzenia, ruchy gracza, ruchy arcymistrza
    oraz logikę rozgrywki (m.in. promocję, szach, mat, pat, cofanie ruchów oraz odmierzanie czasu).

    :param player_color: Kolor gracza ('w' dla białych, 'b' dla czarnych).
    :param grandmaster_name: Nazwa arcymistrza, z którego ruchy będą wykorzystywane (np. "Nakamura").
    :param game_time: Początkowy czas gry dla obu graczy (w sekundach).
    :return: None
    """
    pygame.init()
    # Ładowanie konfiguracji
    config = load_config()
    resolution = config["resolution"]
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
        pieces[piece] = pygame.transform.scale(
            pygame.image.load("pieces/" + icon_type + "/" + piece + ".png"), (SQUARE_SIZE-10, SQUARE_SIZE-10)
        )
    
    running = True
    main_board = Board()
    grandmaster_color = 'w' if player_color == 'b' else 'b'
    grandmaster_moves = load_grandmaster_moves(grandmaster_name)
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    # Minimax awaryjny
    minimax_process = None
    minimax_queue = multiQueue()
    calculating = False

    # Teksty interfejsu
    texts = (
        (font.render(f"{global_translations.get('turn')}: {global_translations.get('white')}", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"{global_translations.get('turn')}: {global_translations.get('black')}", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(global_translations.get("exit_to_menu"), True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(global_translations.get("confirm_undo_text"), True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),  # Dodano przycisk "Cofnij ruch"
    )
    check_text = font.render(global_translations.get("check"), True, pygame.Color("red"))

    nerd_view = config["nerd_view"]
    if nerd_view:
        from queue import Queue
        nerd_view_queue = Queue()
        moves_queue = Queue()
        import tkinter as tk
        root = tk.Tk()
        root.geometry("600x400+800+100")  # Pozycja obok okna gry
        stats_window = NormalStatsWindow(root, nerd_view_queue, moves_queue)
        moves_number = sum(len(value) for value in main_board.get_all_moves(turn))

        algo_root = tk.Toplevel()
        moves = []
        info_window = AlgorithmInfoWindow(
            algo_root,
            moves_list=moves,
            algorithm_name=grandmaster_name,
            search_depth=2,
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

    if player_color == 'w':
        is_reversed = False
    else:
        is_reversed = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    root.destroy()
                except Exception:
                    pass
                try:
                    minimax_process.terminate()  # Natychmiastowe zabicie procesu
                except Exception:
                    pass
                running = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Modyfikacja wykrywania kliknięć w zależności od orientacji planszy
                if is_reversed:
                    col = pos[0] // SQUARE_SIZE
                    row = pos[1] // SQUARE_SIZE
                else:
                    col = 7 - (pos[0] // SQUARE_SIZE)
                    row = 7 - (pos[1] // SQUARE_SIZE)
                
                if col < 8 and row < 8:
                    if selected_piece:
                        if turn == player_color and tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                            move_time = time.time() - start_time
                            if turn == 'w':
                                white_time -= move_time
                            else:
                                black_time -= move_time
                            turn = 'w' if turn == 'b' else 'b'
                            
                            # Sprawdzanie co po ruchu
                            if selected_piece is not None:
                                whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
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
                            selected_piece = None
                            if nerd_view:
                                moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                moves_queue.put(move_time)
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                # Obsługa przycisku "Wyjście"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and pos[1] >= height - 80:
                    running = False
                    try:
                        minimax_process.terminate()
                    except Exception:
                        pass
                    try:
                        root.destroy()
                    except Exception:
                        pass
                    return
                # Obsługa przycisku "Cofnij ruch"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and height - 100 <= pos[1] < height - 80:
                    # Reset zmiennych wątku
                    calculating = False
                    try:
                        minimax_process.terminate()  # Natychmiastowe zabicie procesu
                    except Exception:
                        pass
                    while not minimax_queue.empty():
                        minimax_queue.get_nowait()
                    if confirm_undo_dialog(screen, SQUARE_SIZE):
                        if undoMove(main_board):  # Cofnięcie ruchu
                            turn = 'w' if turn == 'b' else 'b'  # Zmiana tury
                            start_time = time.time()  # Reset czasu tury
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    try:
                        minimax_process.terminate()  # Natychmiastowe zabicie procesu
                    except Exception:
                        pass
        if turn != player_color:
            draw_board(screen, SQUARE_SIZE, main_board, main_board.incheck, is_reversed)
            draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
            pygame.display.flip()
            grandmaster_move, moves_from_json_list = get_grandmaster_move(main_board, grandmaster_color, grandmaster_moves)
            try: 
                cords = notation_to_cords(main_board, grandmaster_move, turn)
                y1, x1, y2, x2 = cords
            except Exception:
                cords = False
            if cords and tryMove(turn, main_board, y1, x1, y2, x2):
                if nerd_view:
                    info_window.update_algorithm(grandmaster_name)
                    info_window.update_moves(moves_from_json_list)
                    info_window.update_additional_info(" ")
                    info_window.update_best_move(cords)
                try:
                    minimax_process.terminate()
                except Exception:
                    pass
                calculating = False
                # Sprawdzanie co po ruchu
                move_time = time.time() - start_time
                if turn == 'w':
                    white_time -= time.time() - start_time
                else:
                    black_time -= time.time() - start_time
                turn = 'w' if turn == 'b' else 'b'
                whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, y1, x1, y2, x2)
                if whatAfter == "promotion":
                    choiceOfPromotion = "4"
                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, x1, y1, x2, y2)
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
                # Liczenie liczby ruchów, ważne pod nerd_view
                if nerd_view:
                    moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                    moves_queue.put(move_time)
                selected_piece = None
                start_time = time.time()
            else:
                if nerd_view:
                    info_window.update_algorithm("minimax")
                if not calculating:
                    calculating = True
                    minimax_process = Process(
                        target=calculate_minimax,
                        args=(main_board, turn, minimax_queue),
                        daemon=True
                    )
                    minimax_process.start()
                if calculating and not minimax_queue.empty():
                    all_info = minimax_queue.get(timeout=0.01)
                    move, additional_info, moves_from_json_list = all_info
                    if nerd_view:
                        info_window.update_moves(moves_from_json_list)
                        info_window.update_additional_info(additional_info)
                        info_window.update_best_move(move)
                    y1, x1, y2, x2 = move
                    if tryMove(turn, main_board, y1, x1, y2, x2):
                        # Obsługa poprawnego wykonania ruchu
                        move_time = time.time() - start_time
                        if turn == 'w':
                            white_time -= time.time() - start_time
                        else:
                            black_time -= time.time() - start_time
                        turn = 'w' if turn == 'b' else 'b'
                        
                        # Obsługa promocji i stanu gry
                        whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, y1, x1, y2, x2)
                        if whatAfter == "promotion":
                            promotion(yForPromotion, xForPromotion, main_board, '4')  # Zawsze na hetmana
                            whatAfter, _, _ = afterMove(turn, main_board, y1, x1, y2, x2)
                        
                        # Aktualizacja stanu gry
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
                        # Liczenie liczby ruchów, ważne pod nerd_view
                        if nerd_view:
                            moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                            moves_queue.put(move_time)
                        start_time = time.time()
                        calculating = False
                        try:
                            minimax_process.terminate()  # Natychmiastowe zabicie procesu
                        except Exception:
                            pass

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
            result = global_translations.get("time_out")
            winner = global_translations.get("black") if current_white_time <= 0 else global_translations.get("white")
            running = False

        player_times_font = update_times_display(
            current_white_time, current_black_time, turn, player_color,
            font, SQUARE_SIZE, YELLOW, GRAY, height
        )
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check, is_reversed)
        evaluation = get_evaluation(main_board, turn)[0] - get_evaluation(main_board, turn)[1]  # Calculate evaluation
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text)
        try:
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0], selected_piece[1])[0] == player_color:
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]], SQUARE_SIZE, main_board, HIGHLIGHT_MOVES, HIGHLIGHT_TAKES, is_reversed)
        except (TypeError, AttributeError):
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
        pygame.display.flip()
        clock.tick(60)
        if nerd_view:  # Rysowanie nerd_view
            current_time_for_stats = time.time()
            evaluation = get_evaluation(main_board)
            evaluation = evaluation[0] - evaluation[1]
            nerd_view_queue.put((current_time_for_stats, evaluation, moves_number))
            root.update()
    save_in_short_algebraic(main_board, winner, result)
    save_in_long_algebraic(main_board, winner, result)
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)

    return


if __name__ == "__main__":
    # Przykładowe wywołanie - NIE ZMIENIAJ NIC W KODZIE
    # Przykład funkcji z adnotacjami typów:
    # def funcja(x: str, y: int) -> bool:  # Zwraca True, jeśli operacja się powiodła
    main('w', 'Nakamura')
