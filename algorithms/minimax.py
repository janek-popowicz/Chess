#importacja bibliotek zewnętrznych 

import sys, copy , os

#importacja plików wewnętrznych 

import algorithms.evaluation as evaluation 
import engine.board_and_fields as board_and_fields 
import engine.engine as engine 


class Minimax:
    def __init__(self, main_board, depth, color):
        self.main_board = main_board
        self.depth = depth 
        self.alpha = -100000
        self.beta = 100000
        self.color = color #kolor AI
        
        self.best_move = None
    
    def get_evaluation_score(self,board,is_maximizing):
        eval_result = evaluation.get_evaluation(board, self.color) # eval_result = [ocena_białych, ocena_czarnych]
        color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        if board_and_fields.Board.get_all_moves(board, color) == {} and board.is_in_check(color):
            if color == 'w':
                return [-1000000, 1000000]
            else:
                return [1000000, -1000000]
        elif board_and_fields.Board.get_all_moves(board, color) == {} and board.is_in_check(color) == False:
            if color == 'w' and  eval_result[0] > eval_result[1]:
                return [0, 0]
            else:
                return [0, 0]

        if self.color == 'b':
            return (eval_result[1] - eval_result[0])
        else:
            return eval_result[0] - eval_result[1]
        
    def minimax(self, board, depth, alfa, beta, is_maximizing):

        '''if depth == self.depth:
            board = self.main_board'''
        current_color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')

        legal_moves = board.get_all_moves(current_color)

        if depth == 0 or legal_moves == {}:
            score = self.get_evaluation_score(board,is_maximizing)
            return score, None


        if is_maximizing:
            max_eval = -float('inf')
            best_move = None 

            for figure in legal_moves:
                for move in legal_moves[figure]:

                    new_board = copy.deepcopy(board)

                    (y1, x1) = figure 
                    (y2, x2) = move 

                    new_board.make_move(y1,x1,y2,x2)

                    eval_value, _ = self.minimax(new_board, depth -1, alfa, beta , False)

                    if eval_value > max_eval:
                        max_eval = eval_value
                        best_move = (y1, x1,y2, x2)

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

                    new_board = copy.deepcopy(board)

                    (y1, x1) = figure 
                    (y2, x2) = move 

                    new_board.make_move(y1,x1,y2,x2)

                    eval_value, _ = self.minimax(new_board, depth -1, alfa, beta , True)

                    if eval_value < min_eval:
                        min_eval = eval_value
                        best_move = (y1, x1,y2, x2)

                        beta = min(beta, eval_value)

                        if beta <= alfa:
                            break
                if beta <= alfa:
                    break
            return min_eval, best_move
    def get_best_move(self):
        """Wywołuje funkcję minimax dla aktualnej planszy i zwraca najlepszy ruch."""
        score, move = self.minimax(self.main_board, self.depth, self.alpha, self.beta, True)
        return move



