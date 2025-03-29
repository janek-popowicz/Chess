#importacja bibliotek zewnętrznych 

import sys, copy, os, time, random  # Dodano moduł time do zarządzania czasem

#importacja plików wewnętrznych 

import algorithms.evaluation as evaluation 
import engine.board_and_fields as board_and_fields 
import engine.engine as engine 
from pathlib import Path
from engine.fen_operations import *
from random import randint
import json
#json_path = Path(f"algorithms/opening.json")

class Minimax:
    """
    Klasa implementująca algorytm Minimax z przycinaniem alfa-beta oraz ograniczeniem czasowym.
    """
    def __init__(self, main_board, depth, color, time_limit):
        """
        Inicjalizuje obiekt Minimax.

        :param main_board: Główna plansza gry.
        :param depth: Maksymalna głębokość przeszukiwania.
        :param color: Kolor gracza AI ('w' dla białych, 'b' dla czarnych).
        :param time_limit: Limit czasu na wykonanie ruchu (w sekundach).
        """
        self.main_board = copy.deepcopy(main_board)  # Make a deep copy to avoid race conditions
        self.depth = depth 
        self.alpha = -100000
        self.beta = 100000
        self.color = color  # Kolor AI
        self.time_limit = time_limit  # Limit czasu w sekundach
        self.start_time = None  # Czas rozpoczęcia przeszukiwania
        
        self.best_move = None  # Najlepszy ruch znaleziony do tej pory
        self.path = Path(f"algorithms/opening.json")
    
    def get_evaluation_score(self, board, is_maximizing):
        """
        Oblicza ocenę planszy na podstawie funkcji oceny.

        :param board: Aktualna plansza gry.
        :param is_maximizing: Czy obecnie maksymalizujemy wynik.
        :return: Ocena planszy.
        """
        eval_result = evaluation.get_evaluation(board)  # Wynik oceny [białe, czarne]
        color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        
        # Sprawdzenie sytuacji matowej lub patowej
        if board_and_fields.Board.get_all_moves(board, color) == {} and board.is_in_check(color):
            if color == 'w':
                return 1000000  # Mat dla białych
            else:
                return -1000000  # Mat dla czarnych
        elif board_and_fields.Board.get_all_moves(board, color) == {} and not board.is_in_check(color):
            return 0  # Pat

        # Zwrócenie różnicy ocen w zależności od koloru AI
        if color == 'b':
            return eval_result[1] - eval_result[0]
        else:
            return eval_result[0] - eval_result[1]
    
    def is_time_exceeded(self):
        """
        Sprawdza, czy przekroczono limit czasu.

        :return: True, jeśli czas został przekroczony, False w przeciwnym razie.
        """
        return (self.start_time is not None and 
                time.time() - self.start_time >= self.time_limit)
    def undo_move(self, board, y1, x1, y2, x2):
        """
        Przywraca ruch na planszy.

        :param board: Plansza gry.
        :param y1: Wiersz początkowy figury. param x1: Kolumna początkowa figury.
        :param y2: Wiersz docelowy figury. param x2: Kolumna docelowa figury.
        """
        # Przywrócenie figury na pierwotne miejsce
        board[y1][x1].figure = board[y2][x2].figure
        board[y2][x2].figure = None

    
            
    def minimax(self, board, depth, alfa, beta, is_maximizing):
        """
        Implementacja algorytmu Minimax z przycinaniem alfa-beta z dokładną kontrolą czasu.

        :param board: Aktualna plansza gry.
        :param depth: Pozostała głębokość przeszukiwania.
        :param alfa: Wartość alfa dla przycinania.
        :param beta: Wartość beta dla przycinania.
        :param is_maximizing: Czy obecnie maksymalizujemy wynik.
        :return: Najlepsza ocena i ruch.
        """
        # Natychmiastowe sprawdzenie limitu czasu
        if self.is_time_exceeded():
            return None, None

        current_color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        legal_moves = board.get_all_moves(current_color)

        # Base case
        if depth == 0 or legal_moves == {}:
            score = self.get_evaluation_score(board, is_maximizing)
            return score, None

        best_move = None
        if is_maximizing:
            max_eval = -float('inf')
            for figure in legal_moves:
                for move in legal_moves[figure]:
                    if self.is_time_exceeded():
                        return max_eval, best_move

                    y1, x1 = figure
                    y2, x2 = move

                    # Zachowaj stan przed ruchem
                    captured_piece = board.board_state[y2][x2].figure
                    prev_cords = board.piece_cords.copy()

                    # Wykonaj ruch
                    board.make_move(y1, x1, y2, x2)
                    board.piece_cords.remove((y1, x1))
                    if (y2, x2) not in board.piece_cords:
                        board.piece_cords.append((y2, x2))

                    # Szybka ocena pozycji
                    current_eval = self.get_evaluation_score(board, is_maximizing)
                    
                    # Przycięcie gałęzi jeśli pozycja jest znacząco gorsza
                    if current_eval < max_eval - 200:  # Wartość progowa
                        # Cofnij ruch
                        board.make_move(y2, x2, y1, x1)
                        board.board_state[y2][x2].figure = captured_piece
                        board.piece_cords = prev_cords
                        continue

                    # Rekurencyjne wywołanie
                    eval_value, _ = self.minimax(board, depth - 1, alfa, beta, False)

                    # Cofnij ruch
                    board.make_move(y2, x2, y1, x1)
                    board.board_state[y2][x2].figure = captured_piece
                    board.piece_cords = prev_cords
                    print("eval_value: ", eval_value)
                    print("max_eval: ", max_eval)
                    if eval_value is not None:
                        if eval_value > max_eval:
                            max_eval = eval_value
                            best_move = (y1, x1, y2, x2)
                            if depth == self.depth:
                                self.best_move = best_move
                        alfa = max(alfa, eval_value)

                    if beta <= alfa:
                        break
                if beta <= alfa:
                    break
            return max_eval, best_move

        else:
            min_eval = float('inf')
            for figure in legal_moves:
                for move in legal_moves[figure]:
                    if self.is_time_exceeded():
                        return min_eval, best_move

                    y1, x1 = figure
                    y2, x2 = move

                    # Zachowaj stan przed ruchem
                    captured_piece = board.board_state[y2][x2].figure
                    prev_cords = board.piece_cords.copy()

                    # Wykonaj ruch
                    board.make_move(y1, x1, y2, x2)
                    board.piece_cords.remove((y1, x1))
                    if (y2, x2) not in board.piece_cords:
                        board.piece_cords.append((y2, x2))

                    # Szybka ocena pozycji
                    current_eval = self.get_evaluation_score(board, is_maximizing)
                    
                    # Przycięcie gałęzi jeśli pozycja jest znacząco lepsza
                    if current_eval > min_eval + 200:  # Wartość progowa
                        # Cofnij ruch
                        board.make_move(y2, x2, y1, x1)
                        board.board_state[y2][x2].figure = captured_piece
                        board.piece_cords = prev_cords
                        continue

                    # Rekurencyjne wywołanie
                    eval_value, _ = self.minimax(board, depth - 1, alfa, beta, True)

                    # Cofnij ruch
                    board.make_move(y2, x2, y1, x1)
                    board.board_state[y2][x2].figure = captured_piece
                    board.piece_cords = prev_cords

                    if eval_value is not None:
                        if eval_value < min_eval:
                            min_eval = eval_value
                            best_move = (y1, x1, y2, x2)
                        beta = min(beta, eval_value)

                    if beta <= alfa:
                        break
                if beta <= alfa:
                    break
            return min_eval, best_move

    def get_random_move(self):
        """Helper method to get a random move when interrupted"""
        legal_moves = self.main_board.get_all_moves(self.color)
        if not legal_moves:
            return None
        figure = random.choice(list(legal_moves.keys()))
        move = random.choice(legal_moves[figure])
        return (*figure, *move)

    def check_opening_book(self, board=None, turn=None):
        """Check opening book for current position"""
        if board is None:
            board = self.main_board
        if turn is None:
            turn = self.color
            
        try:
            with open(self.path, "r") as f:
                opening_list = json.load(f)
        except FileNotFoundError:
            return None

        current_fen = board_to_fen_inverted(board, turn)
        fen_parts = current_fen.split(' ')
        position_fen = f"{fen_parts[0]} {fen_parts[1]}"
        
        if position_fen in opening_list:
            moves_list = opening_list[position_fen]
            return moves_list[randint(0, len(moves_list)-1)]
        return None

    def load_opening_moves():
        """Wczytuje ruchy arcymistrza z pliku JSON."""
        json_path = Path(f"algorithms/opening.json")
        try:
            with open(json_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Nie znaleziono pliku z ruchami arcymistrza: {json_path}")
            return {}

    def get_best_move(self):
        """
        Wywołuje funkcję minimax dla aktualnej planszy i zwraca najlepszy ruch.

        :return: Najlepszy ruch znaleziony przez algorytm.
        """
        self.start_time = time.time()  # Zapisz czas rozpoczęcia
        self.best_move = None  # Reset best move
        
        # Try opening book first
        opening_move = self.check_opening_book()
        if opening_move is not None:
            return engine.notation_to_cords(self.main_board, opening_move, self.color)

        # Run minimax search
        score, move = self.minimax(self.main_board, self.depth, self.alpha, self.beta, True)
        
        # If no move found or interrupted, try random move
        if move is None:
            move = self.get_random_move()
            
        return move



