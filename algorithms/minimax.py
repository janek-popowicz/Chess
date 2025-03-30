import sys, copy, os, time, random
import algorithms.evaluation as evaluation 
import engine.board_and_fields as board_and_fields 
import engine.engine as engine 
from pathlib import Path
from engine.fen_operations import *
import json
from random import randint

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
        self.path = Path(__file__).parent / "opening.json"
        self.opening_book = self.load_opening_book()

    def load_opening_book(self):
        """Load opening book with proper color handling"""
        try:
            if not self.path.exists():
                # Create default opening book with color information
                default_book = {
                    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w": ["d4", "e4", "c4", "Nf3"],
                    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b": ["Nf6", "d5", "f5"],
                    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w": ["c4", "Bg5"],
                    "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b": ["e6", "c5", "g6"]
                }
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump(default_book, f, indent=2)
                return default_book

            with open(self.path, 'r', encoding='utf-8') as f:
                opening_book = json.load(f)
                print(f"Loaded opening book with {len(opening_book)} positions")
                return opening_book

        except Exception as e:
            print(f"Error loading opening book: {e}")
            return {}

    def get_mate_pattern_bonus(self, board, color, move):
        """Evaluate potential checkmate patterns"""
        y1, x1, y2, x2 = move
        piece = board.board_state[y1][x1].figure
        if not piece:  # Add early return if no piece
            return 0
            
        opponent_color = 'b' if color == 'w' else 'w'
        opponent_king_pos = None
        bonus = 0
        
        # Find opponent's king
        for y in range(8):
            for x in range(8):
                fig = board.board_state[y][x].figure
                if fig and fig.type == 'k' and fig.color == opponent_color:
                    opponent_king_pos = (y, x)
                    break
        if not opponent_king_pos:
            return 0
            
        ky, kx = opponent_king_pos
        
        # Pattern 1: Back rank mate potential
        if piece.type in ['r', 'q']:  # Changed to lowercase
            if ky in [0, 7] and abs(y2 - ky) == 0:
                if all(board.board_state[ky][x].figure and 
                       board.board_state[ky][x].figure.color == opponent_color 
                       for x in range(min(kx+1, 7), 8)):
                    bonus += 500

        # Pattern 2: Corner trap
        if kx in [0, 7] and ky in [0, 7]:
            if piece.type in ['q', 'r']:  # Changed to lowercase
                dist_to_king = abs(y2 - ky) + abs(x2 - kx)
                if dist_to_king <= 2:
                    bonus += 300

        # Pattern 3: Queen + Knight mate pattern
        if piece.type == 'q':  # Changed to lowercase
            knights = []
            for y in range(8):
                for x in range(8):
                    fig = board.board_state[y][x].figure
                    if fig and fig.type == 'n' and fig.color == color:  # Changed to lowercase
                        knights.append((y, x))
            if knights:
                dist_to_king = abs(y2 - ky) + abs(x2 - kx)
                if dist_to_king <= 2:
                    bonus += 400

        return bonus

    def get_evaluation_score(self, board, is_maximizing):
        eval_result = evaluation.get_evaluation(board)
        color = self.color if is_maximizing else ('w' if self.color == 'b' else 'b')
        
        # Check for mate and stalemate
        if not board.get_all_moves(color):
            if board.is_in_check_minimax(color):
                return -1000000 if is_maximizing else 1000000
            return 0  # Stalemate
            
        score = eval_result[0] - eval_result[1] if color == 'w' else eval_result[1] - eval_result[0]
        
        # Add checkmate pattern detection for the last move
        if hasattr(board, 'last_move') and board.last_move:
            mate_bonus = self.get_mate_pattern_bonus(board, color, board.last_move)
            score += mate_bonus if is_maximizing else -mate_bonus
        
        return score

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

                    # Store last move for pattern detection
                    new_board.last_move = (y1, x1, y2, x2)
                    
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

                    # Store last move for pattern detection
                    new_board.last_move = (y1, x1, y2, x2)
                    
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
        """Check opening book for current position with color"""
        try:
            if not self.opening_book:
                return None

            # Get FEN with color
            current_fen = board_to_fen_inverted(self.main_board, self.color)
            fen_parts = current_fen.split(' ')
            position_key = f"{fen_parts[0]} {fen_parts[1]}"  # Board + active color
            
            print(f"Looking for position: {position_key}")
            
            if position_key in self.opening_book:
                moves = self.opening_book[position_key]
                print(f"Found {len(moves)} possible moves: {moves}")
                # Use 0-based indexing for randint
                move_notation = moves[randint(0, len(moves)-1)]
                print(f"Selected move: {move_notation}")
                return engine.notation_to_cords(self.main_board, move_notation, self.color)

            return None

        except Exception as e:
            print(f"Error checking opening book: {e}")
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