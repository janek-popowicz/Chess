import sys
import copy
import os
import algorithms.evaluation as evaluation
import engine.board_and_fields as board_and_fields
import engine.engine as engine

class Minimax:
    def __init__(self):
        self.depth = 3  # głębokość przeszukiwania drzewa gry
        self.board = board_and_fields.Board()  # inicjalizacja planszy
        self.alpha = -1000000  # minus nieskończoność
        self.beta = 1000000    # plus nieskończoność
        self.color = 'b'       # kolor naszej AI ("w" dla white lub "b" dla black)
        # Pobieramy wszystkie ruchy dla aktualnej planszy i koloru (opcjonalnie – można odłożyć do get_best_move)
        self.all_moves = self.board.get_all_moves(self.board, self.color)
        self.best_move = None

    def get_evaluation_score(self, board):
        """
        Używa funkcji get_evaluation z modułu evaluation.
        Zwraca dodatnią wartość, jeśli AI (np. czarne) jest w korzystniejszej sytuacji,
        ujemną, jeśli przeciwnik (białe) ma przewagę.
        """
        eval_result = evaluation.get_evaluation(board)  # eval_result = [ocena_białych, ocena_czarnych]
        if self.color == 'b':
            return eval_result[1] - eval_result[0]
        else:
            return eval_result[0] - eval_result[1]

    def minimax(self, board, depth, alfa, beta, is_maximizing):
        # Ustalamy kolor aktualnego gracza w zależności od tego, czy maksymalizujemy, czy minimalizujemy
        current_color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        
        # Pobieramy wszystkie legalne ruchy dla danego koloru na przekazanej planszy
        legal_moves = board.get_all_moves(board, current_color)
        
        # Warunek zakończenia rekurencji: osiągnięto maksymalną głębokość lub brak ruchów
        if depth == 0 or not legal_moves:
            score = self.get_evaluation_score(board)
            return score, None
        
        if is_maximizing:
            max_eval = -float('inf')
            best_move = None
            for figure in legal_moves:
                for move in legal_moves[figure]:
                    new_board = copy.deepcopy(board)
                    (a, b) = figure
                    (c, d) = move
                    
                    # Wykonujemy ruch na kopii planszy
                    new_board_state = new_board.make_move_new_board(a, b, c, d)
                    temp_board = board_and_fields.Board()
                    temp_board.board_state = new_board_state
                    
                    # Wywołanie minimax dla przeciwnika (ruch minimalizujący)
                    eval_value, _ = self.minimax(temp_board, depth - 1, alfa, beta, False)
                    
                    if eval_value > max_eval:
                        max_eval = eval_value
                        best_move = (a, b, c, d)  # Format: skąd_y, skąd_x, dokąd_y, dokąd_x
                    
                    alfa = max(alfa, eval_value)
                    if beta <= alfa:
                        break  # przycinanie alfa-beta
            return max_eval, best_move
        else:  # Ruch minimalizujący
            min_eval = float('inf')
            best_move = None
            for figure in legal_moves:
                for move in legal_moves[figure]:
                    new_board = copy.deepcopy(board)
                    (a, b) = figure
                    (c, d) = move
                    
                    # Wykonujemy ruch na kopii planszy
                    new_board_state = new_board.make_move_new_board(a, b, c, d)
                    temp_board = board_and_fields.Board()
                    temp_board.board_state = new_board_state
                    
                    # Wywołanie minimax dla AI (ruch maksymalizujący)
                    eval_value, _ = self.minimax(temp_board, depth - 1, alfa, beta, True)
                    
                    if eval_value < min_eval:
                        min_eval = eval_value
                        best_move = (a, b, c, d)
                    
                    beta = min(beta, eval_value)
                    if beta <= alfa:
                        break  # przycinanie alfa-beta
            return min_eval, best_move

    def get_best_move(self):
        """Wywołuje funkcję minimax dla aktualnej planszy i zwraca najlepszy ruch."""
        score, move = self.minimax(self.board, self.depth, self.alpha, self.beta, True)
        return move

def main():
    """Tworzy instancję minimax i zwraca najlepszy ruch."""
    minimax_instance = Minimax()
    best_move = minimax_instance.get_best_move()
    print(f"Najlepszy ruch: {best_move}")
    return best_move

if __name__ == "__main__":
    main()
