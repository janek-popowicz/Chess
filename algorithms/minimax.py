#importacja bibliotek zewnętrznych 

import sys, copy, os, time, random  # Dodano moduł time do zarządzania czasem

#importacja plików wewnętrznych 

import algorithms.evaluation as evaluation 
import engine.board_and_fields as board_and_fields 
import engine.engine as engine 


class Minimax:
    """
    Klasa implementująca algorytm Minimax z przycinaniem alfa-beta oraz ograniczeniem czasowym.
    """
    def __init__(self, main_board, depth, color, time_limit=0.01):
        """
        Inicjalizuje obiekt Minimax.

        :param main_board: Główna plansza gry.
        :param depth: Maksymalna głębokość przeszukiwania.
        :param color: Kolor gracza AI ('w' dla białych, 'b' dla czarnych).
        :param time_limit: Limit czasu na wykonanie ruchu (w sekundach).
        """
        self.main_board = main_board
        self.depth = depth 
        self.alpha = -100000
        self.beta = 100000
        self.color = color  # Kolor AI
        self.time_limit = time_limit  # Limit czasu w sekundach
        self.start_time = None  # Czas rozpoczęcia przeszukiwania
        
        self.best_move = None  # Najlepszy ruch znaleziony do tej pory
    
    def get_evaluation_score(self, board, is_maximizing):
        """
        Oblicza ocenę planszy na podstawie funkcji oceny.

        :param board: Aktualna plansza gry.
        :param is_maximizing: Czy obecnie maksymalizujemy wynik.
        :return: Ocena planszy.
        """
        eval_result = evaluation.get_evaluation(board, self.color)  # Wynik oceny [białe, czarne]
        color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        
        # Sprawdzenie sytuacji matowej lub patowej
        if board_and_fields.Board.get_all_moves(board, color) == {} and board.is_in_check(color):
            if color == 'w':
                return [-1000000, 1000000]  # Mat dla białych
            else:
                return [1000000, -1000000]  # Mat dla czarnych
        elif board_and_fields.Board.get_all_moves(board, color) == {} and not board.is_in_check(color):
            return [0, 0]  # Pat

        # Zwrócenie różnicy ocen w zależności od koloru AI
        if self.color == 'b':
            return eval_result[1] - eval_result[0]
        else:
            return eval_result[0] - eval_result[1]
    
    def is_time_exceeded(self):
        """
        Sprawdza, czy przekroczono limit czasu.

        :return: True, jeśli czas został przekroczony, False w przeciwnym razie.
        """
        return time.time() - self.start_time >= self.time_limit
        
    def minimax(self, board, depth, alfa, beta, is_maximizing):
        """
        Implementacja algorytmu Minimax z przycinaniem alfa-beta.

        :param board: Aktualna plansza gry.
        :param depth: Pozostała głębokość przeszukiwania.
        :param alfa: Wartość alfa dla przycinania.
        :param beta: Wartość beta dla przycinania.
        :param is_maximizing: Czy obecnie maksymalizujemy wynik.
        :return: Najlepsza ocena i ruch.
        """
        current_color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        legal_moves = board.get_all_moves(current_color)

        # Sprawdzenie limitu czasu
        if self.is_time_exceeded():
            try:
                if best_move is not None:
                    return 0, best_move  # Zwróć najlepszy ruch znaleziony do tej pory
                else:
                    # Wybierz losowy ruch, jeśli nie znaleziono żadnego
                    legal_moves_main = self.main_board.get_all_moves(self.color)
                    moves = legal_moves_main
                    if moves == {}:
                        return 0, None
                    key = random.sample(sorted(moves), 1)
                    move = random.sample(moves[key[0]], 1) 
                    final_move = (*key[0], move[0][0], move[0][1])
                    return 0, final_move
            except UnboundLocalError:
                # Obsługa sytuacji, gdy best_move nie jest zdefiniowany
                legal_moves_main = self.main_board.get_all_moves(self.color)
                moves = legal_moves_main
                if moves == {}:
                    return 0, None
                key = random.sample(sorted(moves), 1)
                move = random.sample(moves[key[0]], 1) 
                final_move = (*key[0], move[0][0], move[0][1])
                return 0, final_move

        # Warunek zakończenia przeszukiwania
        if depth == 0 or legal_moves == {}:
            score = self.get_evaluation_score(board, is_maximizing)
            return score, None

        if is_maximizing:
            max_eval = -float('inf')
            best_move = None 

            for figure in legal_moves:
                for move in legal_moves[figure]:
                    if self.is_time_exceeded():  # Sprawdzenie limitu czasu w każdej iteracji
                        return max_eval, best_move

                    new_board = copy.deepcopy(board)

                    (y1, x1) = figure 
                    (y2, x2) = move 

                    new_board.make_move(y1, x1, y2, x2)

                    eval_value, _ = self.minimax(new_board, depth - 1, alfa, beta, False)

                    if eval_value > max_eval:
                        max_eval = eval_value
                        best_move = (y1, x1, y2, x2)

                        alfa = max(alfa, eval_value)

                        if beta <= alfa:
                            break
                if beta <= alfa:
                    break
                    
            return max_eval, best_move

        else:
            min_eval = float('inf')
            best_move = None

            for figure in legal_moves:
                for move in legal_moves[figure]:
                    if self.is_time_exceeded():  # Sprawdzenie limitu czasu w każdej iteracji
                        return min_eval, best_move

                    new_board = copy.deepcopy(board)

                    (y1, x1) = figure 
                    (y2, x2) = move 

                    new_board.make_move(y1, x1, y2, x2)

                    eval_value, _ = self.minimax(new_board, depth - 1, alfa, beta, True)

                    if eval_value < min_eval:
                        min_eval = eval_value
                        best_move = (y1, x1, y2, x2)

                        beta = min(beta, eval_value)

                        if beta <= alfa:
                            break
                if beta <= alfa:
                    break
            return min_eval, best_move

    def get_best_move(self):
        """
        Wywołuje funkcję minimax dla aktualnej planszy i zwraca najlepszy ruch.

        :return: Najlepszy ruch znaleziony przez algorytm.
        """
        self.start_time = time.time()  # Zapisz czas rozpoczęcia
        score, move = self.minimax(self.main_board, self.depth, self.alpha, self.beta, True)
        return move



