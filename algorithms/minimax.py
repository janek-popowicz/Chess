import sys
import os
import copy 

'''
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *

import engine.engine as engine
import engine.board_and_fields as board_and_fields
import engine.figures as figures
import evaluation 
'''
import engine.board_and_fields as board_and_fields
from engine.engine import *
import engine.figures as figures
import algorithms.evaluation as evaluation

class Minimax:
    def __init__(self):
        self.depth = 3 # głębokość przeszukiwania drzewa gry
        self.board = board_and_fields.Board() #dobrze na pewno
        self.evaluation = evaluation.Evaluation(self.board)   
        self.alpha = -1000000  # minus nieskończoność
        self.beta = 1000000    # plus nieskończoność
        self.color = "black"        # kolor naszej AI ("white" lub "black")
        self.all_moves = self.board.get_legal_moves(self.board, self.color)
        self.best_move = None 

    def minimax(self, board, depth, alpha, beta, isMaximizing):
        # Określamy kolor ruchu w zależności od gałęzi
        current_color = self.color if isMaximizing else ("black" if self.color == "white" else "white")
        legal_moves = board_and_fields.get_legal_moves(board, current_color)
        
        # Warunek zakończenia: głębokość 0 lub brak ruchów (np. szach-mat/stalemate)
        if depth == 0 or not legal_moves:
            return self.evaluation.evaluate(board), None

        best_move = None

        if isMaximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                # Utwórz kopię planszy i symuluj ruch
                new_board = copy.deepcopy(board)
                board_and_fields.make_move(new_board, move, current_color)
                 
                if eval_value > max_eval:
                    max_eval = eval_value
                    best_move = move
                alpha = max(alpha, eval_value)
                if beta <= alpha:
                    break  # Pruning – dalsze ruchy nie zmienią wyniku
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                new_board = board.copy()
                board_and_fields.make_move(new_board, move, current_color)
                
                eval_value, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval_value < min_eval:
                    min_eval = eval_value
                    best_move = move
                beta = min(beta, eval_value)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_best_move(self):
        """Wywołanie funkcji minimax na aktualnej planszy, zwraca najlepszy ruch w formacie [skąd_y, skąd_x, dokąd_y, dokąd_x]."""
        cokolwiek, move = self.minimax(self.board, self.depth, self.alpha, self.beta, True)
        return move

def main():
    minimax = Minimax()
    move = minimax.get_best_move()
    print(move)
