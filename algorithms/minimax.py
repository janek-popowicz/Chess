import sys, copy, os, time, random
import algorithms.evaluation as evaluation 
import engine.board_and_fields as board_and_fields 
import engine.engine as engine 
from pathlib import Path
from engine.fen_operations import *
import json
from random import randint

class Minimax:
    def __init__(self, main_board, depth, color, time_limit=50):
        self.main_board = copy.deepcopy(main_board)
        self.depth = depth
        self.alpha = -100000
        self.beta = 100000
        self.color = color
        self.time_limit = time_limit
        self.start_time = None
        self.best_move = None
        self.message = " "
        self.available_moves_from_json = []

    def get_opening_move(self):
        """
        Checks opening book JSON for current position and returns a random move if found
        Returns: (tuple) move in format (y1, x1, y2, x2) or None if not found
        """
        try:
            json_path = Path(__file__).parent / "opening.json"
            print(f"\n=== Opening Book Search ===")
            
            if not json_path.exists():
                print("❌ Opening book not found")
                return None

            with open(json_path, 'r', encoding='utf-8') as f:
                opening_book = json.load(f)
                print(f"📚 Loaded opening book with {len(opening_book)} positions")

            current_fen = board_to_fen_inverted(self.main_board, self.color)
            fen_parts = current_fen.split(' ')
            position_key = f"{fen_parts[0]} {fen_parts[1]}"
            
            print(f"🔍 Searching for position: {position_key}")
            
            if position_key in opening_book:
                moves = opening_book[position_key]
                if not moves:
                    print("❌ No moves found in opening book")
                    return None
                
                self.available_moves_from_json = moves
                move_notation = random.choice(moves)
                print(f"✅ Found {len(moves)} moves in opening book")
                print(f"📌 Selected move: {move_notation}")
                
                return engine.notation_to_cords(
                    self.main_board, 
                    move_notation, 
                    self.color
                )

            print("❌ Position not found in opening book")
            return None

        except Exception as e:
            print(f"❌ Opening book error: {str(e)}")
            return None

    def get_best_move(self):
        """Main move search function"""
        self.start_time = time.time()
        print("\n=== Move Search Started ===")
        
        # Try opening book first
        print("\n📖 Checking opening book...")
        book_move = self.get_opening_move()
        if book_move:
            print(f"✨ Using book move: {book_move}")
            return book_move, self.message, self.available_moves_from_json

        print("\n🔄 Starting minimax search...")
        moves_by_depth = {}
        best_move = None
        best_eval = -float('inf')

        piece_types = {
            'p': 'Pawn', 'r': 'Rook', 'n': 'Knight',
            'b': 'Bishop', 'q': 'Queen', 'k': 'King'
        }

        try:
            for current_depth in range(1, self.depth + 1):
                if self.is_time_exceeded():
                    print(f"⚠️ Time limit reached at depth {current_depth-1}")
                    break
                    
                depth_start = time.time()
                eval_score, move = self.minimax(self.main_board, current_depth, -float('inf'), float('inf'), True)
                
                if move and not self.is_time_exceeded():
                    moves_by_depth[current_depth] = (move, eval_score)
                    y1, x1, y2, x2 = move
                    piece = self.main_board.board_state[y1][x1].figure
                    piece_name = piece_types.get(piece.type, piece.type)
                    print(f"\n📊 Depth {current_depth}:")
                    print(f"   Piece: {piece_name}")
                    print(f"   Move: {chr(97+x1)}{8-y1} → {chr(97+x2)}{8-y2}")
                    print(f"   Score: {eval_score:.2f}")
                    print(f"   Time: {time.time() - depth_start:.3f}s")
                    
                    if eval_score > best_eval:
                        best_move = move
                        best_eval = eval_score
                        print(f"   ⭐ New best move!")

            total_time = time.time() - self.start_time
            print(f"\n=== Search Complete ===")
            print(f"🕒 Total time: {total_time:.3f}s")
            print(f"📈 Max depth reached: {len(moves_by_depth)}")
            print(f"💫 Final best move: {best_move}")
            print(f"📋 Final score: {best_eval:.2f}")
            
            return best_move, self.message, self.available_moves_from_json

        except Exception as e:
            print(f"❌ Error in search: {e}")
            return None

    def get_mate_pattern_bonus(self, board, color, move):
        """
        Oblicza bonus za potencjalne wzorce matowe na podstawie ruchu.

        Argumenty:
            board (Board): Obecny stan planszy.
            color (str): Kolor gracza wykonującego ruch ('w' lub 'b').
            move (tuple): Ruch w formacie (y1, x1, y2, x2).

        Zwraca:
            int: Bonus punktowy za wzorce matowe.
        """
        y1, x1, y2, x2 = move
        piece = board.board_state[y1][x1].figure
        if not piece:
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
        if piece.type in ['r', 'q']:
            if ky in [0, 7] and abs(y2 - ky) == 0:
                if all(board.board_state[ky][x].figure and 
                       board.board_state[ky][x].figure.color == opponent_color 
                       for x in range(min(kx+1, 7), 8)):
                    bonus += 500

        # Pattern 2: Corner trap
        if kx in [0, 7] and ky in [0, 7]:
            if piece.type in ['q', 'r']:
                dist_to_king = abs(y2 - ky) + abs(x2 - kx)
                if dist_to_king <= 2:
                    bonus += 300

        # Pattern 3: Queen + Knight mate pattern
        if piece.type == 'q':
            knights = []
            for y in range(8):
                for x in range(8):
                    fig = board.board_state[y][x].figure
                    if fig and fig.type == 'n' and fig.color == color:
                        knights.append((y, x))
            if knights:
                dist_to_king = abs(y2 - ky) + abs(x2 - kx)
                if dist_to_king <= 2:
                    bonus += 400

        # Pattern 4: Single Rook mate pattern
        if piece.type == 'r':
            # Check if king is restricted to edge
            if ky in [0, 7] or kx in [0, 7]:
                # Check if rook is cutting off king's escape
                if (y2 == ky and abs(x2 - kx) > 1) or (x2 == kx and abs(y2 - ky) > 1):
                    # Verify king has limited escape squares
                    escape_squares = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            new_y, new_x = ky + dy, kx + dx
                            if 0 <= new_y < 8 and 0 <= new_x < 8:
                                target = board.board_state[new_y][new_x].figure
                                if not target or (target.color != opponent_color):
                                    escape_squares += 1
                    if escape_squares <= 3:
                        bonus += 600

        # Pattern 5: Bishop + Knight mate pattern
        if piece.type in ['b', 'n']:
            bishops = []
            knights = []
            # Find all bishops and knights of same color
            for y in range(8):
                for x in range(8):
                    fig = board.board_state[y][x].figure
                    if fig and fig.color == color:
                        if fig.type == 'b':
                            bishops.append((y, x))
                        elif fig.type == 'n':
                            knights.append((y, x))
            
            # If we have both bishop and knight
            if bishops and knights:
                # Check if king is near corner
                corner_distance = min(
                    abs(ky - 0) + abs(kx - 0),
                    abs(ky - 0) + abs(kx - 7),
                    abs(ky - 7) + abs(kx - 0),
                    abs(ky - 7) + abs(kx - 7)
                )
                if corner_distance <= 2:
                    # Check if pieces are in good positions
                    for by, bx in bishops:
                        for ny, nx in knights:
                            bishop_dist = abs(by - ky) + abs(bx - kx)
                            knight_dist = abs(ny - ky) + abs(nx - kx)
                            if bishop_dist <= 3 and knight_dist <= 2:
                                bonus += 700
                                
        return bonus

    def get_evaluation_score(self, board, is_maximizing):
        """
        Oblicza ocenę pozycji na planszy, uwzględniając wzorce matowe i inne czynniki.

        Argumenty:
            board (Board): Obecny stan planszy.
            is_maximizing (bool): Czy obecny gracz maksymalizuje wynik.

        Zwraca:
            int: Wynik oceny pozycji.
        """
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
        """
        Sprawdza, czy limit czasu na obliczenia został przekroczony.

        Zwraca:
            bool: True, jeśli czas został przekroczony, w przeciwnym razie False.
        """
        if not self.start_time:
            return False
        return time.time() - self.start_time >= self.time_limit - 0.1  # 100ms buffer

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Implementacja algorytmu minimax z przycinaniem alfa-beta.

        Argumenty:
            board (Board): Obecny stan planszy.
            depth (int): Głębokość rekursji.
            alpha (float): Wartość alfa dla przycinania.
            beta (float): Wartość beta dla przycinania.
            is_maximizing (bool): Czy obecny gracz maksymalizuje wynik.

        Zwraca:
            tuple: Najlepszy wynik i ruch w formacie (wynik, ruch).
        """
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