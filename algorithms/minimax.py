import sys, copy, os, time, random
import algorithms.evaluation as evaluation 
import engine.board_and_fields as board_and_fields 
import engine.engine as engine 
from pathlib import Path
from engine.fen_operations import *
import json

class Minimax:
    def __init__(self, main_board, depth, color, time_limit=10):
        self.main_board = copy.deepcopy(main_board)
        self.depth = depth = 2
        self.alpha = -100000
        self.beta = 100000
        self.color = color
        self.time_limit = time_limit
        self.start_time = None
        self.best_move = None
        self.path = Path("algorithms/opening.json")

    def get_evaluation_score(self, board, is_maximizing):
        eval_result = evaluation.get_evaluation(board)
        color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        
        # Check for mate and stalemate
        if not board.get_all_moves(color):
            if board.is_in_check(color):
                return -1000000 if is_maximizing else 1000000
            return 0  # Stalemate
            
        return eval_result[0] - eval_result[1] if color == 'w' else eval_result[1] - eval_result[0]

    def is_time_exceeded(self):
        if not self.start_time:
            return False
        return time.time() - self.start_time >= self.time_limit - 0.1  # 100ms buffer

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        # Immediate time check
        if self.is_time_exceeded():
            return None, None

        current_color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        legal_moves = board.get_all_moves(current_color)

        # Base cases
        if depth == 0 or not legal_moves:
            return self.get_evaluation_score(board, is_maximizing), None

        best_move = None
        if is_maximizing:
            max_eval = -float('inf')
            for (y1, x1), moves in legal_moves.items():
                for y2, x2 in moves:
                    if self.is_time_exceeded():
                        return max_eval, best_move

                    # Save board state
                    new_board = copy.deepcopy(board)
                    
                    # Make move
                    if not engine.tryMove(current_color, new_board, y1, x1, y2, x2):
                        continue

                    eval_value, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                    if eval_value is None:
                        continue

                    if eval_value > max_eval:
                        max_eval = eval_value
                        best_move = (y1, x1, y2, x2)
                    alpha = max(alpha, eval_value)
                    if beta <= alpha:
                        break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for (y1, x1), moves in legal_moves.items():
                for y2, x2 in moves:
                    if self.is_time_exceeded():
                        return min_eval, best_move

                    new_board = copy.deepcopy(board)
                    if not engine.tryMove(current_color, new_board, y1, x1, y2, x2):
                        continue

                    eval_value, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                    if eval_value is None:
                        continue

                    if eval_value < min_eval:
                        min_eval = eval_value
                        best_move = (y1, x1, y2, x2)
                    beta = min(beta, eval_value)
                    if beta <= alpha:
                        break
            return min_eval, best_move

    def check_opening_book(self):
        try:
            with open(self.path, "r") as f:
                opening_book = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        current_fen = board_to_fen_inverted(self.main_board, self.color)
        position_key = current_fen.split(' ')[0]
        
        if position_key in opening_book:
            moves = opening_book[position_key]
            move_notation = random.choice(moves)
            return engine.notation_to_cords(self.main_board, move_notation, self.color)
        return None

    def get_best_move(self):
        self.start_time = time.time()
        
        # Try opening book first
        book_move = self.check_opening_book()
        if book_move:
            print(f"Using book move (time: {time.time() - self.start_time:.3f}s)")
            return book_move

        # Iterative deepening
        best_move = None
        for current_depth in range(1, self.depth + 1):
            if self.is_time_exceeded():
                break
                
            depth_start = time.time()
            _, move = self.minimax(self.main_board, current_depth, -float('inf'), float('inf'), True)
            
            if move and not self.is_time_exceeded():
                best_move = move
                print(f"Depth {current_depth} completed in {time.time() - depth_start:.3f}s")
            else:
                break

        # Use random move if no move found
        if not best_move:
            legal_moves = self.main_board.get_all_moves(self.color)
            if legal_moves:
                figure = random.choice(list(legal_moves.keys()))
                move_coords = random.choice(legal_moves[figure])
                best_move = (*figure, *move_coords)
                print("Using random move (emergency)")

        print(f"Search finished in {time.time() - self.start_time:.3f}s")
        return best_move