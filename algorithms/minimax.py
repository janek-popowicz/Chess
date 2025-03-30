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
        self.depth = depth = 3
        self.alpha = -100000
        self.beta = 100000
        self.color = color
        self.time_limit = time_limit
        self.start_time = None
        self.best_move = None
        self.path = Path(__file__).parent / "opening.json"
        self.opening_book = self.load_opening_book()

    def load_opening_book(self):
        """
        Ładuje książkę debiutów z pliku JSON. Jeśli plik nie istnieje, tworzy domyślną książkę debiutów.
        
        Zwraca:
            dict: Słownik zawierający pozycje i możliwe ruchy.
        """
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

    def check_opening_book(self):
        """
        Sprawdza książkę debiutów dla obecnej pozycji i koloru gracza.

        Zwraca:
            tuple lub None: Ruch w formacie (y1, x1, y2, x2) lub None, jeśli brak ruchu w książce.
        """
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

    def check_move_safety(self, board, move, color):
        """
        Placeholder dla oceny bezpieczeństwa ruchu.

        Argumenty:
            board (Board): Obecny stan planszy.
            move (tuple): Ruch w formacie (y1, x1, y2, x2).
            color (str): Kolor gracza wykonującego ruch ('w' lub 'b').

        Zwraca:
            int: Wartość bezpieczeństwa ruchu (domyślnie 0).
        """
        return 0

    def get_best_move(self):
        """
        Znajduje najlepszy ruch dla obecnej pozycji, używając algorytmu minimax i książki debiutów.

        Zwraca:
            tuple lub None: Najlepszy ruch w formacie (y1, x1, y2, x2) lub None, jeśli brak ruchu.
        """
        self.start_time = time.time()
        
        # Try opening book first
        book_move = self.check_opening_book()
        if book_move:
            print(f"Using book move: {book_move}")
            return book_move

        # Initialize move tracking
        moves_by_depth = {}
        best_move = None
        best_eval = -float('inf')
        
        piece_types = {
            'p': 'Pawn', 'r': 'Rook', 'n': 'Knight',
            'b': 'Bishop', 'q': 'Queen', 'k': 'King'
        }

        try:
            # Iterative deepening
            for current_depth in range(1, self.depth + 1):
                if self.is_time_exceeded():
                    break
                    
                depth_start = time.time()
                eval_score, move = self.minimax(self.main_board, current_depth, -float('inf'), float('inf'), True)
                
                if move and not self.is_time_exceeded():
                    moves_by_depth[current_depth] = (move, eval_score)
                    
                    # Print current depth move
                    y1, x1, y2, x2 = move
                    piece = self.main_board.board_state[y1][x1].figure
                    piece_name = piece_types.get(piece.type, piece.type)
                    print(f"Depth {current_depth}: {piece_name} from {chr(97+x1)}{8-y1} to {chr(97+x2)}{8-y2} (score: {eval_score:.2f}, time: {time.time() - depth_start:.3f}s)")
                    
                    # Update best move with depth preference
                    if best_move is None:
                        best_move = move
                        best_eval = eval_score
                    else:
                        # Prefer deeper searches unless they're significantly worse
                        prev_eval = moves_by_depth[current_depth-1][1]
                        if eval_score >= prev_eval - 200:  # Allow some tolerance
                            best_move = move
                            best_eval = eval_score
                        elif eval_score < prev_eval - 500:  # If much worse, keep previous
                            print(f"Depth {current_depth} significantly worse, keeping previous move")

            # Compare and print all moves
            print("\nMoves comparison:")
            selected_depth = None
            for depth, (move, score) in moves_by_depth.items():
                y1, x1, y2, x2 = move
                piece = self.main_board.board_state[y1][x1].figure
                piece_name = piece_types.get(piece.type, piece.type)
                mark = "★" if move == best_move else " "
                print(f"{mark} Depth {depth}: {piece_name} {chr(97+x1)}{8-y1}-{chr(97+x2)}{8-y2} (score: {score:.2f})")
                if move == best_move:
                    selected_depth = depth

            if selected_depth:
                print(f"\nSelected move from depth {selected_depth}")

            print(f"Search completed in {time.time() - self.start_time:.3f}s")
            return best_move

        except Exception as e:
            print(f"Error in get_best_move: {e}")
            return None