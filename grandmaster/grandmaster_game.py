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
from algorithms.evaluation import *
from multiprocessing import Process
from multiprocessing import Queue as multiQueue
from algorithms.minimax import *
from nerd_view import *


def calculate_minimax(board,color,result_queue):
    minimax_start_time = time.time()
    board_copy = copy.deepcopy(board)
    minimax_obj = Minimax(board_copy, 2, color, 6)
    best_move, additional_info, moves_list = minimax_obj.get_best_move()
    full_info = best_move, additional_info, moves_list
    if time.time() - minimax_start_time < 2:
        time.sleep(2 - (time.time() - minimax_start_time))
    result_queue.put(full_info)


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
    position_fen = f"{fen_parts[0]} {fen_parts[1]}"
    if position_fen in grandmaster_moves:
        moves_list = grandmaster_moves[position_fen]
        return moves_list[randint(1,len(moves_list))-1], moves_list  # Bierzemy losowy ruch
    return (0,0,0,0), []

def update_times_display(white_time, black_time, current_time, start_time, turn, player_color, font, SQUARE_SIZE, YELLOW, GRAY, height):
    """
    Returns tuple of time displays with player's time at bottom and grandmaster's time at top.
    
    Args:
        white_time (float): White player's total time
        black_time (float): Black player's total time
        current_time (float): Current timestamp
        start_time (float): Turn start timestamp
        turn (str): Current turn ('w' or 'b')
        player_color (str): Human player's color ('w' or 'b')
        font (pygame.font.Font): Font for rendering text
        SQUARE_SIZE (int): Size of a chess square
        YELLOW (pygame.Color): Color for active player
        GRAY (pygame.Color): Color for inactive player
        height (int): Screen height for positioning
    """
    # Calculate current times
    if turn == 'w':
        current_white_time = white_time + (current_time - start_time)
        current_black_time = black_time
    else:
        current_black_time = black_time + (current_time - start_time)
        current_white_time = white_time
    
    # Determine display positions based on player color
    if player_color == 'w':
        return (
            # Grandmaster's time (black) at top
            (font.render(format_time(current_black_time), True, YELLOW if turn == 'b' else GRAY),
             (8 * SQUARE_SIZE + 10, 80)),
            # Player's time (white) at bottom
            (font.render(format_time(current_white_time), True, YELLOW if turn == 'w' else GRAY),
             (8 * SQUARE_SIZE + 10, height - 150))
        )
    else:
        return (
            # Grandmaster's time (white) at top
            (font.render(format_time(current_white_time), True, YELLOW if turn == 'w' else GRAY),
             (8 * SQUARE_SIZE + 10, 80)),
            # Player's time (black) at bottom
            (font.render(format_time(current_black_time), True, YELLOW if turn == 'b' else GRAY),
             (8 * SQUARE_SIZE + 10, height - 150))
        )

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

    # Minimax awaryjny
    minimax_process = None
    minimax_queue = multiQueue()
    calculating = False

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

    nerd_view = config["nerd_view"]
    print(nerd_view)
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
            algorithm_name = grandmaster_name,
            search_depth=2,
            additional_info="...",
            best_move=(None) 
        )


    if player_color == 'w':
        is_reversed = False
    else:
        is_reversed = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try: root.destroy()
                except: pass
                try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
                except: pass
                running = False
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
                            if nerd_view:
                                moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                moves_queue.put(move_time)
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                # Obsługa przycisku "Wyjście"
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    running = False
                    try: minimax_process.terminate()
                    except: pass
                    try: root.destroy()
                    except: pass
                    return
                # Obsługa przycisku "Cofnij ruch"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and height - 100 <= pos[1] < height - 80:
                    # Reset thread variables
                    calculating = False
                    try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
                    except: pass
                    while not minimax_queue.empty():
                        minimax_queue.get_nowait()
                    if confirm_undo_dialog(screen, SQUARE_SIZE):
                        if undoMove(main_board):  # Cofnięcie ruchu
                            turn = 'w' if turn == 'b' else 'b'  # Zmiana tury
                            start_time = time.time()  # Reset czasu tury
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    try: minimax_process.terminate()  # Natychmiastowe zabicie procesu
                    except: pass
        if turn != player_color:
            move_time = time.time() - start_time
            
            if turn == 'w':
                white_time += move_time
            else:
                black_time += move_time
            draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck)
            draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
            pygame.display.flip()
            grandmaster_move, moves_from_json_list = get_grandmaster_move(main_board, grandmaster_color, grandmaster_moves)
            try: 
                cords = notation_to_cords(main_board, grandmaster_move, turn)
                time.sleep(1)
                y1, x1, y2, x2 = cords
            except:
                cords = False
            if cords and tryMove(turn, main_board, y1, x1, y2, x2):
                if nerd_view:
                    info_window.update_algorithm(grandmaster_name)
                    info_window.update_moves(moves_from_json_list)
                    info_window.update_additional_info(" ")
                    info_window.update_best_move(cords)
                try: minimax_process.terminate()
                except: pass
                calculating = False
                #sprawdzanie co po ruchu
                move_time = time.time() - start_time
                if turn == 'w':
                    white_time += time.time() - start_time
                else:
                    black_time += time.time() - start_time
                turn = 'w' if turn == 'b' else 'b'
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
                #liczenie liczby ruchów, ważne pod nerd_view
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
                        args=(main_board,turn,minimax_queue),
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
                        # Handle successful move
                        move_time = time.time() - start_time
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
                        #liczenie liczby ruchów, ważne pod nerd_view
                        if nerd_view:
                            moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                            moves_queue.put(move_time)
                        start_time = time.time()
                        calculating = False
                        minimax_process.terminate()  # Natychmiastowe zabicie procesu   

        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if turn == 'w':
            current_white_time = max(0, 10 * 60 - (current_time - start_time + white_time))  # Odliczanie od 10 minut
            current_black_time = max(0, 10 * 60 - black_time)  # Zachowaj czas czarnego
        else:
            current_black_time = max(0, 10 * 60 - (current_time - start_time + black_time))  # Odliczanie od 10 minut
            current_white_time = max(0, 10 * 60 - white_time)  # Zachowaj czas białego

        # Sprawdzenie, czy czas się skończył
        if current_white_time <= 0 or current_black_time <= 0:
            running = False
            result = "Czas się skończył!"
            winner = "Czarny" if current_white_time <= 0 else "Biały"
            break

        player_times_font = update_times_display(
            white_time, black_time, current_time, start_time, turn, player_color,
            font, SQUARE_SIZE, YELLOW, GRAY, height
        )
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check)
        evaluation = get_evaluation(main_board, turn)[0] - get_evaluation(main_board, turn)[1]  # Calculate evaluation
        draw_interface(screen, turn, SQUARE_SIZE,BLACK, texts, player_times_font, in_check, check_text, evaluation)
        try:
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == turn:
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES, is_reversed)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
        pygame.display.flip()
        clock.tick(60)
        if nerd_view: #rysowanie nerd_view
            current_time_for_stats = time.time()
            evaluation = get_evaluation(main_board)
            evaluation = evaluation[0] - evaluation[1]
            nerd_view_queue.put((current_time_for_stats, evaluation, moves_number))
            root.update()
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    return
if __name__ == "__main__":

    main('w', 'Nakamura')  # Przykładowe wywołanie
