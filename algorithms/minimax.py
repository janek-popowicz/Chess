import sys 
import copy 
import os 

import algorithms.evaluation as evaluation
import engine.board_and_fields as board_and_fields
import engine.engine as engine



class Minimax:
    def __init__(self):
        self.depth = 3 # głębokość przeszukiwania drzewa gry
        self.board = board_and_fields.Board() #dobrze na pewno
        #self.evaluation = evaluation.Evaluation(self.board)   
        self.alpha = -1000000  # minus nieskończoność
        self.beta = 1000000    # plus nieskończoność
        self.color = 'b'        # kolor naszej AI ("white" lub "black")
        self.all_moves = self.board.get_all_moves(self.board, self.color) 
        self.best_move = None 

    
    def minimax(self, board, depth, alfa, beta, is_maximizing):
        # Określamy aktualny kolor (AI vs przeciwnik)
        if is_maximizing:
            current_color = self.color
        else:
            current_color = 'w' if self.color == 'b' else 'b'
        
        legal_moves = self.board.get_all_moves(board, current_color)
        
        if depth == 0 or self.all_moves == []:
            score = evaluation.Evaluation(board)
            return score, None
            #return evaluation.Evaluation(board), None
        

        if is_maximizing:
            max_eval = -float('inf')
            best_move = None
            for figure in legal_moves:
                for move in legal_moves[figure]:
                    new_board = copy.deepcopy(board)
                    #tu jest funckcja że on gra ten ruch na nowej planszy
                    (a,b) = figure
                    (c,d) = move
                    new_board = self.board.make_move_new_board(a,b,c,d) #masz Ignacy naprawiłem ci wykonywanie ruchu ~ Benedykt 
                    eval_value, _ = self.minimax(new_board, depth - 1, alfa, beta, False)
                    max_eval = max(max_eval, eval_value)
                    alfa = max(alfa, eval_value)
                    if beta <= alfa:
                        break
                    if eval_value == max_eval:
                        best_move = move
                return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for figure in legal_moves:
                for move in legal_moves[figure]:
                    new_board = copy.deepcopy(board)
                    (a,b) = figure
                    (c,d) = move
                    new_board = self.board.make_move_new_board(a,b,c,d) #masz Ignacy naprawiłem ci wykonywanie ruchu ~ Benedykt
                #tu jest funckcja że on gra ten ruch na nowej planszy

                eval_value, _ = self.minimax(new_board, depth - 1, alfa, beta, True)
                min_eval = min(min_eval, eval_value)
                beta = min(beta, eval_value)
                if beta <= alfa:
                    break
                if eval_value == min_eval:
                    best_move = move
            return min_eval, best_move

    def get_best_move(self):
        """Wywołanie funkcji minimax na aktualnej planszy, zwraca najlepszy ruch w formacie [skąd_y, skąd_x, dokąd_y, dokąd_x]."""
        _, move = self.minimax(self.board,self.depth,self.alpha,self.beta, True)
        return move

'''def main():
    minimax = Minimax()
    move = minimax.get_best_move()
    print(move)'''
